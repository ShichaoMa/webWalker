# -*- coding:utf-8 -*-
import logging
import sys
import os
import re
import errno
import socket
import struct
import psutil
from cloghandler import ConcurrentRotatingFileHandler
from urllib import urlencode
from urlparse import urlparse, urlunparse

from log_to_kafka import LogFactory, KafkaHandler


class LoggerDiscriptor(object):

    def __init__(self, logger=None):

        self.logger = logger

    def __get__(self, instance, cls):

        if not self.logger:
            instance.set_logger()

        return self.logger

    def __set__(self, instance, value):

        self.logger = value


class Logger(object):

    def set_logger(self, crawler):

        self.logger = LogFactory._instance or self.init_logger(crawler)

    def init_logger(self, crawler):

        my_level = crawler.settings.get('SC_LOG_LEVEL', 'INFO')
        my_name = "%s_%s" % (crawler.spidercls.name, get_ip_address())
        my_output = crawler.settings.get('SC_LOG_TYPE', "FILE")
        my_json = crawler.settings.get('SC_LOG_JSON', True)
        my_dir = crawler.settings.get('SC_LOG_DIR', 'logs')
        my_bytes = crawler.settings.get('SC_LOG_MAX_BYTES', '10MB')
        my_file = "%s_%s.log" % (crawler.spidercls.name, get_ip_address())
        my_backups = crawler.settings.get('SC_LOG_BACKUPS', 5)
        st = crawler.settings.get("SPIDER_REQ")

        if st:
            my_name += "_%s" % st
            my_file = my_file[:-4] + "_%s" % st + ".log"
        logger = LogFactory.get_instance(json=my_json,
                                              name=my_name,
                                              level=my_level)

        if my_output == "CONSOLE":
            logger.set_handler(logging.StreamHandler(sys.stdout))
        elif my_output == "KAFKA":
            logger.set_handler(KafkaHandler(crawler.settings))
        else:

            try:
                os.makedirs(my_dir)
            except OSError as exception:

                if exception.errno != errno.EEXIST:
                    raise

            file_handler = ConcurrentRotatingFileHandler(my_dir + '/' + my_file,
                                                         maxBytes=my_bytes,
                                                         backupCount=my_backups)
            logger.set_handler(file_handler)

        return logger


def _get_ip_address(ifname):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    import fcntl
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(), 0x8915, struct.pack('256s', ifname[:15])
    )[20:24])


def _get_net_interface():

    p = os.popen("ls /sys/class/net")
    buf = p.read(10000)
    return buf.strip(" \nlo")


def get_netcard():

    netcard_info = []
    info = psutil.net_if_addrs()

    for k,v in info.items():

        for item in v:

            if item[0] == 2 and not item[1]=='127.0.0.1':
                netcard_info.append((k,item[1]))

    return netcard_info


def get_ip_address():

    if sys.platform == "win32":
        hostname = socket.gethostname()
        IPinfo = socket.gethostbyname_ex(hostname)
        r = IPinfo[2][2]
    else:
        ips = get_netcard()

        if ips:
            return ips[0][1]
        else:
            shell_command = "ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'"
            os.popen(shell_command).read().strip()
        #
        # try:
        #     r = _get_ip_address(_get_net_interface())
        # except Exception:
        #
        #     try:
        #         r = _get_ip_address('enp0s25')
        #     except Exception:
        #
        #         try:
        #             r = _get_ip_address('enp0s8')
        #         except Exception:
        #
        #             try:
        #                 r = _get_ip_address('ens32')
        #             except Exception:
        #                 r = os.popen( shell_command ).read().strip()
    return r


def url_arg_increment(arg_pattern, url):
    """
    对于使用url arguments标志page字段而实现分页的url，使用这个函数生成下一页url
    关于正则表达式：
    第一组匹配url分页参数前面的部分
    第二组匹配分页参数的名字+等号+起始页的页序数
    第三组匹配当前页数
    第四组匹配分页参数后来的值
    正常使用时，一 三 四组不需要修改，只需要修改第二组中的值即可
    @param arg_pattern:r'(.*?)(pn=0)(\d+)(.*)',
    @param url:http://www.nike.com/abc?pn=1
    @return:http://www.nike.com/abc?pn=2
    """
    first_next_page_index = int(re.search(r"\d+", arg_pattern).group())
    arg_pattern = arg_pattern.replace(str(first_next_page_index), "")
    mth = re.search(arg_pattern, url)
    if mth:
        prefix = mth.group(1)
        midfix = mth.group(2)
        page = int(mth.group(3))
        stuffix = mth.group(4)
        return "%s%s%s%s" % (prefix, midfix, page + 1, stuffix)
    else:
        midfix = re.sub(r"[\(\)\\d\+\.\*\?]+", "", arg_pattern)
        if url.count("?"):
            midfix = "&" + midfix
        else:
            midfix = "?" + midfix
        return "%s%s%s" % (url, midfix, first_next_page_index + 1)



def url_item_arg_increment(index, url, count):
    """
    对于使用url arguments标志item的index而实现分页的url，使用这个函数生成下一页url
    @param index: start 用来指定index的相应字段
    @param url: http://www.ecco.com/abc?start=30
    @param count:  30当前页item的数量
    @return: http://www.ecco.com/abc?start=60
    """
    mth = re.search(r"%s=(\d+)"%index, url)
    if mth:
        start = int(mth.group(1))
    else:
        start = 1
    parts = urlparse(url)
    if parts.query:
        query = dict(map(lambda x: x.split("="), parts.query.split("&")))
        query[index] = start + count
    else:
        query = {index:count+1}
    return urlunparse(parts._replace(query=urlencode(query)))


def url_path_arg_increment(pattern_str, url):
    """
    对于将页数放到path中的url,使用这个函数生成下一页url
    如下：
    其中subpath=用来标明该url是用urlpath中某一部分自增来进行翻页
    等号后面为正则表达式
        第一组用来匹配自增数字前面可能存在的部分（可为空）
        第二组用来匹配自增数字
        第三组来匹配自增数字后面可能存在的部分（可为空）
    如示例中给出的url，经过转换后得到下一页的url为
    'http://www.timberland.com.hk/en/men-apparel-shirts/page/2/'
    其中http://www.timberland.com.hk/en/men-apparel-shirts为原url
    /page/为第一组所匹配; 2为第二组匹配的; /为第三组匹配的
    当给出的url为'http://www.timberland.com.hk/en/men-apparel-shirts/page/2/'
    输出结果为'http://www.timberland.com.hk/en/men-apparel-shirts/page/3/'
    @param pattern_str: r'subpath=(/page/)(\d+)(/)'
    @param url: 'http://www.timberland.com.hk/en/men-apparel-shirts‘
    @return:'http://www.timberland.com.hk/en/men-apparel-shirts/page/2/'
    """
    pattern = pattern_str.split("=")[1]
    mth = re.search(pattern, url)
    if mth:
        return re.sub(pattern, "\g<1>%s\g<3>"%(int(mth.group(2))+1), url)
    else:
        page_num = 2
        parts = urlparse(url)
        path = re.sub(r"\((.*)\)(?:\(.*\))\((.*)\)", repl_wrapper(parts.path, page_num), pattern).replace("\\", "")
        return urlunparse(parts._replace(path=path))


def repl_wrapper(path, page_num):
    def _repl(mth):
        sub_path = "%s%d%s"%(mth.group(1), page_num, mth.group(2))
        if path.endswith(mth.group(2).replace("\\", "")):
            return path[:path.rfind(mth.group(2).replace("\\", ""))]+sub_path
        else:
            return path + sub_path
    return _repl

