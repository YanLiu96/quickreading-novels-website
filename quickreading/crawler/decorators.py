"""
 Created by Yan Liu at 2019/2/2.
"""
from sanic import response
from aiocache.log import logger
from aiocache.utils import get_args_dict, get_cache
from sanic.request import Request

try:
    from ujson import loads as json_loads
    from ujson import dumps as json_dumps
except:
    from json import loads as json_loads
    from json import dumps as json_dumps


# Token from https://github.com/argaen/aiocache/blob/master/aiocache/decorators.py
# Reference https://github.com/argaen/aiocache
def cached(ttl=0, key=None, key_from_attr=None, cache=None, serializer=None, plugins=None, **kwargs):
    cache_kwargs = kwargs

    def cached_decorator(func):
        async def wrapper(*args, **kwargs):
            cache_instance = get_cache(
                cache=cache, serializer=serializer, plugins=plugins, **cache_kwargs)
            args_dict = get_args_dict(func, args, kwargs)
            cache_key = key or args_dict.get(
                key_from_attr,
                (func.__module__ or 'stub') + func.__name__ + str(args) + str(kwargs))
            try:
                if await cache_instance.exists(cache_key):
                    return await cache_instance.get(cache_key)
            except Exception:
                logger.exception("Unexpected error with %s", cache_instance)
            result = await func(*args, **kwargs)
            if result:
                try:
                    await cache_instance.set(cache_key, result, ttl=ttl)
                except Exception:
                    logger.exception("Unexpected error with %s", cache_instance)
            return result
        return wrapper
    return cached_decorator


def response_handle(request, dict_value, status=200):
    """
    Return sanic.response or json depending on the request
    :param request: sanic.request.Request or dict
    :param dict_value:
    :return:
    """
    if isinstance(request, Request):
        return response.json(dict_value, status=status)
    else:
        return json_dumps(dict_value, ensure_ascii=False)
