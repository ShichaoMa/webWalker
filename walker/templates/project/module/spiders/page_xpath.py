# -*- coding:utf-8 -*-


PAGE_XPATH = {
    "bluefly": [
        '//*[@id="page-content"]//a[@rel="next"]/@href',
    ],
    "douban": [
        "//div[@class='pagination']/a[last()]/@href",
    ]
}
