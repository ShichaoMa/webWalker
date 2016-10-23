# -*- coding:utf-8 -*-
import argparse

def format(d, f=False):
    for k, v in d.items():
        if f:
            print("reason --> %s"%v.ljust(22))
            print("url    --> %s"%k.ljust(22))
        else:
            print("%s -->  %s"%(k.ljust(22), v))

def start(crawlid, host, custom):
    if custom:
        from custom_redis.client import Redis
    else:
        from redis import Redis

    redis_conn = Redis(host)
    key = "crawlid:%s"%crawlid
    failed_pages = int(redis_conn.hget(key, "failed_download_pages") or 0)
    format(redis_conn.hgetall(key))
    if failed_pages :
        print_if = raw_input("show the failed pages? y/n default n:")
        if print_if == "y":
            key_ = "failed_pages:%s" % crawlid
            p = redis_conn.hgetall(key_)
            format(p, True)


def main():
    parser = argparse.ArgumentParser(description="usage: %prog [options]")
    parser.add_argument("--host", default="127.0.0.1", help="redis host")
    parser.add_argument("-p", "--port", default="6379", help="redis port")
    parser.add_argument("crawlids", nargs="+", help="crawlids")
    parser.add_argument("--custom", action="store_true", default=False)
    args = parser.parse_args();
    for crawlid in args.crawlids:
        start(crawlid=crawlid, host=args.host, custom=args.custom)


if __name__ == "__main__":
    main()
