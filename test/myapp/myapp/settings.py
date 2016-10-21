# -*- coding:utf-8
# This file houses all default settings for the Crawler
# to override please use a custom localsettings.py file
# Scrapy Cluster Settings
# ~~~~~~~~~~~~~~~~~~~~~~~
import pkgutil

# Specify the host and port to use when connecting to Redis.
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

CUSTOM_REDIS = True

RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 403, 304]
# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# seconds to wait between seeing new queues, cannot be faster than spider_idle time of 5
SCHEDULER_QUEUE_REFRESH = 10

# we want the queue to produce a consistent pop flow
QUEUE_MODERATED = True

# how long we want the duplicate timeout queues to stick around in seconds
DUPEFILTER_TIMEOUT = 600

# how often to refresh the ip address of the scheduler
SCHEDULER_IP_REFRESH = 60

CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 4

# 自带了一些user_agents，可不改
USER_AGENT_LIST = pkgutil.get_data('walker', 'user_agents.list')

# 500+ retry times
RETRY_TIMES = 20

# 需要改
PROXY_LIST = pkgutil.get_data('myapp', 'proxy.list')

# redirect max times
REDIRECT_MAX_TIMES = 20

REDIRECT_PRIORITY_ADJUST = -1


# how many times to retry getting an item from the queue before the spider is considered idle
SCHEUDLER_ITEM_RETRIES = 3

# log setup scrapy cluster crawler
SC_LOG_LEVEL = 'DEBUG'
SC_LOG_TYPE = "CONSOLE"
SC_LOG_JSON = False
SC_LOG_DIR = "logs"
SC_LOG_MAX_BYTES = '10MB'
SC_LOG_BACKUPS = 5
TO_KAFKA = False
KAFKA_HOSTS = '192.168.200.58:9092'
TOPIC = "log.incoming"


HEADERS = {
    "ashford": {
                "Cookie": {"userPrefLanguage": "zh_CN"},
                "Host": "www.ashford.com",
                },
    "onlineshoes": {
                "Cookie": {
                    "OLS": "cur=USD&sc=US&iwmh=CN%7cUS",
                    "path": "/"
                },
                "Host": "www.onlineshoes.com",
                },
    "jomashop": {
                "Cookie": {"D_SID": "23.83.236.209:UrJdaeCr0OXNj8YS4rPJGGgSy06q86mWo2sbfA1lbrg",
                           "D_PID": "3119DF0B-3C06-308A-88B4-6118E4B86D16",
                           "D_IID": "939D1695-634B-356A-B981-8ACEE26C1FC4",
                           "D_UID": "F1FBDFB9-DEF1-32D4-8299-4F784475575A",
                           "D_HID": "TgwvBOECiSZjP2tULaaRUypFxBrZ0rmSTEeGsHUfx4A",
                           "D_ZID": "BD763E80-80C7-3BE6-8945-E553C4FB1029"
                           },
                }
}


# 需要改
BOT_NAME = 'myapp'

# 需要改
SPIDER_MODULES = ['myapp.spiders']
# 需要改
NEWSPIDER_MODULE = 'myapp.spiders'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "walker.scheduler.Scheduler"

STATS_CLASS = 'walker.stats_collectors.StatsCollector'


# Store scraped item in redis for post-processing.
ITEM_PIPELINES = {
    'walker.pipelines.JSONPipeline': 100,
    'walker.pipelines.LoggingBeforePipeline': 1,
    'walker.pipelines.LoggingAfterPipeline': 101,
}

SPIDER_MIDDLEWARES = {
    # disable built-in DepthMiddleware, since we do our own
    # depth management per crawl request
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware':None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    #'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'walker.downloadermiddlewares.CustomUserAgentMiddleware': 400,
    # Handle timeout retries with the redis scheduler and logger
    'walker.downloadermiddlewares.CustomRetryMiddleware': 510,
    #"walker.downloadermiddlewares.ProxyMiddleware": 511,
    # exceptions processed in reverse order
    # custom cookies to not persist across crawl requests
    'walker.downloadermiddlewares.CustomRedirectMiddleware': 600,
    'walker.downloadermiddlewares.CustomCookiesMiddleware': 700,
}

# Disable the built in logging in production
LOG_ENABLED = True
COOKIES_DEBUG = False
# Allow all return codes
HTTPERROR_ALLOW_ALL = True

DOWNLOAD_TIMEOUT = 30

# Avoid in-memory DNS cache. See Advanced topics of docs for info
DNSCACHE_ENABLED = True


# Local Overrides
# ~~~~~~~~~~~~~~~

try:
    from localsettings import *
except ImportError:
    pass
