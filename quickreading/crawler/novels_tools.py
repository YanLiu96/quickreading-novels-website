"""
 Created by Yan Liu at 2019/1/20.
"""

from importlib import import_module


async def get_novels_info(class_name, novels_name):
    novels_module = import_module(
        "quickreading.crawler.{}.{}_searchEngine_spider".format('searchEngine', class_name))
    novels_info = await novels_module.start(novels_name)
    return novels_info


if __name__ == '__main__':
    import asyncio
    import aiocache

    REDIS_DICT = {}
    aiocache.settings.set_defaults(
        class_="aiocache.RedisCache",
        endpoint=REDIS_DICT.get('REDIS_ENDPOINT', 'localhost'),
        port=REDIS_DICT.get('REDIS_PORT', 6379),
        db=REDIS_DICT.get('CACHE_DB', 0),
        password=REDIS_DICT.get('REDIS_PASSWORD', None),
    )

    res = asyncio.get_event_loop().run_until_complete(
        get_novels_info(class_name='baidu', novels_name='intitle:雪中悍刀行 小说 阅读'))
    print(res)
