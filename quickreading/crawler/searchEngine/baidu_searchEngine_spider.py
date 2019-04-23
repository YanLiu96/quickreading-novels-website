"""
 Created by Yan Liu at 2019.1.17.
"""
import aiohttp
import asyncio
import async_timeout
from aiocache.serializers import PickleSerializer
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from quickreading.crawler.decorators import cached
from quickreading.crawler.function import get_random_user_agent
from quickreading.crawler.searchEngine.base_searchEngine_spider import BaseSearchEngine


# implement methods in base class
class BaiduSearchEngine(BaseSearchEngine):
    def __init__(self):
        super(BaiduSearchEngine, self).__init__()

    async def data_extraction(self, html):
        try:
            # find the selector in baidu search result page
            url = html.select('h3.t a')[0].get('href', None)
            real_url = await self.get_real_url(url=url) if url else None
            if real_url:
                real_str_url = str(real_url)
                # get the netloc in the url(urlparse function in urllib can do it)
                netloc = urlparse(real_str_url).netloc
                if "http://" + netloc + "/" == real_str_url:
                    return None
                if 'baidu' in real_str_url or netloc in self.resource_domain:
                    return None
                is_parse = 1 if netloc in self.rules.keys() else 0
                title = html.select('h3.t a')[0].get_text()
                is_recommend = 1 if netloc in self.latest_rules.keys() else 0
                timestamp = 0
                time = ""
                return {'title': title, 'url': real_str_url.replace('index.html', ''), 'time': time,
                        'is_parse': is_parse,
                        'is_recommend': is_recommend,
                        'timestamp': timestamp,
                        'netloc': netloc}
            else:
                return None
        except Exception as e:
            self.logger.exception(e)
            return None

    # get the real url of search result
    async def get_real_url(self, url):
        with async_timeout.timeout(5):
            try:
                async with aiohttp.ClientSession() as client:
                    # In case of IP is blocked, use random user agent
                    headers = {'user-agent': await get_random_user_agent()}
                    async with client.head(url, headers=headers, allow_redirects=True) as response:
                        self.logger.info('Parse url: {}'.format(response.url))
                        url = response.url if response.url else None
                        # return the search result's url
                        return url
            except Exception as e:
                self.logger.exception(e)
                return None

    # search novels based on novels name
    async def novels_search(self, novels_name):
        url = self.config.URL_PC
        params = {'wd': novels_name, 'ie': 'utf-8', 'rn': self.config.BAIDU_RN, 'vf_bl': 1}
        headers = {'user-agent': await get_random_user_agent()}
        html = await self.fetch_url(url=url, params=params, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            result = soup.find_all(class_='result')
            extra_tasks = [self.data_extraction(html=i) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            res = [task.result() for task in done_list if task.result()]
            return res
        else:
            return []


# store the search novels' name
@cached(ttl=259200, key_from_attr='novels_name', serializer=PickleSerializer(), namespace="novels_name")
async def start(novels_name):
    """
    Start spider
    :return:
    """
    return await BaiduSearchEngine.start(novels_name)


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
    res = asyncio.get_event_loop().run_until_complete(start('intitle:雪中悍刀行 小说 阅读'))
    print(res)
