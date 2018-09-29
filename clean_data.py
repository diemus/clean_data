# encoding=utf-8
# 数据清洗
import re
from bs4 import BeautifulSoup, Comment
from html import unescape
from urllib.parse import urljoin


def clean_attrs(soup):
    # 清除所有标签的属性,[]表示删除所有属性,['scr']表示只保留src属性，None表示保留所有属性
    whitelist = {
        'a': ['href'],
        'img': ['src'],
    }
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            # 不在白名单的清除所有属性
            tag.attrs = {}
        else:
            # 在白名单的，遍历所有属性，只保留白名单里的属性
            allowed_attrs = whitelist[tag.name]
            new_attrs = {}
            if allowed_attrs is None:
                new_attrs = tag.attrs
            else:
                # 遍历所有属性，对指定属性进行保留
                for k, v in tag.attrs.items():
                    if k in allowed_attrs:
                        new_attrs[k] = v
            tag.attrs = new_attrs
    return soup


def clean_tags(soup):
    # 去除无用标签，只保留指定标签
    whitelist = ['p', 'br', 'div', 'strong', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th']
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.unwrap()
    return soup


def clean_extra(soup):
    # 清除不包含src链接的空img
    for tag in soup.find_all('img'):
        if 'src' not in tag.attrs:
            tag.decompose()

    # 清除js注释
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # 清除不包含任何内容的标签
    target_list = ['p', 'div']
    for tag in soup.find_all(target_list):
        if tag.string is None and not tag.contents:
            tag.decompose()

    return soup


def pre_clean(text):
    # 清除\n换行，防止干扰标签清洗
    text = re.sub(r'\n', '', text)
    return text


def clean_text(text):
    '''处理特殊的规则（注意：非通用规则请放在spider内处理）'''

    # 转换HTML特殊字符为unicode，比如&nbsp,\xa0等（bs4可以自动转换，暂时注释掉）
    # text = unescape(text)

    # 替换连续换行<br><br>为<br>
    text = re.sub(r'(<br/*>)+', '<br>', text)

    # 替<p>标签结尾换行<p>.......<br><p>
    text = re.sub(r'(<br/*>)+</p>', '</p>', text)

    # 清除空段落换行<p><br></p>
    text = re.sub(r'<p>(<br/*>)*</p>', '', text)

    # 清除空段落换行<div><br></div>
    text = re.sub(r'<div>(<br/*>)*</div>', '', text)

    # 清除空段落换行<p>\xa0</p>
    text = re.sub(r'<p>\s*</p>', '', text)

    # 清除空段落换行<div>\xa0</div>
    text = re.sub(r'<div>\s*</div>', '', text)
    return text


def join_url(soup, origin_url):
    # 对a/img标签中的相对地址链接进行还原
    for tag in soup.find_all(['img', 'a']):
        if 'src' in tag.attrs:
            tag['src'] = urljoin(origin_url, tag['src'])
        if 'href' in tag.attrs:
            tag['href'] = urljoin(origin_url, tag['href'])
    return soup


def clean_data(text, origin_url=None):
    # 文本预清洗
    text = pre_clean(text)

    # 标签清洗
    soup = BeautifulSoup(text, 'lxml')
    soup = clean_attrs(soup)
    soup = clean_tags(soup)
    soup = clean_extra(soup)
    # 对相对地址进行还原
    if origin_url:
        soup = join_url(soup, origin_url)

    # 转换为文本继续处理
    text = str(soup.extract())
    text = clean_text(text)
    return text


if __name__ == "__main__":
    # a = '"home&nbsp;-&nbsp;study\xa0"'
    a = '<img src="http://www.baiasdsadsadsadu.com">sdfdsffsd</img>'
    t = clean_data(a, 'http://www.baidu.com')
    print(t)
    # a = '"home&nbsp;-&nbsp;study\xa0"'
    # print(repr(clean(a)))
    # print(a)
    # print(repr(a))
