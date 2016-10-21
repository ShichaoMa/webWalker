# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from scrapy.conf import settings

from walker.spiders import start
from spiders import SPIDERS


start(SPIDERS, globals(), settings.get("NEWSPIDER_MODULE"))