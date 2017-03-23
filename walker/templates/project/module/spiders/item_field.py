# -*- coding:utf-8 -*-


ITEM_FIELD = {
    "bluefly": [

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
    ],
    "douban": [
        ("title", {
            "xpath": [
                "//div[@class='item-info']/h3/text()",
            ]
        })
    ]
}




