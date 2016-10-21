# -*- coding:utf-8 -*-
from walker.spiders.constant.page_xpath import PAGE_XPATH


PAGE_XPATH["bluefly"] = [
        '//*[@id="page-content"]//a[@rel="next"]/@href',
    ]
PAGE_XPATH["zhaopin"] = [
        '//a[@class="next-page"]/@href',
    ]
PAGE_XPATH["caoliu"] = [
        u"//a[contains(text(), '下一頁')]/@href",
    ]