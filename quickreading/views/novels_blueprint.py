"""
Latest modified by Yan Liu at 2019.4.23 5：59
This file is the back-end of novels searching, search ranking, searching result, novels chapter page, content page
"""
import time

from jinja2 import Environment, PackageLoader, select_autoescape
from operator import itemgetter
from sanic import Blueprint
from sanic.response import redirect, html, text, json

from quickreading.database.mongodb import MotorBase
from quickreading.config import ENGINE_PRIORITY, CONFIG, LOGGER, RULES, REPLACE_RULES
from quickreading.crawler.function import get_time, get_netloc
from quickreading.crawler.novels_tools import get_novels_info
from quickreading.utils import ver_question
from quickreading.crawler.cache_novel_info import cache_novels_content, cache_novels_chapter, cache_search_ranking

novels_bp = Blueprint('novels_blueprint')
novels_bp.static('/static/novels', CONFIG.BASE_DIR + '/static/novels')


@novels_bp.listener('before_server_start')
def setup_db(novels_bp, loop):
    global motor_base
    motor_base = MotorBase()


@novels_bp.listener('after_server_stop')
def close_connection(novels_bp, loop):
    motor_base = None


# jinjia2 config
env = Environment(
    loader=PackageLoader('views.novels_blueprint', '../templates/novels'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@novels_bp.route("/")
async def index(request):
    """
    Index Page
    :param request:
    :return:
        index.html:
            is_login=0: User not login before(or session expired)
            is_login=1: User login before and not logout
            search_ranking: The top 25 searching rank novels' name
    """
    user = request['session'].get('user', None)
    # get novels name from search ranking cache(which update every 5 min)
    search_ranking = await cache_search_ranking()
    if user:
        motor_db = motor_base.get_db()
        data = await motor_db.user.find_one({'user': user})
        try:
            user_role = data.get("role", None)
            if user_role:
                return template('index.html', title='quick reading - search and enjoy', is_login=1, user=user,
                                user_role=user_role,
                                search_ranking=search_ranking[:25])
        except Exception as e:
            return template('index.html', title='quick reading - search and enjoy', is_login=0,
                            search_ranking=search_ranking[:25])
    else:
        return template('index.html', title='quick reading - search and enjoy', is_login=0,
                        search_ranking=search_ranking[:25])


@novels_bp.route("/register")
async def user_register(request):
    """
    Enter register page
    :param request: user name in session
    :return: register.html, question
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
                title='quick reading website - register - novels searching and reading website',
                question=ver_que_ans[1]
            )
        else:
            return redirect('/')


@novels_bp.route("/search", methods=['GET'])
async def quickreading_search(request):
    """
    Search Button
    :param request:novel's name
    :return:
        result.html: search result(original website link, chapter page link, Whether parsed or recommended)
        html("No result"): There is an error
    """
    start = time.time()
    # delete space in the beginning and the ending of input novel's name
    name = str(request.args.get('wd', '')).strip()
    novels_keyword = name.split(' ')[0]
    # use motor to manage mongodb
    motor_db = motor_base.get_db()
    if not name:
        return redirect('/')
    else:
        # store the search record
        try:
            await motor_db.search_records.update_one({'keyword': name}, {'$inc': {'count': 1}}, upsert=True)
        except Exception as e:
            LOGGER.exception(e)
    # Retrieve the search results through a search engine
    parse_result = None
    # choose different search engine to search novels
    if name.startswith('!baidu'):
        novels_keyword = name.split('baidu')[1].strip()
        novels_name = 'intitle:{name} 小说 阅读'.format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
    elif name.startswith('!360'):
        novels_keyword = name.split('360')[1].strip()
        novels_name = "{name} 小说 最新章节".format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='so', novels_name=novels_name)
    elif name.startswith('!bing'):
        novels_keyword = name.split('bing')[1].strip()
        novels_name = "{name} 小说 阅读 最新章节".format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='bing', novels_name=novels_name)
    elif name.startswith('!google'):
        novels_keyword = name.split('google')[1].strip()
        novels_name = "{name} 小说 阅读 最新章节".format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='google', novels_name=novels_name)
    else:
        for each_engine in ENGINE_PRIORITY:
            # for bing
            if each_engine == "bing":
                novels_name = "{name} 小说 阅读 最新章节".format(name=name)
                parse_result = await get_novels_info(class_name='bing', novels_name=novels_name)
                if parse_result:
                    break
            # for 360 so
            if each_engine == "360":
                novels_name = "{name} 小说 最新章节".format(name=name)
                parse_result = await get_novels_info(class_name='so', novels_name=novels_name)
                if parse_result:
                    break
            # for baidu
            if each_engine == "baidu":
                novels_name = 'intitle:{name} 小说 阅读'.format(name=name)
                parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
                if parse_result:
                    break
            if each_engine == "google":
                novels_name = '{name} 小说 阅读'.format(name=name)
                parse_result = await get_novels_info(class_name='google', novels_name=novels_name)
                if parse_result:
                    break
    if parse_result:
        # sort the search result (is_recommend, is_parse put first place)
        result_sorted = sorted(parse_result, reverse=True, key=itemgetter('is_recommend', 'is_parse', 'timestamp'))
        user = request['session'].get('user', None)
        if user:
            data = await motor_db.user.find_one({'user': user})
            user_role = data.get('role', None)
            try:
                time_now = get_time()
                # store search date
                res = await motor_db.user_message.update_one({'user': user},
                                                             {'$set': {'last_update_time': time_now}},
                                                             upsert=True)
                if res:
                    # store novels name and count(if searched before add one )
                    store_search_information = await motor_db.user_message.update_one(
                        {'user': user, 'search_records.keyword': {'$ne': novels_keyword}},
                        {'$push': {'search_records': {'keyword': novels_keyword, 'counts': 1}}},
                    )

                    if store_search_information:
                        await motor_db.user_message.update_one(
                            {'user': user, 'search_records.keyword': novels_keyword},
                            {'$inc': {'search_records.$.counts': 1}}
                        )
            except Exception as e:
                LOGGER.exception(e)
            return template(
                'result.html',
                is_login=1,
                user=user,
                user_role=user_role,
                name=novels_keyword,
                time='%.2f' % (time.time() - start),
                result=result_sorted,
                count=len(parse_result))
        else:
            return template(
                'result.html',
                is_login=0,
                name=novels_keyword,
                time='%.2f' % (time.time() - start),
                result=result_sorted,
                count=len(parse_result))

    else:
        return html("No Result!")


@novels_bp.route("/chapter")
async def chapter(request):
    """
    Chapter of novel
    :param request:
        url: the url of chapter page(url in quickreading )
        novels_name: the name of novel which is input by user
    :return:
        template: chapter.html
        content_url: element of generated chapter page url
    """
    # the request (url) contains search name and original website url.
    url = request.args.get('url', None)
    novels_name = request.args.get('novels_name', None)
    # resource website(domian name)
    netloc = get_netloc(url)
    if netloc not in RULES.keys():
        return redirect(url)
    if netloc in REPLACE_RULES.keys():
        url = url.replace(REPLACE_RULES[netloc]['old'], REPLACE_RULES[netloc]['new'])
    content_url = RULES[netloc].content_url
    content = await cache_novels_chapter(url=url, netloc=netloc)
    if content:
        # delete the js script and useless url
        content = str(content).strip('[],, Jjs').replace(', ', '').replace('onerror', '').replace('js', '').replace(
            '加入书架', '')
        return template(
            'chapter.html', novels_name=novels_name, url=url, content_url=content_url, soup=content)
    else:
        return text('Parse fail you can read in original page：{url}'.format(url=url))


@novels_bp.route("/quickreading_content")
async def quickreading_content(request):
    """
    Content of selected chapter
    :param request:
        url: resource content url
    :return:
        content_url: the url of selected chapter's content in this quickreading
    """
    url = request.args.get('url', None)
    chapter_url = request.args.get('chapter_url', None)
    novels_name = request.args.get('novels_name', None)
    name = request.args.get('name', '')
    is_ajax = request.args.get('is_ajax', '')
    # 当小说内容url不在解析规则内 跳转到原本url
    netloc = get_netloc(url)
    if netloc not in RULES.keys():
        return redirect(url)
    user = request['session'].get('user', None)
    motor_db = motor_base.get_db()
    # 拼接小说目录url
    book_url = "/chapter?url={chapter_url}&novels_name={novels_name}".format(
        chapter_url=chapter_url,
        novels_name=novels_name)
    motor_db = motor_base.get_db()
    if url == chapter_url:
        # 阅读到最后章节时候 在数据库中保存最新阅读章节
        if user and is_ajax == "quickReading_cache":
            quickReading_referer = request.headers.get('Referer', '').split('quickreading_content')[1]
            if quickReading_referer:
                latest_read = "/quickreading_content" + quickReading_referer
                await motor_db.user_message.update_one(
                    {'user': user, 'books_url.book_url': book_url},
                    {'$set': {'books_url.$.last_read_url': latest_read}})
        return redirect(book_url)
    content_url = RULES[netloc].content_url
    content_data = await cache_novels_content(url=url, netloc=netloc)
    if content_data:
        try:
            content = content_data.get('content', 'Failure to get')
            next_chapter = content_data.get('next_chapter', [])
            title = content_data.get('title', '').replace(novels_name, '')
            name = title if title else name
            # 拼接小说书签url
            bookmark_url = "{path}?url={url}&name={name}&chapter_url={chapter_url}&novels_name={novels_name}".format(
                path=request.path,
                url=url,
                name=name,
                chapter_url=chapter_url,
                novels_name=novels_name
            )
            # delete advertisement
            content = str(content).strip('[]Jjs,').replace('http', 'hs')
            if user:
                data = await motor_db.user.find_one({'user': user})
                user_role = data.get('role', None)
                bookmark = await motor_db.user_message.find_one({'user': user, 'bookmarks.bookmark': bookmark_url})
                book = await motor_db.user_message.find_one({'user': user, 'books_url.book_url': book_url})
                bookmark = 1 if bookmark else 0
                if book:
                    # hs exsitence
                    book = 1
                    # save latest reading history
                    if is_ajax == "quickReading_cache":
                        quickReading_referer = \
                            request.headers.get('Referer', bookmark_url).split('quickreading_content')[1]
                        latest_read = "/quickreading_content" + quickReading_referer
                        await motor_db.user_message.update_one(
                            {'user': user, 'books_url.book_url': book_url},
                            {'$set': {'books_url.$.last_read_url': latest_read}})
                else:
                    book = 0
                if is_ajax == "quickReading_cache":
                    quickReading_cache_dict = dict(
                        is_login=1,
                        user=user,
                        name=name,
                        url=url,
                        bookmark=bookmark,
                        book=book,
                        content_url=content_url,
                        chapter_url=chapter_url,
                        novels_name=novels_name,
                        next_chapter=next_chapter,
                        soup=content
                    )
                    return json(quickReading_cache_dict)
                return template(
                    'content.html',
                    is_login=1,
                    user=user,
                    user_role=user_role,
                    name=name,
                    url=url,
                    bookmark=bookmark,
                    book=book,
                    content_url=content_url,
                    chapter_url=chapter_url,
                    novels_name=novels_name,
                    next_chapter=next_chapter,
                    soup=content)
            else:
                if is_ajax == "quickReading_cache":
                    quickReading_cache_dict = dict(
                        is_login=0,
                        name=name,
                        url=url,
                        bookmark=0,
                        book=0,
                        content_url=content_url,
                        chapter_url=chapter_url,
                        novels_name=novels_name,
                        next_chapter=next_chapter,
                        soup=content
                    )
                    return json(quickReading_cache_dict)
                return template(
                    'content.html',
                    is_login=0,
                    name=name,
                    url=url,
                    bookmark=0,
                    book=0,
                    content_url=content_url,
                    chapter_url=chapter_url,
                    novels_name=novels_name,
                    next_chapter=next_chapter,
                    soup=content)
        except Exception as e:
            LOGGER.exception(e)
            return redirect(book_url)
    else:
        if user:
            is_login = 1
            user = user
            return template('parse_error.html', url=url, is_login=is_login, user=user)
        else:
            is_login = 0
            return template('parse_error.html', url=url, is_login=is_login)


@novels_bp.route('/admininterface')
async def admininterface(request):
    """
    Administrator interface
    :param request:
    :return:
        template: adminInterface.html
        is_admin: role is admin
    """
    admin = request['session'].get('user', None)
    role = request['session'].get('role', None)
    head = ['User name', 'email', 'role', 'delete']
    if admin:
        try:
            if role == 'Admin':
                motor_db = motor_base.get_db()
                keyword_cursor = motor_db.user.find(
                    {'role': {'$ne': 'Admin'}},
                    {'user': 1, 'email': 1, 'role': 1, '_id': 0})
                result = []
                indexs = 1
                async for document in keyword_cursor:
                    result.append({'user': document['user'], 'email': document['email'],
                                   'role': document['role'], 'index': indexs})
                    indexs += 1
                return template('adminInterface.html', title='QuickReading Admin Interface',
                                is_login=1, user=admin, alluser=result, user_role=role, is_admin=1, head=head)
            else:
                return redirect('/')
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        print("chucuo")
        return redirect('/')
