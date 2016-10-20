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

USER_AGENT_LIST = pkgutil.get_data('walker', 'user_agents.list')

# 500+ retry times
RETRY_TIMES = 20

PROXY_LIST = pkgutil.get_data('walker', 'proxy.list')

# redirect max times
REDIRECT_MAX_TIMES = 20

REDIRECT_PRIORITY_ADJUST = -1


CHECK_URL = "https://www.amazon.com/gp/product/B000EXAAJE/ref=twister_dp_update?ie=UTF8&psc=1"

'''
----------------------------------------
The below parameters configure how spiders throttle themselves across the cluster
All throttling is based on the TLD of the page you are requesting, plus any of the
following parameters:

Type: You have different spider types and want to limit how often a given type of
spider hits a domain

IP: Your crawlers are spread across different IP's, and you want each IP crawler clump
to throttle themselves for a given domain

Combinations for any given Top Level Domain:
None - all spider types and all crawler ips throttle themselves from one tld queue
Type only - all spiders throttle themselves based off of their own type-based tld queue,
    regardless of crawler ip address
IP only - all spiders throttle themselves based off of their public ip address, regardless
    of spider type
Type and IP - every spider's throttle queue is determined by the spider type AND the
    ip address, allowing the most fined grained control over the throttling mechanism
'''
# add Spider type to throttle mechanism
SCHEDULER_TYPE_ENABLED = True

# add ip address to throttle mechanism
SCHEDULER_IP_ENABLED = True
'''
----------------------------------------
'''

# how many times to retry getting an item from the queue before the spider is considered idle
SCHEUDLER_ITEM_RETRIES = 3

# log setup scrapy cluster crawler
SC_LOG_LEVEL = 'DEBUG'
SC_LOG_STDOUT = "FILE"
SC_LOG_JSON = False
SC_LOG_DIR = "logs"
SC_LOG_MAX_BYTES = '10MB'
SC_LOG_BACKUPS = 5
PRINT_DEBUG = False
TO_KAFKA = False
# Kafka server information
KAFKA_HOSTS = '192.168.200.58:9092'


STATS_RESPONSE_CODES = [
    200,
    404,
    403,
    504,
]
STATS_CYCLE = 5

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

HEADERS = {
    "ashford": {
                "Cookie": "userPrefLanguage=en_US;",
                "Host": "www.ashford.com",
                },
    "onlineshoes": {
                "Cookie": "OLS=cur=USD&sc=US&iwmh=CN%7cUS; path=/;",
                "Host": "www.onlineshoes.com",
                },
    "jomashop": {
                "Cookie": "D_SID=23.83.236.209:UrJdaeCr0OXNj8YS4rPJGGgSy06q86mWo2sbfA1lbrg; D_PID=3119DF0B-3C06-308A-88B4-6118E4B86D16; D_IID=939D1695-634B-356A-B981-8ACEE26C1FC4; D_UID=F1FBDFB9-DEF1-32D4-8299-4F784475575A; D_HID=TgwvBOECiSZjP2tULaaRUypFxBrZ0rmSTEeGsHUfx4A; D_ZID=BD763E80-80C7-3BE6-8945-E553C4FB1029;",
                }
}
# from time variables in scutils.stats_collector class
STATS_TIMES = [
    'SECONDS_15_MINUTE',
    'SECONDS_1_HOUR',
    'SECONDS_6_HOUR',
    'SECONDS_12_HOUR',
    'SECONDS_1_DAY',
    'SECONDS_1_WEEK',
]

# Scrapy Settings
# ~~~~~~~~~~~~~~~

# Scrapy settings for distributed_crawling project
#
BOT_NAME = 'walker'

SPIDER_MODULES = ['walker.spiders']
NEWSPIDER_MODULE = 'walker.spiders'

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
    'walker.downloadermiddlewares.CustomRequestHeaderMiddleware': 390,
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
