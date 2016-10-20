# -*- coding:utf-8 -*-
from helper import *
import time
import random



BASE_FIELD = ["success", "domain", "exception", "crawlid", "meta", "response_url", "status_code", "status_msg", "url", "seed"]

ZHAOPIN = [
    ('id', {
        "extract": lambda item, response: re.search("zhaopin.com/(.*).htm", item["meta"]["url"]).group(1)
    }),
    ('position', {
        "xpath": [
            '//div[@class="inner-left fl"]/h1/text()',
        ],
    }),
    ('company', {
        "xpath": [
            '//div[@class="inner-left fl"]/h2/a/text()',
        ],
    }),
    ('salery', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix"]/li[1]/strong/text()',
        ],
    }),
    ('expirence', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix"]/li[5]/strong/text()',
        ],
    }),
    ('qualification', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix"]/li[6]/strong/text()',
        ],
    }),
    ('employ_count', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix"]/li[7]/strong/text()',
        ],
    }),
    ('address', {
        "xpath": [
            '//h2/preceding-sibling::b/../h2/text()',
        ],
    }),
    ('discription', {
        "xpath": [
            '//div[@class="terminalpage-main clearfix"]/div[@class="tab-cont-box"]'
            '/div[@class="tab-inner-cont"]/p/span/text()',
        ],
    }),
    ('scale', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix terminal-company mt20"]/li[1]/strong/text()',
        ],
    }),
    ('character', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix terminal-company mt20"]/li[2]/strong/text()',
        ],
    }),
    ('industry', {
        "xpath": [
            '//ul[@class="terminal-ul clearfix terminal-company mt20"]/li[3]/strong/a/text()',
        ],
    }),
]

CAOLIU = [
             ('product_id', {
                 "extract": lambda item, response: "abc"
             }),
             ('title', {
                 'xpath': [
                     '//title/text()',
                 ],
                 "extract": lambda item, response: "abc"
             }),
             ('images', {
                 "xpath": [
                     "//input/@src",
                 ],
                 "function": lambda x, item: map(lambda y: {"path": "F:\\yazhou4\\%s_%s.%s" % (
                 time.time() + random.random(), item['title'], "jpg" if y.rfind(".") == -1 else y[y.rfind(".") + 1:]),
                                                            "url": y}, x.extract()),
             }),
         ]

BLUEFLY = [

            ('retail_price', {
                "xpath": [
                    '//*[@id="product-selection"]//span[@class="mz-price-retail-label"]/../text()',
                ],
                "function": format_html_xpath_common,
            }),
            ('list_price', {
                "xpath": [
                    '//*[@id="product-selection"]//div[@itemprop="price"]/text() | //div[@id="product-selection"]//div[@class="mz-price"]/text()',
                ],
                "function": format_html_xpath_common,
            }),
            ('brand', {
                "xpath": [
                    '//p[@class="mz-productbrand"]/a/text()',
                ],
            }),
            ('names', {
                "xpath": [
                    '//span[@class="mz-breadcrumb-current"]/text()',
                ],
            }),
            ('product_id', {
                "xpath": [
                    '//li[@itemprop="productID"]/text()',
                ],
            }),
        ]


ITEM_FIELD = {
    "caoliu": CAOLIU,
    "zhaopin": ZHAOPIN,
    "bluefly": BLUEFLY,
}

