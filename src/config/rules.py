"""
Created by Yan Liu at 2019.1.17
"""
from collections import namedtuple

# The resource website domain
RESOURCE_DOMAIN = ['WWW.biquge.com']
ENGINE_PRIORITY = ['360', 'baidu', 'google','bing', 'duck_go']
Rules = namedtuple('Rules', 'content_url chapter_selector content_selector')
RULES = {
    # demo  'name': Rules('content_url', {chapter_selector}, {content_selector})
    # content_url=1 表示章节链接使用本身自带的链接，不用拼接
    # content_url=0 表示章节网页需要当前页面url拼接
    # 'www.biqule.com': Rules('www.biqule.com', {'class': 'box_con'},{}),
    # 'www.lingdiankanshu.com': Rules('www.lingdiankanshu.com', {'class': 'box_con'}, {}),
    # 'www.hhlwx.com': Rules('www.hhlwx.co', {'class': 'chapterlist'},{}),
    # 已解析
    'www.biquge.com': Rules('http://www.biquge.com/', {'class': 'box_con'}, {'id': 'content'})
}