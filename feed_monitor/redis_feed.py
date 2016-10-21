# -*- coding:utf-8 -*-
import os
import sys
import argparse
import traceback
from log_to_kafka import Logger
from tldextract import extract

class RedisFeed(Logger):

    def __init__(self, settings, crawlid, spiderid, url, priority):
        self.name = "redis_feed"
        super(RedisFeed, self).__init__(settings)
        self.crawlid = crawlid
        self.spiderid = spiderid
        self.url = url
        self.priority = priority
        self.inc = 0
        self.extract = extract
        self.setup()

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--settings', type=str, default="settings.py")
        parser.add_argument('-u', '--url', required=True, type=str)
        parser.add_argument('-c', '--crawlid', required=True, type=str)
        parser.add_argument('-s', '--spiderid', required=True, type=str)
        parser.add_argument('-p', '--priority', type=int, default=100)
        return cls(**vars(parser.parse_args()))

    def setup(self):
        self.failed_count, self.failed_rate, self.sucess_rate = 0, 0, 0
        if self.settings.get("CUSTOM_REDIS"):
            from custom_redis.client import Redis
        else:
            from redis import Redis
        self.redis_conn = Redis(host=self.settings.get("REDIS_HOST"),
                           port=self.settings.get("REDIS_PORT"))
        self.redis_conn.delete("crawlid:%s" % self.crawlid)
        self.redis_conn.delete("failed_pages:%s" % self.crawlid)
        self.redis_conn.delete("crawlid:%s:model" % self.crawlid)

    def start(self):
        url_list = self.url.split("     ")
        lines_count = len(url_list)
        sucess_rate, failed_rate = 0, 0
        for index, url in enumerate(url_list):
            json_req = '{"url":"%s","crawlid":"%s","spiderid":"%s","callback":"parse","priority":%s}' % (
                url.strip(),
                self.crawlid,
                self.spiderid,
                self.priority,
            )
            ex_res = self.extract(url)
            queue_name = "{sid}:{dom}.{suf}:queue".format(
                sid=self.spiderid,
                dom=ex_res.domain,
                suf=ex_res.suffix)
            self.failed_count += self.feed(queue_name, json_req)
            sucess_rate, failed_rate = self.show_process_line(lines_count, index + 1, self.failed_count)
        self.redis_conn.hset("crawlid:%s" % self.crawlid, "type", "get")
        print "\ntask feed complete. sucess_rate:%s%%, failed_rate:%s%%"%(sucess_rate, failed_rate)

    def feed(self, queue_name, req):
        if self.settings.get("CUSTOM_REDIS"):
            from custom_redis.client.errors import RedisError
        else:
            from redis import RedisError
        try:
            if self.settings.get("CUSTOM_REDIS"):
                self.redis_conn.zadd(queue_name, -self.priority, req)
            else:
                self.redis_conn.zadd(queue_name, req, -self.priority)
            return 0
        except RedisError:
            traceback.print_exc()
            return 1

    def show_process_line(self, count, num, failed):
        per = count / 100
        success = num - failed
        success_rate = success * 100.0 / count
        failed_rate = failed * 100.0 / count
        str_success_rate = "%.2f%%  " % success_rate
        str_failed_rate = "%.2f%%  " % failed_rate
        if num >= self.inc:
            self.inc += per
            if sys.platform == "win32":
                import ctypes
                std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)
                color_ctl = ctypes.windll.kernel32.SetConsoleTextAttribute
                color_ctl(std_out_handle, 2)
                print "\r", str_success_rate,
                color_ctl(std_out_handle, 32)
                print int(success_rate * 30 / 100) * ' ',
                if int(failed_rate):
                    color_ctl(std_out_handle, 64)
                    print int(failed_rate * 30 / 100) * ' ',
                color_ctl(std_out_handle, 0)
                color_ctl(std_out_handle, 4)
                print str_failed_rate,
                color_ctl(std_out_handle, 7)
            else:
                print "\r", str_success_rate,
                print "%s%s" % (int(success_rate * 50 / 100) * '\033[42m \033[0m',
                                int(failed_rate * 50 / 100) * '\033[41m \033[0m'), str_failed_rate,
        return success_rate, failed_rate

if __name__ == "__main__":
    RF = RedisFeed.parse_args()
    RF.start()