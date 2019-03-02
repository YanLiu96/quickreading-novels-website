import datetime
# Some of the most used hash functions are: MD5: Message digest algorithm producing a 128 bit hash value. This is
# widely used to check data integrity. It is not suitable for use in other fields due to the security vulnerabilities
#  of MD5.

import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Blueprint
from sanic.response import html, json
from urllib.parse import parse_qs, unquote

from src.database.mongodb import MotorBase
from src.fetcher.function import get_time
from src.utils import get_real_answer
from src.config import CONFIG, LOGGER

try:
    from ujson import loads as json_loads
    from ujson import dumps as json_dumps
except:
    from json import loads as json_loads
    from json import dumps as json_dumps

operate_bp = Blueprint('operate_blueprint', url_prefix='operate')

# Replace sender@example.com with your "From" address.
# This address must be verified.
SENDER = '278899085@qq.com'
SENDERNAME = 'Yan Liu'

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
#RECIPIENT  = '352886335@qq.com'

# Replace smtp_username with your Amazon SES SMTP user name.
USERNAME_SMTP = "AKIAJIH6FB7JSFHH3RFQ"

# Replace smtp_password with your Amazon SES SMTP password.
PASSWORD_SMTP = "BJHpzXYnj9k74KyT3I9SJW7719f8h+zOSOxpAZNCJU0H"
# If you're using Amazon SES in an AWS Region other than 美国西部（俄勒冈）,
# replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
# endpoint in the appropriate region.
HOST = "email-smtp.eu-west-1.amazonaws.com"
PORT = 587

# The subject line of the email.
SUBJECT = 'Test for email'

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Yan Liu says\r\n"
             "SBSBSBSBSBSBSB "
             "Interface using the Python smtplib package."
            )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Liu Yan test email</h1>
  <p>This email was sent with Amazon SES using the
    <a href='https://www.python.org/'>Python</a>
    <a href='https://docs.python.org/3/library/smtplib.html'>
    smtplib</a> library.</p>
</body>
</html>
            """


@operate_bp.listener('before_server_start')
def setup_db(operate_bp, loop):
    global motor_base
    motor_base = MotorBase()


@operate_bp.listener('after_server_stop')
def close_connection(operate_bp, loop):
    motor_base = None


# jinjia2 config
env = Environment(
    loader=PackageLoader('views.operate_blueprint', '../templates/operate'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@operate_bp.route("/change_email", methods=['POST'])
async def change_email(request):
    """
    修改用户邮箱
    :param request:
    :return:
        :   -1  用户session失效  需要重新登录
        :   0   修改邮箱失败
        :   1   添加邮箱成功
    """
    user = request['session'].get('user', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    if user:
        try:
            email = data.get('email', None)[0]
            motor_db = motor_base.get_db()
            await motor_db.user.update_one({'user': user},
                                           {'$set': {'email': email}})
            LOGGER.info('email has been edited')
            return json({'status': 1})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})


@operate_bp.route("/change_pass", methods=['POST'])
async def change_pass(request):
    """
    修改用户密码
    :param request:
    :return:
        :   -1  用户session失效  需要重新登录
        :   0   修改密码失败
        :   1   添加密码成功
        :   -2  原始密码错误
    """
    user = request['session'].get('user', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    if user:
        try:
            new_pass = data.get('new_pass', None)[0]
            old_pass = data.get('old_pass', None)[0]
            motor_db = motor_base.get_db()
            user_data = await motor_db.user.find_one({'user': user})
            if user_data:
                pass_first = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + old_pass).encode("utf-8")).hexdigest()
                pass_second = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + new_pass).encode("utf-8")).hexdigest()
                new_password = hashlib.md5(pass_second.encode("utf-8")).hexdigest()
                password = hashlib.md5(pass_first.encode("utf-8")).hexdigest()
                if password == user_data.get('password'):
                    await motor_db.user.update_one({'user': user},
                                                   {'$set': {'password': new_password}})
                    LOGGER.info('password has benn changed')
                    return json({'status': 1})
                else:
                    return json({'status': -2})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})


@operate_bp.route("/login", methods=['POST'])
async def owllook_login(request):
    """
    用户登录
    :param request:
    :return:
        :   -1  用户名或密码不能为空
        :   0   用户名或密码错误
        :   1   登陆成功
    """
    login_data = parse_qs(str(request.body, encoding='utf-8'))
    user = login_data.get('user', [None])[0]
    pwd = login_data.get('pwd', [None])[0]
    if user and pwd:
        motor_db = motor_base.get_db()
        data = await motor_db.user.find_one({'user': user})
        if data:
            pass_first = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + pwd).encode("utf-8")).hexdigest()
            password = hashlib.md5(pass_first.encode("utf-8")).hexdigest()
            if password == data.get('password'):
                response = json({'status': 1})
                # 将session_id存于cokies
                date = datetime.datetime.now()
                response.cookies['owl_sid'] = request['session'].sid
                response.cookies['owl_sid']['expires'] = date + datetime.timedelta(days=30)
                response.cookies['owl_sid']['httponly'] = True
                # 此处设置存于服务器session的user值
                request['session']['user'] = user
                # response.cookies['user'] = user
                # response.cookies['user']['expires'] = date + datetime.timedelta(days=30)
                # response.cookies['user']['httponly'] = True
                # response = json({'status': 1})
                # response.cookies['user'] = user
                return response
            else:
                return json({'status': -2})
        return json({'status': -1})
    else:
        return json({'status': 0})


@operate_bp.route("/logout", methods=['GET'])
async def owllook_logout(request):
    """
    用户登出
    :param request:
    :return:
        :   0   退出失败
        :   1   退出成功
    """
    user = request['session'].get('user', None)
    if user:
        response = json({'status': 1})
        del response.cookies['user']
        del response.cookies['owl_sid']
        return response
    else:
        return json({'status': 0})


@operate_bp.route("/register", methods=['POST'])
async def owllook_register(request):
    """
    用户注册 不允许重名
    :param request:
    :return:
        :   -1  用户名已存在
        :   0   用户名或密码不能为空
        :   1   注册成功
    """
    register_data = parse_qs(str(request.body, encoding='utf-8'))
    user = register_data.get('user', [None])[0]
    pwd = register_data.get('pwd', [None])[0]
    Email = register_data.get('email', [None])[0]
    answer = register_data.get('answer', [None])[0]
    reg_index = request.cookies.get('reg_index')
    if user and pwd and Email and answer and reg_index and len(user) > 2 and len(pwd) > 5:
        motor_db = motor_base.get_db()
        is_exist = await motor_db.user.find_one({'user': user})
        if not is_exist:
            # 验证问题答案是否准确
            real_answer = get_real_answer(str(reg_index))
            if real_answer and real_answer == answer:
                pass_first = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + pwd).encode("utf-8")).hexdigest()
                password = hashlib.md5(pass_first.encode("utf-8")).hexdigest()
                time = get_time()
                data = {
                    "user": user,
                    "password": password,
                    "email": Email,
                    "register_time": time,
                }
                RECIPIENT = Email
                # Create message container - the correct MIME type is multipart/alternative.
                msg = MIMEMultipart('alternative')
                msg['Subject'] = SUBJECT
                msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                msg['To'] = RECIPIENT
                # Comment or delete the next line if you are not using a configuration set
                # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(BODY_TEXT, 'plain')
                part2 = MIMEText(BODY_HTML, 'html')

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)
                try:
                    server = smtplib.SMTP(HOST, PORT)
                    server.ehlo()
                    server.starttls()
                    # stmplib docs recommend calling ehlo() before & after starttls()
                    server.ehlo()
                    server.login(USERNAME_SMTP, PASSWORD_SMTP)
                    server.sendmail(SENDER, RECIPIENT, msg.as_string())
                    server.close()
                # Display an error message if something goes wrong.
                except Exception as e:
                    print("Error: ", e)
                else:
                    print("Email sent!")
                await motor_db.user.save(data)
                return json({'status': 1})
            else:
                return json({'status': -2})
        else:
            return json({'status': -1})
    else:
        return json({'status': 0})

    # post_data = json_loads(str(request.body, encoding='utf-8'))
    # pass_first = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + post_data['pwd']).encode("utf-8")).hexdigest()
    # password = hashlib.md5(pass_first.encode("utf-8")).hexdigest()
    # time = get_time()
    # data = {
    #     "user": post_data['user'],
    #     "password": password,
    #     "email": post_data['email'],
    #     "register_time": time,
    # }
    # motor_db = motor_base.get_db()
    # await motor_db.user.save(data)


@operate_bp.route("/add_bookmark", methods=['POST'])
async def owllook_add_bookmark(request):
    """
    添加书签
    :param request:
    :return:
        :   -1  用户session失效  需要重新登录
        :   0   添加书签失败
        :   1   添加书签成功
    """
    user = request['session'].get('user', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    bookmark_url = data.get('bookmark_url', '')
    if user and bookmark_url:
        url = unquote(bookmark_url[0])
        time = get_time()
        try:
            motor_db = motor_base.get_db()
            res = await motor_db.user_message.update_one({'user': user}, {'$set': {'last_update_time': time}},
                                                         upsert=True)
            if res:
                await motor_db.user_message.update_one(
                    {'user': user, 'bookmarks.bookmark': {'$ne': url}},
                    {'$push': {'bookmarks': {'bookmark': url, 'add_time': time}}})
                LOGGER.info('书签添加成功')
                return json({'status': 1})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})
