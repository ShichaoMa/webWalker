# -*- coding:utf-8 -*-
import sys
import argparse
import traceback


class RedisFeed:

    def __init__(self, crawlid, spiderid, url, urls_file, priority, port, host, custom):

        self.name = "redis_feed"
        self.crawlid = crawlid
        self.spiderid = spiderid
        self.url = url
        self.urls_file = urls_file
        self.priority = priority
        self.port = port
        self.host = host
        self.custom = custom
        self.inc = 0
        self.failed_count, self.failed_rate, self.sucess_rate = 0, 0, 0

        if self.custom:
            from custom_redis.client import Redis
        else:
            from redis import Redis

        self.redis_conn = Redis(host=self.host, port=self.port)
        self.clean_previous_task(self.crawlid)

    @classmethod
    def parse_args(cls):

        parser = argparse.ArgumentParser(description="usage: %prog [options]")
        parser.add_argument('-rh', "--redis-host", dest="host", type=str, default="127.0.0.1", help="Redis host to feed in. ")
        parser.add_argument('-rp', "--redis-port", dest="port", type=int, default=6379, help="Redis port to feed in. ")
        parser.add_argument('-u', '--url', type=str, help="The url to crawl, a list of products. ")
        parser.add_argument('-uf', '--urls-file', type=str, help="The urlsfile to crawl, single product. ")
        parser.add_argument('-c', '--crawlid', required=True, type=str, help="An unique Id for a crawl task. ")
        parser.add_argument('-s', '--spiderid', required=True, type=str, help="The website you wanna crawl. ")
        parser.add_argument('-p', '--priority', type=int, default=100, help="Feed in the task queue with priority. ")
        parser.add_argument('--custom', action="store_true", help="Use the custom redis whether or not. ")
        return cls(**vars(parser.parse_args()))

    def clean_previous_task(self, crawlid):
        failed_keys = self.redis_conn.keys("failed_download_*:%s" % crawlid)
        for fk in failed_keys:
            self.redis_conn.delete(fk)

        self.redis_conn.delete("crawlid:%s" % crawlid)
        self.redis_conn.delete("crawlid:%s:model" % crawlid)

    def start(self):
        sucess_rate, failed_rate = 0, 0
        # item抓取
        if self.urls_file:
            with open(self.urls_file) as f:
                lst = f.readlines()
                lines_count = len(lst)
                for index, url in enumerate(lst):
                    json_req = '{"url":"%s","crawlid":"%s","spiderid":"%s","callback":"parse_item", "priority":%s}' % (
                        url.strip("\357\273\277\r\n"),
                        self.crawlid,
                        self.spiderid,
                        self.priority
                    )
                    self.failed_count += self.feed(self.get_name(), json_req)
                    sucess_rate, failed_rate = self.show_process_line(lines_count, index + 1, self.failed_count)
                self.redis_conn.hset("crawlid:%s" % self.crawlid, "total_pages", lines_count)
                self.redis_conn.expire("crawlid:%s" % self.crawlid, 2 * 24 * 60 * 60)
        # 分类抓取
        else:
            url_list = self.url.split("     ")
            lines_count = len(url_list)

            for index, url in enumerate(url_list):
                json_req = '{"url":"%s","crawlid":"%s","spiderid":"%s","callback":"parse","priority":%s}' % (
                    url.strip(),
                    self.crawlid,
                    self.spiderid,
                    self.priority,
                )
                self.failed_count += self.feed(self.get_name(), json_req)
                sucess_rate, failed_rate = self.show_process_line(lines_count, index + 1, self.failed_count)
        print "\ntask feed complete. sucess_rate:%s%%, failed_rate:%s%%"%(sucess_rate, failed_rate)

    def get_name(self):
        return "{sid}:item:queue".format(sid=self.spiderid)

    def feed(self, queue_name, req):

        if self.custom:
            from custom_redis.client.errors import RedisError
        else:
            from redis import RedisError

        try:
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