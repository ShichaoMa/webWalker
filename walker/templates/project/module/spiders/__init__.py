# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy.conf import settings

from walker.spiders import start
from .spiders import SPIDERS
from .item_field import ITEM_FIELD
from .item_xpath import ITEM_XPATH
from .page_xpath import PAGE_XPATH


start(SPIDERS, globals(), settings.get("NEWSPIDER_MODULE"), ITEM_FIELD, ITEM_XPATH, PAGE_XPATH)