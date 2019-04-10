#!/usr/bin/env python
import asyncio_redis

from quickreading.config import CONFIG


# Token from https://github.com/subyraman/sanic_session
# Reference https://sanic-session.readthedocs.io/en/latest/
class RedisSession:
    """
    A simple wrapper class that allows you to share a connection
    pool across your application.
    """
    _pool = None

    async def get_redis_pool(self):
        if not self._pool:
            REDIS_DICT = CONFIG.REDIS_DICT
            self._pool = await asyncio_redis.Pool.create(
                host=str(REDIS_DICT.get('REDIS_ENDPOINT', "localhost")), port=int(REDIS_DICT.get('REDIS_PORT', 6379)),
                poolsize=int(REDIS_DICT.get('POOLSIZE', 10)), password=REDIS_DICT.get('REDIS_PASSWORD', None),
                db=REDIS_DICT.get('SESSION_DB', None)
            )
        return self._pool
