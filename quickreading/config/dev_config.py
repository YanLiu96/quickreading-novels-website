"""
Create by Yan Liu 2019.1.18
"""
import os

from .config import Config


class DevConfig(Config):
    VAL_HOST = os.getenv('VAL_HOST', 'false')

    # Config mongodb and redis
    MONGODB = dict(
        MONGO_HOST=os.getenv('MONGO_HOST', ""),
        # The default port of mongodb is 27017
        MONGO_PORT=int(os.getenv('MONGO_PORT', 27017)),
        MONGO_USERNAME=os.getenv('MONGO_USERNAME', ""),
        MONGO_PASSWORD=os.getenv('MONGO_PASSWORD', ""),
        DATABASE='quickReading',
    )
    REDIS_DICT = dict(
        IS_CACHE=True,
        REDIS_ENDPOINT=os.getenv('REDIS_ENDPOINT', "localhost"),
        # The default port of redis is 6379
        REDIS_PORT=int(os.getenv('REDIS_PORT', 6379)),
        REDIS_PASSWORD=os.getenv('REDIS_PASSWORD', None),
        CACHE_DB=0,
        SESSION_DB=1,
        POOLSIZE=10,
    )

    # config website running and the token
    WEBSITE = dict(
        IS_RUNNING=os.getenv('QUICKREADING _IS_RUNNING', True),
        TOKEN=os.getenv('QUICKREADING_TOKEN', '')
    )
    '''
    AUTH = {
        "QuickReading-Api-Key": os.getenv('QUICKREADING_API_KEY', "your key")
    }
    '''
