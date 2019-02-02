import time

from jinja2 import Environment, PackageLoader, select_autoescape
from operator import itemgetter
from sanic import Blueprint
from sanic.response import redirect, html
from src.config import ENGINE_PRIORITY, CONFIG
from src.fetcher.novels_tools import get_novels_info
from src.utils import ver_question
novels_bp = Blueprint('novels_blueprint')
novels_bp.static('/static/novels', CONFIG.BASE_DIR + '/static/novels')


# jinjia2 config
env = Environment(
    loader=PackageLoader('views.novels_blueprint', '../templates/novels'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@novels_bp.route("/")
async def index(request):
    return template('index.html', title='quick reading - search and enjoy')


@novels_bp.route("/register")
async def owllook_register(request):
    """
    用户登录
    :param request:
    :return:
        :   -1  用户名或密码不能为空
        :   0   用户名或密码错误
        :   1   登陆成功
    """
    user = request['session'].get('user', None)
    if user:
        return redirect('/')
    else:
        ver_que_ans = ver_question()
        if ver_que_ans:
            request['session']['index'] = ver_que_ans
            return template(
                'register.html',
                title='quick reading websit - register - novels searching and reading website',
                question=ver_que_ans[1]
            )
        else:
            return redirect('/')


@novels_bp.route("/search", methods=['GET'])
async def owllook_search(request):
    start = time.time()
    name = str(request.args.get('wd', '')).strip()
    novels_keyword = name.split(' ')[0]

    # 通过搜索引擎获取检索结果
    parse_result = None
    if name.startswith('!baidu'):
        novels_keyword = name.split('baidu')[1].strip()
        novels_name = 'intitle:{name} 小说 阅读'.format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
    elif name.startswith('!bing'):
        novels_keyword = name.split('bing')[1].strip()
        novels_name = "{name} 小说 阅读 最新章节".format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='bing', novels_name=novels_name)
    else:
        for each_engine in ENGINE_PRIORITY:
            # for bing
            if each_engine == "bing":
                novels_name = "{name} 小说 阅读 最新章节".format(name=name)
                parse_result = await get_novels_info(class_name='bing', novels_name=novels_name)
                if parse_result:
                    break
            # for baidu
            if each_engine == "baidu":
                novels_name = 'intitle:{name} 小说 阅读'.format(name=name)
                parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
                if parse_result:
                    break
    if parse_result:
        # result_sorted = sorted(
        #     parse_result, reverse=True, key=lambda res: res['timestamp']) if ':baidu' not in name else parse_result
        # 优先依靠是否解析进行排序  其次以更新时间进行排序
        result_sorted = sorted(
            parse_result,
            reverse=True,
            key=itemgetter('is_recommend', 'is_parse', 'timestamp'))
        return template(
            'result.html',
            is_login=0,
            name=novels_keyword,
            time='%.2f' % (time.time() - start),
            result=result_sorted,
            count=len(parse_result))
    else:
        return html("No Result！请将小说名反馈给本站，谢谢！")

