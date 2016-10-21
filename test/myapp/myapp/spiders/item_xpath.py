# -*- coding:utf-8 -*-
from walker.spiders.constant.item_xpath import ITEM_XPATH


ITEM_XPATH["bluefly"] = [
        '//ul[@class="mz-productlist-list mz-l-tiles"]/li//a[@class="mz-productlisting-title"]/@href',
    ]
ITEM_XPATH["zhaopin"] = [
        '//td[@class="zwmc"]/div/a/@href',
    ]
ITEM_XPATH["caoliu"] = [
        u"//tr/td[contains(text(), '亞洲')]/h3/a/@href",
    ]