# 分类项目子项目详细信息抓取工具

用于jay-cluster的spider主要分为三部分：
    1 parse函数：用于抓取分类链接中的所有item url 及所有下一页 url，并生成request用于item抓取及下一页抓取
    2 parse_item函数：用于抓取item的所有信息，包括标识号，标题，描述，图片，尺码，价格等信息，可以理解为所能获取到的全部信息
    3 parse_item_update函数：用于抓取更新字段，主要包涵价格， 运费等参数
以上三个函数均提供了公共实现，仅需要配置少量参数即可以实现抓取，下面分开介绍每个函数配置项的编写方法

parse函数：
    parse公共函数的主要功能介绍
    （1）在meta中记录seed
    （2）获取所有页面单商品Url并生成request
    （3）在meta中记录该链接是否为翻页链接
    （4）设置商品Url及翻页Url的回调函数
    （5）设定商品Url及翻页Url的优先级
    （6）获取翻页Url并生成request
     注：如要重写parse函数，请务必实现以上功能，具体实现方式请参见父类代码
     对于简单网站，即可以从分类页面中通过xpath直接获取单商品Url及翻页Url的网站，使用父类函数即可
     配置方法：
	（1）在constrant/page_xpath.py：PAGE_XPATH字典中，定义一组映射key(type=str):value(type=list)， spider_name:[page_xpath1，page_xpath2...]xpath可以定义多个，所得到的结果为所有xpath结果的总和
	（2）在constrant/item_field.py：ITEM_XPATH字典中，定义一组映射key(type=str):value(type=list)， spider_name:[item_xpath1，item_xpath2...]xpath可以定义多个，所得到的结果为所有xpath结果的总和
     对于不能直接用分类页面中能过xpath直接获取单商品Url及翻页Url的网站，可以在子类中重写parse函数，但务必实现上述6点功能
parse_item函数：
    parse_item公共函数的主要功能介绍
     （1）构造 item，为item赋初始化值
     （2）为item增加配置的字段
     （3）为特定网站去重复item
     （4）记录抓取的数量
     （5）增发请求抓取特定字段
      注：可以选择重写parse_item函数，但请务必实现（1）（3）（4）功能，具体实现方式请参见父类代理
      配置详解：
      在constrant/item_field.py:ITEM_FIELD字典中，定义一组映射key(type=str):value(type=dict)， spider_name:SPIDER_NAME_DICT
      SPIDER_NAME_DICT中定义三组映射key(type=str):value(type=list)：
      1 get:用于定义抓取需要使用的字段
      2 update:用于定义更新需要使用的字段（parse_item_update使用）
      3 common:用于定义更新和抓取都需要使用的字段
      字段定义在一个list中，每个字段为2元元组，结构如下：
      ('shipping_cost', { # 字段名
                "xpath": [ # 选择器名称，可以为xpath, re, css
                    '//*[@id="ourprice_shippingmessage"]/span/b/text()', # 选择器表达式
                    '//*[@id="ourprice_shippingmessage"]/span/text()',   # 可以有多条选择器表达式，从上往下执行
                    '//*[@id="saleprice_shippingmessage"]/span/b/text()',# 返回值经转换函数转换后不为空，则执行中止
                    '//*[@id="saleprice_shippingmessage"]/span/text()',  # 可以同时配置多种选择器
                    '//*[@id="olpTabContent"]//p[@class="olpShippingInfo"]//span[@class="a-color-secondary"]//text()', # 多种选择器执行顺序为re, xpath, css, 返回值经转换函数转换后不为空，则执行中止
                ],
                "function": lambda x, item: extract_shipping_cost_price_from_shipping_cost_string(xpath_exchange(x)), # 转换函数，将选择器的返回值做相应转换，最终得到所需要的数据类型，若得不到所需值，则返回空
		"extract": lambda item, response: image_urls_from(safely_json_loads(item["color_images"]))# 若经过上述步骤未获取所需值，则可以尝试从item中抽取
                "request_url": lambda item, response: urljoin(item['response_url'], ''.join(response.xpath('//div[@id="unqualifiedBuyBox"]/div/div[1]/a/@href').extract()).strip()) if item['availability'] == 'other' else None, # 若上述步骤未能得到所需值，则提供url做增发请求操作，用于在下一个页面中获取所需值，下一个页面抽取所需值的选择器及选择表达式可配置到已配置的表达式中，下一个页面使用的转换函数和抽取函数可以使用之前的函数，也可以单独配置，配置的名称为function_after以及extract_after，函数结构保持一致。
                "default": "$0" # 若上述步骤仍未获取到所需值，则提供默认值
            }),
	各函数的输入输出要素
        1）function: # 转换函数 若为没有此字串，则使用默认转换函数（见下一节）
	    param1:选择器选择结果
            param2:item（item字段，其中包含按顺序抽取完毕的字段值）
            return:字段写入数据库的值或空
        2）function_after: # 增发请求特定转换函数
           同上
        3）extract: # 抽取函数
            param1:item
            param2:response
            return:字段写入数据库的值或空
	4）extract_after: # 增发请求特定抽取函数
           同上
	5）request_url: # 增发请求url生成函数
	   param1:item
           param2:response
           return:增发请求url或空
        各函数执行顺序 function, extract, request_url, function[_after], extract[_after],任意函数只要返回了非空值，则执行中止，非空值作为最终值赋给item中的字段
parse_item_update函数:
parse_item公共函数的主要功能介绍
     （1）构造 item，为item赋初始化值
     （2）为item增加配置的字段
     （3）记录抓取的数量
     （4）增发请求抓取特定字段
     注：可以选择重写parse_item_update函数，但请务必实现（1）（2）（3）功能，具体实现方式请参见父类代理
      配置详解：与parse_item函数相同

function转换函数公共函数使用
以下4个公共函数适用于大多，直接在function中配置即可
1 function_xpath_common # 默认xpath转换函数
2 function_re_common # 默认re转换函数
3 format_html_xpath_common # 实现如下，对需要html_format的xpath结果进行转换
def format_html_xpath_common(x, item):
    return format_html_string(xpath_exchange(x))
4 safely_json_re_common # 实现如下，对需要safely_json_loads的re结果进行转换
def safely_json_re_common(x, item):
    return safely_json_loads(re_exchange(x).replace('&nbsp;', ''))




