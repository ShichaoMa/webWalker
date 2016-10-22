import re
import json


def function_xpath_common(x, item):

    return xpath_exchange(x)


def format_html_xpath_common(x, item):

    return format_html_string(xpath_exchange(x))

def xpath_exchange(x):

    return "".join(x.extract()).strip()


def function_re_common(x, item):

    return re_exchange(x)


def safely_json_re_common(x, item):

    return safely_json_loads(re_exchange(x).replace('&nbsp;', ''))


def re_exchange(x):

    return "".join(x).strip()


def safely_json_loads(json_str):

    if not json_str:
        return {}
    else:
        return json.loads(json_str)


def format_html_string(a_string):

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

    if isinstance(re_str, (str, unicode)):
        re_str = [re_str]

    for rex in re_str:

        if dotall:
            match_obj = re.search(rex, text, re.DOTALL)
        else:
            match_obj = re.search(rex, text)

        if match_obj is not None:
            t = match_obj.group(1).replace('\n', '')
            t = t.replace("'", '"')
            return t

    return ""