# -*- coding:utf-8 -*-
import json
import random

from scrapy.http.request import Request

from .spiders.utils import Logger, parse_cookie, P22P3Encoder
from .spiders.exception_process import next_request_method_wrapper, enqueue_request_method_wrapper


class Scheduler(Logger):
    # 记录当前正在处理的item, 在处理异常时使用
    present_item = None

    def __init__(self, crawler):

        self.settings = crawler.settings
        self.set_logger(crawler)
        if self.settings.get("CUSTOM_REDIS"):
            from custom_redis.client import Redis
        else:
            from redis import Redis
        self.redis_conn = Redis(self.settings.get("REDIS_HOST"),
                                self.settings.get("REDIS_PORT"))
        self.queue_name = "%s:*:queue"
        self.queues = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open(self, spider):

        self.spider = spider
        self.queue_name = self.queue_name%spider.name
        spider.set_redis(self.redis_conn)
        spider.set_logger(self.logger)

    def request_to_dict(self, request):

        headers = dict([(item[0].decode("ascii"), item[0]) for item in request.headers.items()])
        req_dict = {
            'url': request.url,
            'method': request.method,
            'headers': headers,
            'body': request.body,
            'cookies': request.cookies,
            'meta': request.meta,
            '_encoding': request._encoding,
            'dont_filter': request.dont_filter,
            'callback': None if request.callback is None else request.callback.__name__,
            'errback': None if request.errback is None else request.errback.__name__,
        }
        return req_dict

    @enqueue_request_method_wrapper
    def enqueue_request(self, request):

        req_dict = self.request_to_dict(request)
        key = "{sid}:item:queue".format(sid=req_dict['meta']['spiderid'])
        self.redis_conn.zadd(key, json.dumps(req_dict, cls=P22P3Encoder), -int(req_dict["meta"]["priority"]))
        self.logger.debug("Crawlid: '{id}' Url: '{url}' added to queue"
                          .format(id=req_dict['meta']['crawlid'],
                                  url=req_dict['url']))

    @next_request_method_wrapper
    def next_request(self):

        queues = self.redis_conn.keys(self.queue_name)

        if queues:
            queue = random.choice(queues)
            self.logger.info("length of queue %s is %s" %
                             (queue, self.redis_conn.zcard(queue)))

            item = None
            if self.settings.get("CUSTOM_REDIS"):
                item = self.redis_conn.zpop(queue)
            else:
                pipe = self.redis_conn.pipeline()
                pipe.multi()
                pipe.zrange(queue, 0, 0).zremrangebyrank(queue, 0, 0)
                result, count = pipe.execute()
                # 1.1.8 add
                if result:
                    item = result[0]

            if item:
                item = json.loads(item)
                self.present_item = item
                headers = item.get("headers", {})
                body = item.get("body")
                if item.get("method"):
                    method = item.get("method")
                else:
                    method = "GET"

                try:
                    req = Request(item['url'], method=method, body=body, headers=headers)
                except ValueError:
                    req = Request('http://' + item['url'], method=method, body=body, headers=headers)

                if 'callback' in item:
                    cb = item['callback']
                    if cb and self.spider:
                        cb = getattr(self.spider, cb)
                        req.callback = cb

                if 'errback' in item:
                    eb = item['errback']
                    if eb and self.spider:
                        eb = getattr(self.spider, eb)
                        req.errback = eb

                if 'meta' in item:
                    item = item['meta']

                # defaults not in schema
                if 'curdepth' not in item:
                    item['curdepth'] = 0

                if "retry_times" not in item:
                    item['retry_times'] = 0

                for key in item.keys():
                    req.meta[key] = item[key]

                if 'useragent' in item and item['useragent'] is not None:
                    req.headers['User-Agent'] = item['useragent']

                if 'cookie' in item and item['cookie'] is not None:
                    if isinstance(item['cookie'], dict):
                        req.cookies = item['cookie']
                    elif isinstance(item['cookie'], (str, bytes)):
                        req.cookies = parse_cookie(item['cookie'])

                return req

    def close(self, reason):
        self.logger.info("Closing Spider", {'spiderid': self.spider.name})

    def has_pending_requests(self):
        return False