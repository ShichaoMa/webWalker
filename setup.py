# -*- coding:utf-8 -*-
import codecs
import os
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup


VERSION = '1.0.3'

AUTHOR = "cn"

AUTHOR_EMAIL = "308299269@qq.com"

URL = "https://www.github.com/ShichaoMa/webWalker"


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = "web-walker"

DESCRIPTION = "your can crawl web pages with litte settings. based on scrapy. "

LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "crawl web spider scrapy"

LICENSE = "MIT"

PACKAGES = ["walker", "feed_monitor", "walker.spiders", "walker.spiders.constant"]

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'feed = feed_monitor:main',
        ],
    },
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    install_requires=["scrapy==1.0.5", "log-to-kafka", "custom-redis", "openpyxl", "tldextract==2.0.1"],
    include_package_data=True,
    zip_safe=True,
)