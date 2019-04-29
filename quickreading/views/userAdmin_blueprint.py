from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Blueprint
from sanic.response import html, redirect
from quickreading.database.mongodb import MotorBase
from quickreading.crawler.cache_novel_info import get_the_latest_chapter
from quickreading.config import LOGGER, CONFIG

userAdmin_bp = Blueprint('userAdmin_blueprint', url_prefix='userAdmin')

userAdmin_bp.static('/static/novels', CONFIG.BASE_DIR + '/static/novels')


@userAdmin_bp.listener('before_server_start')
def setup_db(userAdmin_bp, loop):
    global motor_base
    motor_base = MotorBase()


@userAdmin_bp.listener('after_server_stop')
def close_connection(userAdmin_bp, loop):
    motor_base = None


# jinjia2 config
env = Environment(
    loader=PackageLoader('views.novels_blueprint', '../templates/novels'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@userAdmin_bp.route("/bookmarks")
async def bookmarks(request):
    user = request['session'].get('user', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            info = await motor_db.user.find_one({'user': user})
            role = info.get('role', None)
            if role == "VIP User" or role == "Admin":
                data = await motor_db.user_message.find_one({'user': user})
                if data:
                    # 获取所有书签
                    bookmarks = data.get('bookmarks', None)
                    if bookmarks:
                        result = []
                        for i in bookmarks:
                            item_result = {}
                            bookmark = i.get('bookmark', None)
                            query = parse_qs(urlparse(bookmark).query)
                            item_result['novels_name'] = query.get('novels_name', '')[0] if query.get('novels_name',
                                                                                                      '') else ''
                            item_result['chapter_name'] = query.get('name', '')[0] if query.get('name', '') else ''
                            item_result['chapter_url'] = query.get('chapter_url', '')[0] if query.get('chapter_url',
                                                                                                      '') else ''
                            item_result['bookmark'] = bookmark
                            item_result['add_time'] = i.get('add_time', '')
                            result.append(item_result)
                        return template('bookmark.html', title='the bookmarks of {user}'.format(user=user),
                                        is_login=1,
                                        user=user,
                                        user_role=role,
                                        is_bookmark=1,
                                        result=result[::-1])
                return template('bookmark.html', title='the bookmarks of {user}'.format(user=user),
                                is_login=1,
                                user=user,
                                user_role=role,
                                is_bookmark=0)
            else:
                return redirect('/pay')
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')
    else:
        return redirect('/')


@userAdmin_bp.route("/bookshelf")
async def bookshelf(request):
    user = request['session'].get('user', None)
    if user:
        motor_db = motor_base.get_db()
        data = await motor_db.user.find_one({'user': user})
        role = data.get('role', None)
        if role == "VIP User" or role == "Admin":
            try:
                data = await motor_db.user_message.find_one({'user': user})
                if data:
                    books_url = data.get('books_url', None)
                    if books_url:
                        result = []
                        for i in books_url:
                            item_result = {}
                            book_url = i.get('book_url', None)
                            last_read_url = i.get("last_read_url", "")
                            book_query = parse_qs(urlparse(book_url).query)
                            last_read_chapter_name = parse_qs(last_read_url).get('name', ['上次阅读'])[0]
                            item_result['novels_name'] = book_query.get('novels_name', '')[
                                0] if book_query.get(
                                'novels_name', '') else ''
                            item_result['book_url'] = book_url
                            latest_data = await motor_db.latest_chapter.find_one(
                                {'quickreading_chapter_url': book_url})
                            if latest_data:
                                item_result['latest_chapter_name'] = latest_data['data'][
                                    'latest_chapter_name']
                                item_result['quickreading_content_url'] = latest_data['data'][
                                    'quickreading_content_url']
                            else:
                                get_latest_data = await get_the_latest_chapter(book_url) or {}
                                item_result['latest_chapter_name'] = get_latest_data.get(
                                    'latest_chapter_name',
                                    '暂未获取，请反馈')
                                item_result['quickreading_content_url'] = get_latest_data.get(
                                    'quickreading_content_url', '')
                            item_result['add_time'] = i.get('add_time', '')
                            item_result["last_read_url"] = last_read_url if last_read_url else book_url
                            item_result["last_read_chapter_name"] = last_read_chapter_name
                            result.append(item_result)
                        return template('bookshelf.html',
                                        title='bookshelf of {user}'.format(user=user),
                                        is_login=1,
                                        user=user,
                                        user_role=role,
                                        is_bookmark=1,
                                        result=result[::-1])
                return template('bookshelf.html', title='bookshelf of {user}'.format(user=user),
                                is_login=1, user=user, user_role=role, is_bookmark=0)
            except Exception as e:
                LOGGER.error(e)
                return redirect('/')
        else:
            return redirect('/pay')
    else:
        return redirect('/')
