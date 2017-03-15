import re
import json
from functools import reduce


def function_xpath_common(x, item):
    """
    xpath转换公共函数
    :param x:
    :param item:
    :return:
    """
    return xpath_exchange(x)


def format_html_xpath_common(x, item):
    """
    直接需要抽取html的字段的公共函数
    :param x:
    :param item:
    :return:
    """
    return format_html_string(xpath_exchange(x))


def xpath_exchange(x):
    """
    将xpath结果集进行抽取拼接成字符串
    :param x:
    :return:
    """
    return "".join(x.extract()).strip()


def function_re_common(x, item):
    """
    re转换公共函数
    :param x:
    :param item:
    :return:
    """
    return re_exchange(x)


def safely_json_re_common(x, item):
    """
    直接需要抽取json数据的字段的公共函数
    :param x:
    :param item:
    :return:
    """
    return safely_json_loads(re_exchange(x).replace('&nbsp;', ''))


def re_exchange(x):
    """
    将re的结果集进行抽取拼接成字符串
    :param x:
    :param item:
    :return:
    """
    return "".join(x).strip()


def safely_json_loads(json_str, defaulttype=dict, escape=True):
    """
    返回安全的json类型
    :param json_str: 要被loads的字符串
    :param defaulttype: 若load失败希望得到的对象类型
    :param escape: 是否将单引号变成双引号
    :return:
    """
    if not json_str:
        return defaulttype()
    elif escape:
        return json.loads(replace_quote(json_str))
    else:
        return json.loads(json_str)


def chain_all(iter):
    """
    连接两个序列或字典
    :param iter:
    :return:
    """
    iter = list(iter)
    if not iter:
        return None
    if isinstance(iter[0], dict):
        result = {}
        for i in iter:
            result.update(i)
    else:
        result = reduce(lambda x, y: list(x)+list(y), iter)
    return result


def replace_quote(json_str):
    """
    将要被json.loads的字符串的单引号转换成双引号，如果该单引号是元素主体，而不是用来修饰字符串的。则不对其进行操作。
    :param json_str:
    :return:
    """
    double_quote = []
    new_lst = []
    for index, val in enumerate(json_str):
        if val == '"' and json_str[index-1] != "\\":
            if double_quote:
                double_quote.pop(0)
            else:
                double_quote.append(val)
        if val== "'" and json_str[index-1] != "\\":
            if not double_quote:
                val = '"'
        new_lst.append(val)
    return "".join(new_lst)


def format_html_string(a_string):
    """
    格式化html
    :param a_string:
    :return:
    """
    a_string = a_string.replace('\n', '')
    a_string = a_string.replace('\t', '')
    a_string = a_string.replace('\r', '')
    a_string = a_string.replace('  ', '')
    a_string = a_string.replace(u'\u2018', "'")
    a_string = a_string.replace(u'\u2019', "'")
    a_string = a_string.replace(u'\ufeff', '')
    a_string = a_string.replace(u'\u2022', ":")
    re_ = re.compile(r"<([a-z][a-z0-9]*)\ [^>]*>", re.IGNORECASE)
    a_string = re_.sub('<\g<1>>', a_string, 0)
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
    a_string = re_script.sub('', a_string)
    re_a = re.compile("</?a.*?>")
    a_string = re_a.sub("", a_string)
    return a_string


def re_search(re_str, text, dotall=True):
    """
    抽取正则规则的第一组元素
    :param re_str:
    :param text:
    :param dotall:
    :return:
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    if not isinstance(re_str, list):
        re_str = [re_str]

    for rex in re_str:

        if dotall:
            match_obj = re.search(rex, text, re.DOTALL)
        else:
            match_obj = re.search(rex, text)

        if match_obj is not None:
            t = match_obj.group(1).replace('\n', '')
            return t

    return ""