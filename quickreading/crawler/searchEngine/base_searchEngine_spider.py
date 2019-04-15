"""
 Created by Yan Liu at 2019/1/17.
"""
import aiohttp
import async_timeout

from quickreading.config import CONFIG, LOGGER, RESOURCE_DOMAIN, RULES, LATEST_RULES


# Base class of search engine
class BaseSearchEngine:
    def __init__(self, logger=None):
        self.resource_domain = RESOURCE_DOMAIN
        self.config = CONFIG
        self.latest_rules = LATEST_RULES
        self.logger = logger if logger else LOGGER
        self.rules = RULES

    # get the search url of the search engine
    async def fetch_url(self, url, params, headers):
        with async_timeout.timeout(15):
            try:
                # Asynchronous HTTP client-To get something from the web:.
                #  reference: https://github.com/aio-libs/aiohttp
                async with aiohttp.ClientSession() as client:
                    async with client.get(url, params=params, headers=headers) as response:
                        assert response.status == 200
                        LOGGER.info('Task url: {}'.format(response.url))
                        try:
                            # get the source code of search result in search engine
                            text = await response.text()
                        except:
                            text = await response.read()
                        return text
            except Exception as e:
                LOGGER.exception(e)
                return None

    # class method must have a reference to a class object as the first parameter
    @classmethod
    async def start(cls, novels_name):
        return await cls().novels_search(novels_name)

    # get the information of novels
    async def data_extraction(self, html):
        raise NotImplementedError

    # search novels
    async def novels_search(self, novels_name):
        raise NotImplementedError
