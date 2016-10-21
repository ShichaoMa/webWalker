# -*- coding:utf-8 -*-
import json
import random
import re

import tldextract
tldextract.tldextract.LOG.setLevel("INFO")

from scrapy.http.request import Request

from walker.spiders.utils import Logger


class Scheduler(Logger):

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
        self.extract = tldextract.extract

    @classmethod
    def from_crawler(cls, crawler):

        return cls(crawler)

    def open(self, spider):

        self.spider = spider
        self.queue_name = self.queue_name%spider.name
        spider.set_redis(self.redis_conn)
        spider.set_logger(self.logger)

    def request_to_dict(self, request):

        req_dict = {
            'url': request.url.decode('ascii'),
            'method': request.method,
            'headers': dict(request.headers),
            'body': request.body,
            'cookies': request.cookies,
            'meta': request.meta,
            '_encoding': request._encoding,
            'priority': request.priority,
            'dont_filter': request.dont_filter,
            'callback': None if request.callback is None else request.callback.func_name,
            'errback': None if request.errback is None else request.errback.func_name,
        }
        return req_dict

    def enqueue_request(self, request):

        req_dict = self.request_to_dict(request)
        ex_res = self.extract(req_dict['url'])
        key = "{sid}:{dom}.{suf}:queue".format(
            sid=req_dict['meta']['spiderid'],
            dom=ex_res.domain,
            suf=ex_res.suffix)
        self.redis_conn.zadd(key, json.dumps(req_dict), -int(req_dict["priority"]))
        self.logger.debug("Crawlid: '{id}' Url: '{url}' added to queue"
                          .format(id=req_dict['meta']['crawlid'],
                                  url=req_dict['url']))

    def next_request(self):

        queues = self.redis_conn.keys(self.queue_name)

        if queues:
            queue = random.choice(queues)
            self.logger.info("length of queue %s is %s" %
                             (queue, self.redis_conn.zcard(queue)))
            # 自定义redis可以使用此api
            #
            if self.settings.get("CUSTOM_REDIS"):
                item = self.redis_conn.zpop(queue)
            else:
                pipe = self.redis_conn.pipeline()
                pipe.multi()
                pipe.zrange(queue, 0, 0).zremrangebyrank(queue, 0, 0)
                result, count = pipe.execute()
                item = result[0]

            if item:
                item = json.loads(item)

                try:
                    req = Request(item['url'])
                except ValueError:
                    req = Request('http://' + item['url'])

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
                    elif isinstance(item['cookie'], basestring):
                        req.cookies = self.parse_cookie(item['cookie'])
                return req

    def parse_cookie(self, string):

        results = re.findall('([^=]+)=([^\;]+);?\s?', string)
        my_dict = {}

        for item in results:
            my_dict[item[0]] = item[1]

        return my_dict

    def close(self, reason):

        self.logger.info("Closing Spider", {'spiderid': self.spider.name})

    def has_pending_requests(self):

        return False