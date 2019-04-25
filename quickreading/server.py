#!/usr/bin/env python

import aiocache
import os
import sys

from sanic import Sanic
from sanic.response import html, redirect
from sanic_session import RedisSessionInterface

# build package path(otherwise can load the package i created)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Registering blueprints(to make server know this router and url routes)
from quickreading.views import novels_bp, operate_bp, payment_bp, userAdmin_bp, vip_service_bp
from quickreading.database.redies import RedisSession
from quickreading.config import LOGGER, CONFIG

app = Sanic(__name__)
# The routes of this project
app.blueprint(novels_bp)
app.blueprint(operate_bp)
app.blueprint(payment_bp)
app.blueprint(userAdmin_bp)
app.blueprint(vip_service_bp)


# Executed before the server begins to accept connections
@app.listener('before_server_start')
def init_cache(app, loop):
    LOGGER.info("Starting Aiocache : Asyncio Cache Manager For Redis")
    app.config.from_object(CONFIG)
    REDIS_DICT = CONFIG.REDIS_DICT
    # configuration: use aiocache to asyncio manager redis(the port)
    # reference https://github.com/argaen/aiocache
    aiocache.settings.set_defaults(
        class_="aiocache.RedisCache",
        endpoint=REDIS_DICT.get('REDIS_ENDPOINT', 'localhost'),
        port=REDIS_DICT.get('REDIS_PORT', 6379),
        db=REDIS_DICT.get('CACHE_DB', 0),
        password=REDIS_DICT.get('REDIS_PASSWORD', None),
        loop=loop,
    )
    LOGGER.info("Starting Redis")
    # start redis
    redis_session = RedisSession()
    # redis instance for this app
    app.get_redis_pool = redis_session.get_redis_pool
    # pass the getter method for the connection pool into the session
    app.session_interface = RedisSessionInterface(
        app.get_redis_pool, cookie_name="quickReading_cookie", expiry=30 * 24 * 60 * 60)


# two types of middleware: request and response
@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    host = request.headers.get('host', None)
    user_agent = request.headers.get('user-agent', None)
    if user_agent:
        user_ip = request.headers.get('X-Forwarded-For')
        LOGGER.info('user ip is: {}'.format(user_ip))
        if user_ip in CONFIG.FORBIDDEN:
            return html("<h3>The website is under maintenance</h3>")
        if CONFIG.VAL_HOST == 'true':
            if not host or host not in CONFIG.HOST:
                return redirect('http://www.quickreading.net')
        if CONFIG.WEBSITE['IS_RUNNING']:
            await app.session_interface.open(request)
        else:
            return html("<h3>The website is under maintenance</h3>")
    else:
        return html("<h3>The website is under maintenance</h3>")


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    # await app.session_interface.save(request, response)
    if request.path == '/operate/login' and request['session'].get('user', None):
        await app.session_interface.save(request, response)
        import datetime
        response.cookies['quickReading_cookie']['expires'] = datetime.datetime.now(
        ) + datetime.timedelta(days=30)
    elif request.path == '/register':
        try:
            response.cookies['reg_index'] = str(request['session']['index'][0])
        except KeyError as e:
            LOGGER.error(e)


# Set the address of the index page（0.0.0.0:8001）
if __name__ == "__main__":
    app.run(host="0.0.0.0", workers=2, port=8001, debug=CONFIG.DEBUG)
