# -*- coding:utf-8 -*-
from cluster_spider import ClusterSpider


SPIDERS = {
    "bluefly": {
        "allowed_domains": ["bluefly.com"]
    },
    "zhaopin": {
        "allowed_domains": ["zhaopin.com"]
    },
    "caoliu": {
        "allowed_domains": ["c6.ek9.biz"]
    },
}

def create(k, v):
    return type("%sSpider"%k, (ClusterSpider, ), v)

index = 0
for k, v in SPIDERS.items():
    v.update({"name":k})
    exec("cls_%s = create(k, v)"%index)
    index += 1