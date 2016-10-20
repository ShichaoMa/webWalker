# -*- coding:utf-8 -*-
import traceback
from functools import wraps

from scrapy.exceptions import IgnoreRequest
from scrapy.http import Request

from utils import get_ip_address
from constant.item_field import ITEM_FIELD


IP = get_ip_address()


def stats_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):

        try:
            return func(*args, **kwds)
        except Exception:
            traceback.print_exc()

    return wrapper_method


def parse_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):

        try:
            return func(*args, **kwds)
        except Exception:
            self = args[0]
            if hasattr(self, "change_proxy"):
                self.change_proxy = True
            response = args[1]
            msg = "error heppened in %s method. Error:%s"%(func.__name__, traceback.format_exc())
            self.logger.info(msg)
            self.crawler.stats.set_failed_download(response.meta, "%s \n heppened in %s of %s"%(traceback.format_exc(), func.__name__, IP))

    return wrapper_method


def parse_next_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):
        self = args[0]
        response = args[1]
        k = response.meta.get("next_key", "unknow")

        try:
            return func(*args, **kwds)
        except Exception:
            msg = "error heppened in %s method. Error:%s"%(func.__name__, traceback.format_exc())
            self.logger.info(msg)
            item = response.meta.get("item_half", {})
            self.crawler.stats.set_failed_download(
                response.meta, "%s \n heppened in %s of %s product_id: %s," %
                (traceback.format_exc(), func.__name__, IP, item.get("product_id", "unknow"), ),
                k)

    return wrapper_method


def next_request_method_wrapper(self):

    def wrapper(func):
        @wraps(func)

        def wrapper_method(*args, **kwds):

            try:
                return func(*args, **kwds)
            except Exception:
                msg = "error heppened in %s method. Error:%s"%(func.__name__, traceback.format_exc())
                self.logger.info(msg)

                if self.present_item:
                    self.spider.crawler.stats.set_failed_download(
                        self.present_item if not isinstance(self.present_item, Request) else self.present_item["meta"],
                        "%s \n heppened in %s of %s"%(traceback.format_exc(), func.__name__, IP))

        return wrapper_method

    return wrapper


def enqueue_method_wrapper(self):

    def wrapper(func):
        @wraps(func)

        def wrapper_method(*args, **kwds):

            try:
                return func(*args, **kwds)
            except Exception:
                msg = "error heppened in %s method of %s. Error:%s"%(func.__name__, IP, traceback.format_exc())
                self.logger.info(msg)

        return wrapper_method

    return wrapper


def pipline_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):
        count = 0
        spider = args[2]
        item = args[1]

        while count < 3:

            try:
                return func(*args, **kwds)
            except Exception:
                spider.log("error heppened in %s method of %s. Error:%s, processing %s,"%(func.__name__, IP, traceback.format_exc(), str(item)))
                continue

        spider.crawler.stats.set_failed_download(item.meta, traceback.format_exc())

        return item

    return wrapper_method


def process_requset_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):
        self = args[0]
        request = kwds.get("request")
        spider = kwds.get("spider")

        try:
            return func(*args, **kwds)
        except IgnoreRequest:
            raise
        except Exception:
            spider.logger.error("error heppened in process_request method of %s in %s. Error:%s, processing %s," % (
            self.__class__.__name__, IP, traceback.format_exc(), request.url))
            spider.crawler.stats.set_failed_download(request.meta, traceback.format_exc())

    return wrapper_method


def process_response_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):
        self = args[0]
        request = kwds.get("request")
        response = kwds.get("response")
        spider = kwds.get("spider")

        try:
            return func(*args, **kwds)
        except IgnoreRequest:
            raise
        except Exception:
            spider.logger.error("error heppened in process_response method of %s in %s. Error:%s, processing %s," % (
                self.__class__.__name__, IP, traceback.format_exc(), response.url))
            spider.crawler.stats.set_failed_download(request.meta, traceback.format_exc())
            if hasattr(spider, "change_proxy"):spider.change_proxy=True

    return wrapper_method


def process_exception_method_wrapper(func):

    @wraps(func)
    def wrapper_method(*args, **kwds):
        self = args[0]
        request = kwds.get("request")
        exception = kwds.get("exception")
        spider = kwds.get("spider")

        try:
            return func(*args, **kwds)
        except IgnoreRequest:
            raise
        except Exception:
            spider.logger.error("error heppened in process_exception method of %s in %s, deal with exception %s. Error:%s, processing %s," % (
                self.__class__.__name__, IP, "%s:%s"%(exception.__class__.__name__, exception), traceback.format_exc(), request.url))
            spider.crawler.stats.set_failed_download(request.meta, traceback.format_exc())

    return wrapper_method


@parse_next_method_wrapper
def next_request_callback(self, response):

    k = response.meta.get("next_key")
    type = response.meta.get("item_type")
    filed_dict = ITEM_FIELD[self.name]
    v = filter(lambda x:x, map(lambda x:x if x[0] == k else "", filed_dict["common"]+filed_dict[type]))[0][1]
    self.logger.debug("start in parse %s ..." % k)
    item = self.reset_item(response.meta['item_half'], type)
    item[k] = self.get_val(v, response, item, is_after=True) or v.get("default", "")
    self.logger.debug("crawlid:%s, sign_id %s, suceessfully yield item"%(item.get("crawlid"), item.get(SPIDER_SIGN[self.name], "unknow")))
    self.crawler.stats.inc_crawled_pages(response.meta['crawlid'])

    return item


def send_request_wrapper(response, item, k, type):

    def process_request(func):

        def wrapper():
            url = func(item, response)
            response.meta['item_half'] = dict(item)
            response.meta['next_key'] = k
            response.meta['item_type'] = type

            if url:
                return Request(
                        url=url,
                        meta=response.meta,
                        callback=next_request_callback,
                        dont_filter=response.request.dont_filter
                    )

        return wrapper

    return process_request
