# -*- coding:utf-8 -*-
from helper import *



BASE_FIELD = ["success", "domain", "exception", "crawlid", "meta", "response_url", "status_code", "status_msg", "url", "seed"]


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
    "bluefly": BLUEFLY,
}

