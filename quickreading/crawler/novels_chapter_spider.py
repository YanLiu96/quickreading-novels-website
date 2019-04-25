"""
 Created by Yan Liu at 2019/1/22.
"""

import re

from bs4 import BeautifulSoup
from collections import OrderedDict
from operator import itemgetter
from urllib.parse import urljoin, urlparse

from quickreading.config import LOGGER


def extract_chapters(chapters_url, html):
    """
    parse chapter page
    :param chapter_url: novels chapter url
    :param res: html of chapter
    :return:
    """
    # reference https://greasyfork.org/zh-CN/scripts/292-my-novel-reader and https://github.com/howie6879/owllook
    chapters_reg = r'(<a\s+.*?>.*第?\s*[一二两三四五六七八九十○零百千万亿0-9１２３４５６７８９０]{1,6}\s*[章回卷节折篇幕集].*?</a>)'
    # find all the chapter
    chapters_res = re.findall(chapters_reg, str(html), re.I)
    str_chapters_res = '\n'.join(chapters_res)
    chapters_res_soup = BeautifulSoup(str_chapters_res, 'html5lib')
    all_chapters = []
    # link
    for link in chapters_res_soup.find_all('a'):
        each_data = {}
        url = urljoin(chapters_url, link.get('href')) or ''
        name = link.text or ''
        each_data['chapter_url'] = url
        each_data['chapter_name'] = name
        each_data['index'] = int(urlparse(url).path.split('.')[0].split('/')[-1])
        all_chapters.append(each_data)
    chapters_sorted = sorted(all_chapters, reverse=True, key=itemgetter('index'))
    return chapters_sorted


def extract_pre_next_chapter(chapter_url, html):
    """
    Get the next chapter and pre chapter
    :param chapter_url:
    :param html:
    :return:
    """
    next_chapter = OrderedDict()
    try:
        # reference https://greasyfork.org/zh-CN/scripts/292-my-novel-reader
        next_reg = r'(<a\s+.*?>.*[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步].*?</a>)'
        judge_reg = r'[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步]'
        # parse again
        next_res = re.findall(next_reg, html.replace('<<', '').replace('>>', ''), re.I)
        str_next_res = '\n'.join(next_res)
        next_res_soup = BeautifulSoup(str_next_res, 'html5lib')
        for link in next_res_soup.find_all('a'):
            text = link.text or ''
            text = text.replace(' ', '')
            if novels_list(text):
                is_next = re.search(judge_reg, text)
                # is_ok = is_chapter(text)
                if is_next:
                    url = urljoin(chapter_url, link.get('href')) or ''
                    next_chapter[text[:5]] = url
        return next_chapter
    except Exception as e:
        LOGGER.exception(e)
        return next_chapter


def novels_list(text):
    rm_list = ['后一个', '天上掉下个']
    for i in rm_list:
        if i in text:
            return False
        else:
            continue
    return True
