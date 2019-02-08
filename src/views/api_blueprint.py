#!/usr/bin/env python
from urllib.parse import unquote

from sanic import Blueprint

from src.fetcher.extract_novels import extract_chapters
from src.fetcher.function import get_time, get_netloc
from src.fetcher.novels_tools import get_novels_info
from src.fetcher import UniResponse, ResponseField
from src.fetcher.decorators import response_handle, authenticator

from src.config import LOGGER

api_bp = Blueprint('api_blueprint', url_prefix='api')


@api_bp.route("/owl_bd_novels/<name>")
@authenticator('QuickReading-Api-Key')
async def owl_bd_novels(request, name):
    """
    百度小说信息接口
    :param request:
    :param name: 小说名
    :return: 小说相关信息
    """
    name = unquote(name)
    novels_name = 'intitle:{name} 小说 阅读'.format(name=name)
    try:
        res = await get_novels_info(class_name='baidu', novels_name=novels_name)
        parse_result = []
        if res:
            parse_result = [i for i in res if i]
        UniResponse.SUCCESS.update({ResponseField.DATA: parse_result, ResponseField.FINISH_AT: get_time()})
        return response_handle(request, UniResponse.SUCCESS, 200)
    except Exception as e:
        LOGGER.exception(e)
        return response_handle(request, UniResponse.SERVER_UNKNOWN_ERR, 500)


@api_bp.route("/owl_so_novels/<name>")
@authenticator('QuickReading-Api-Key')
async def owl_so_novels(request, name):
    """
    360小说信息接口
    :param request:
    :param name: 小说名
    :return: 小说相关信息
    """
    name = unquote(name)
    novels_name = '{name} 小说 免费阅读'.format(name=name)
    try:
        res = await get_novels_info(class_name='baidu', novels_name=novels_name)
        parse_result = []
        if res:
            parse_result = [i for i in res if i]
        UniResponse.SUCCESS.update({ResponseField.DATA: parse_result, ResponseField.FINISH_AT: get_time()})
        return response_handle(request, UniResponse.SUCCESS, 200)
    except Exception as e:
        LOGGER.exception(e)
        return response_handle(request, UniResponse.SERVER_UNKNOWN_ERR, 500)
