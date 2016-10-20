# -*- coding:utf-8 -*-


PAGE_XPATH = {
    "bluefly": [
        '//*[@id="page-content"]//a[@rel="next"]/@href',
    ],
    "zhaopin": [
        '//a[@class="next-page"]/@href',
    ],
    "caoliu": [
        u"//a[contains(text(), '下一頁')]/@href",
    ],
}