# -*- coding:utf-8 -*-
from .redis_feed import RedisFeed
from .check_status import main


VERSION = '3.0.2'

AUTHOR = "cn"

AUTHOR_EMAIL = "308299269@qq.com"

URL = "https://www.github.com/ShichaoMa/webWalker"


def check():
    main()


def feed():
    RedisFeed.parse_args().start()