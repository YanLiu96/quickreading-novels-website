import sys
import os
import pytest
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quickreading import server


@pytest.yield_fixture
def app():
    yield server.app


@pytest.fixture
def sanic_client(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.yield_fixture
def loop():
    loop = asyncio.get_event_loop()
    yield loop

# reference https://github.com/yunstanford/pytest-sanic/issues/3,
# https://github.com/howie6879/Sanic-For-Pythoneer/blob/master/docs/part1/8.%E6%B5%8B%E8%AF%95%E4%B8%8E%E9%83%A8%E7%BD%B2.md
# test novels blue_print


async def test_index_page(sanic_client):
    resp = await sanic_client.get('/')
    assert resp.status == 200


async def test_register_page(sanic_client):
    resp = await sanic_client.get('/register')
    assert resp.status == 200


async def test_search(sanic_client):
    resp = await sanic_client.get('/search')
    assert resp.status == 200


async def test_chapter_page(sanic_client):
    resp = await sanic_client.get('/chapter')
    assert resp.status == 500


async def admininterface(sanic_client):
    resp = await sanic_client.get('/admininterface')
    assert resp.status == 200
