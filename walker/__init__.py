# -*- coding:utf-8 -*-


VERSION = '1.2.2'

AUTHOR = "cn"

AUTHOR_EMAIL = "308299269@qq.com"

URL = "https://www.github.com/ShichaoMa/webWalker"

from redis_feed import RedisFeed
from check_status import main

def check():
    main()

def feed():
    RedisFeed.parse_args().start()