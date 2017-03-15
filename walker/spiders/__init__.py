# -*- coding:utf-8 -*-
import time
import copy
import socket

from urllib.parse import urlparse, urljoin

from scrapy import Field, Item, signals
from scrapy.exceptions import DontCloseSpider
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.response import response_status_message

from .exception_process import parse_method_wrapper, parse_next_method_wrapper
from .utils import get_ip_address, url_arg_increment, Logger, get_val,\
     url_item_arg_increment, url_path_arg_increment, LoggerDiscriptor, \
    send_request_wrapper


BASE_FIELD = ["success", "domain", "exception", "crawlid", "spiderid", "workerid", "response_url", "status_code", "status_msg", "url", "seed", "timestamp"]
ITEM_FIELD = {}
ITEM_XPATH = {}
PAGE_XPATH = {}


class ClusterSpider(Spider, Logger):

    name = "cluster_spider"
    proxy = None
    change_proxy = None
    logger = LoggerDiscriptor()
    have_duplicate = False

    def __init__(self, *args, **kwargs):

        Spider.__init__(self, *args, **kwargs)
        self.worker_id = ("%s_%s" % (socket.gethostname(), get_ip_address())).replace('.', '_')
        self.gen_field = self._yield_field()
        self.base_item_cls = type("RawResponseItem", (Item, ),
                                  dict(zip(BASE_FIELD, self.gen_field)))

    def _set_crawler(self, crawler):

        Spider._set_crawler(self, crawler)
        self.crawler.signals.connect(self.spider_idle,
                                     signal=signals.spider_idle)


    def spider_idle(self):

        print('Dont close spider........')
        raise DontCloseSpider

    def set_logger(self, crawler):

        Logger.set_logger(self, crawler)

    def set_redis(self, redis_conn):

        self.redis_conn = redis_conn

    def _yield_field(self):

        while True:
            yield Field()

    def get_item_cls(self):

        return type("%sItem"%self.name.capitalize(), (self.base_item_cls, ),
                    dict(zip([x[0] for x in ITEM_FIELD[self.name]], self.gen_field)))

    def reset_item(self, dict):

        item = self.get_item_cls()()

        for key in dict.keys():
            item[key] = dict[key]

        return item

    def common_property(self, response, item, spider_item_field=None):
        # 强化增发请求后获取字段的能力，增加请求可以使用该方法同时获取多个字段，同时还可以继续增发请求，理论上支持无限增发
        field = spider_item_field or copy.deepcopy(ITEM_FIELD[self.name])

        while field:
            k, v = field.pop(0)
            # 只有在spider_item_field存在且没有要求进一步增发请求时，才会判定会是增发请求后的操作
            # 也就是说，如果增发请求后有字段被要求再次增发，当前（未再次增发之前）的处理函数会调用function和extract，不会调用after后缀的函数
            # 对于完成过一次增发请求后不需要再次增发的字段，函数带不带after后缀并没有什么区别 add by msc 2016.11.25
            is_after = (True if spider_item_field is not None else False) and not v.get("request")
            val = get_val(v, response, item, is_after, self, k)
            request_func = v.get("request")

            if request_func:
                if not val:
                    request = send_request_wrapper(response, item, k, self.next_request_callback)(request_func)()

                    if request:
                        return request

            # 获取值的顺序为，增发请求后的值优先，其次是增发前的值，其次是默认值。 add by msc 2016.11.25
            item[k] = val or item.get(k) or v.get("default", "")
            # 对于有增发请求的需求的字段，不管要不要增发请求，都会停止获取需要增发请求的字段之后字段的值
            # 这么做的目的是为了防止没有对于不确定是否增发的字段，若未增发，后续字段会在第一个响应的页面中获取后续字段的值 add by msc 2016.11.26
            if request_func:
                break

    @parse_method_wrapper
    def parse(self, response):

        self.logger.debug("start response in parse")
        item_urls = [urljoin(response.url, x) for x in set(response.xpath("|".join(ITEM_XPATH[self.name])).extract())]
        self.crawler.stats.inc_total_pages(response.meta['crawlid'], len(item_urls))

        if "if_next_page" in response.meta:
            del response.meta["if_next_page"]
        else:
            response.meta["seed"] = response.url

        # 防止代理继承  add at 16.10.26
        response.meta.pop("proxy", None)
        response.meta["callback"] = "parse_item"
        response.meta["priority"] -= 20

        for item_url in item_urls:
            if self.have_duplicate:
                if self.duplicate_filter(response, item_url, self.have_duplicate):
                    continue
            response.meta["url"] = item_url
            yield Request(url=item_url,
                          callback=self.parse_item,
                          meta=response.meta,
                          errback=self.errback)

        xpath = "|".join(PAGE_XPATH[self.name])

        if xpath.count("?") == 1:
            next_page_urls = [url_arg_increment(xpath, response.url)] if len(item_urls) else []
        elif xpath.count("subpath="):
            next_page_urls = [url_path_arg_increment(xpath, response.url)] if len(item_urls) else []
        elif xpath.count("/") > 1:
            next_page_urls = [urljoin(response.url, x) for x in set(response.xpath(xpath).extract())]
        else:
            next_page_urls = [url_item_arg_increment(xpath, response.url, len(item_urls))] if len(item_urls) else []

        response.meta["if_next_page"] = True
        response.meta["callback"] = "parse"
        response.meta["priority"] += 20

        for next_page_url in next_page_urls:
            response.meta["url"] = next_page_url
            yield Request(url=next_page_url,
                          callback=self.parse,
                          meta=response.meta)

    @parse_method_wrapper
    def parse_item(self, response):

        self.logger.debug("start response in parse_item")
        item = self._enrich_base_data(response)
        request = self.common_property(response, item)
        return self.process_forward(request, response, item)

    def process_forward(self, request, response, item):

        if request:
            return request

        self.logger.info("crawlid:%s, product_id: %s, suceessfully yield item" % (
        item.get("crawlid"), item.get("product_id", "unknow")))
        self.crawler.stats.inc_crawled_pages(response.meta['crawlid'])
        return item

    def duplicate_filter(self, response, url, func):

        crawlid = response.meta["crawlid"]
        common_part = func(url)
        if self.redis_conn.sismember("crawlid:%s:model" % crawlid, common_part):
            #self.crawler.stats.inc_total_pages(response.meta['crawlid'], -1)
            return True
        else:
            self.redis_conn.sadd("crawlid:%s:model" % crawlid, common_part)
            self.redis_conn.expire("crawlid:%s:model" % crawlid, self.crawler.settings.get("DUPLICATE_TIMEOUT", 60*60))
            return False

    def _enrich_base_data(self, response):
        item = self.get_item_cls()()
        item['spiderid'] = response.meta['spiderid']
        item['workerid'] = self.worker_id
        item['url'] = response.meta["url"]
        item["seed"] = response.meta.get("seed", "")
        item["timestamp"] = time.strftime("%Y%m%d%H%M%S")
        item['status_code'] = response.status
        item["status_msg"] = response_status_message(response.status)
        item['domain'] = urlparse(response.url).hostname.split(".", 1)[1]
        item['crawlid'] = response.meta['crawlid']
        item['response_url'] = response.url
        return item

    def errback(self, failure):

        if failure and failure.value and hasattr(failure.value, 'response'):
            response = failure.value.response

            if response:
                item = self._enrich_base_data(response)
                self.logger.error("errback: %s" % item)
                self.crawler.stats.inc_crawled_pages(response.meta['crawlid'])
                return item
            else:
                self.logger.error("failure has NO response")
        else:
            self.logger.error("failure or failure.value is NULL, failure: %s" % failure)

    @parse_next_method_wrapper
    def next_request_callback(self, response):

        key = response.meta.get("next_key")
        field = copy.deepcopy(ITEM_FIELD[self.name])

        for k, v in ITEM_FIELD[self.name]:
            if k == key:
                break
            else:
                field.pop(0)

        self.logger.debug("start in parse %s ..." % [x[0] for x in field])
        item = self.reset_item(response.meta['item_half'])
        # 删除增发请求的这个字段的request，防止递归 add by msc 2016.11.26
        del field[0][1]["request"]
        return self.process_forward(self.common_property(response, item, field), response, item)




def start(spiders, globals, module_name, item_field, item_xpath, page_xpath):

    ITEM_FIELD.update(item_field)
    ITEM_XPATH.update(item_xpath)
    PAGE_XPATH.update(page_xpath)

    def create(k, v):
        v["__module__"] = module_name
        return type("%sSpider" % k, (ClusterSpider,), v)

    index = 0

    for k, v in spiders.items():
        v.update({"name": k})
        exec("cls_%s = create(k, v)"% index, locals(), globals)
        index += 1