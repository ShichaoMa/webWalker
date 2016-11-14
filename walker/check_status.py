# -*- coding:utf-8 -*-
import fnmatch
import argparse


def format(d, f=False):
    for k, v in d.items():
        if f:
            print("reason --> %s"%v.ljust(30))
            print("url    --> %s"%k.ljust(30))
        else:
            print("%s -->  %s"%(k.ljust(30), v))


def start(crawlid, host, custom):
    if custom:
        from custom_redis.client import Redis
    else:
        from redis import Redis

    redis_conn = Redis(host)
    key = "crawlid:%s"%crawlid
    data = redis_conn.hgetall(key)
    failed_keys = filter(lambda x: fnmatch.fnmatch(x, "failed_download_*"), data.keys())
    format(data)
    for fk in failed_keys:
        print_if = raw_input("show the %s? y/n default n:"%fk.replace("_", " "))
        if print_if == "y":
            key_ = "%s:%s" % (fk, crawlid)
            p = redis_conn.hgetall(key_)
            format(p, True)


def main():
    parser = argparse.ArgumentParser(description="usage: %prog [options]")
    parser.add_argument("--host", default="127.0.0.1", help="redis host")
    parser.add_argument("-p", "--port", default="6379", help="redis port")
    parser.add_argument("crawlids", nargs="+", help="Crawlids to check. ")
    parser.add_argument("--custom", action="store_true", default=False, help="Use the custom redis whether or not. ")
    args = parser.parse_args()
    for crawlid in args.crawlids:
        start(crawlid=crawlid, host=args.host, custom=args.custom)


if __name__ == "__main__":
    main()
