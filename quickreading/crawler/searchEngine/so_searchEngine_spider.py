#!/usr/bin/env python
"""
 Created by Yan Liu at 2019/2/2.
"""
import asyncio
from aiocache.serializers import PickleSerializer
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from quickreading.crawler.decorators import cached
from quickreading.crawler.function import get_random_user_agent
from quickreading.crawler.searchEngine.base_searchEngine_spider import BaseSearchEngine


class SoSearchEngine(BaseSearchEngine):
    def __init__(self):
        super(SoSearchEngine, self).__init__()

    async def novels_search(self, novels_name):
        # The url of search engine
        url = self.config.SO_URL
        headers = {
            'User-Agent': await get_random_user_agent(),
            'Referer': "http://www.so.com/haosou.html?quickreading=home"
        }
        # set the params in the search (request) url
        params = {'ie': 'utf-8', 'quickreading': 'noscript_home', 'shb': 1, 'q': novels_name, }
        # the source code in search result page(360 search result)
        html = await self.fetch_url(url=url, params=params, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            # find the novels related information(title, original link) which in res-list
            result = soup.find_all(class_='res-list')
            extra_tasks = [self.data_extraction(html=i) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            # get the title, original url, time, whether parsed or recommend, netloc
            res = [task.result() for task in done_list if task.result()]
            return res
        else:
            return []

    async def data_extraction(self, html):
        try:
            try:
                title = html.select('h3 a')[0].get_text()
                url = html.select('h3 a')[0].get('href', None)
            except Exception as e:
                self.logger.exception(e)
                return None
            if "www.so.com/link?m=" in url:
                url = html.select('h3 a')[0].get('data-url', None)
            if "www.so.com/link?url=" in url:
                url = parse_qs(urlparse(url).query).get('url', None)
                url = url[0] if url else None
            netloc = urlparse(url).netloc
            if not url or 'baidu' in url or 'baike.so.com' in url or netloc in self.resource_domain:
                return None
            # if the domain in the rule (which has been parsed)
            is_parse = 1 if netloc in self.rules.keys() else 0
            is_recommend = 1 if netloc in self.latest_rules.keys() else 0
            time = ''
            timestamp = 0
            return {'title': title, 'url': url.replace('index.html', '').replace('Index.html', ''), 'time': time,
                    'is_parse': is_parse,
                    'is_recommend': is_recommend,
                    'timestamp': timestamp,
                    'netloc': netloc}
        except Exception as e:
            self.logger.exception(e)
            return None


@cached(ttl=259200, key_from_attr='novels_name', serializer=PickleSerializer(), namespace="novels_name")
async def start(novels_name):
    """
    Start spider
    :return:
    """
    return await SoSearchEngine.start(novels_name)


if __name__ == '__main__':
    # Start
    import aiocache

    REDIS_DICT = {}
    aiocache.settings.set_defaults(
        class_="aiocache.RedisCache",
        endpoint=REDIS_DICT.get('REDIS_ENDPOINT', 'localhost'),
        port=REDIS_DICT.get('REDIS_PORT', 6379),
        db=REDIS_DICT.get('CACHE_DB', 0),
        password=REDIS_DICT.get('REDIS_PASSWORD', None),
    )
    '''
    res = asyncio.get_event_loop().run_until_complete(start('雪中悍刀行 小说 最新章节'))
    print(res)
    '''
