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
from sanic.response import html, json, redirect
from urllib.parse import parse_qs, unquote
from datetime import datetime as dt, timedelta
from quickreading.database.mongodb import MotorBase
from quickreading.fetcher.function import get_time
from quickreading.utils import get_real_answer
from quickreading.config import CONFIG, LOGGER

try:
    from ujson import loads as json_loads
    from ujson import dumps as json_dumps
except:
    from json import loads as json_loads
    from json import dumps as json_dumps

operate_bp = Blueprint('operate_blueprint', url_prefix='operate')

# This address must be verified.
SENDER = 'quickreadingnovelswebsite@gmail.com'
SENDERNAME = 'Yan Liu'

# Amazon SES SMTP user name.
USERNAME_SMTP = "AKIAZFQQSWKGREV4YKVF"

# Amazon SES SMTP password.
PASSWORD_SMTP = "BJQu3MFe1a6d3cO1+8wiBbJ7nRdFa5nbC3G8+mGB4Bdx"

# endpoint in the appropriate region.
HOST = "email-smtp.eu-west-1.amazonaws.com"
PORT = 587

# The subject line of the email.
SUBJECT1 = 'Register successfully'
SUBJECT2 = 'Sorry you need to renew vip'
# The email body for recipients with non-HTML email clients.


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

'''
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
'''


@operate_bp.route("/login", methods=['POST'])
async def quickreading_login(request):
    """
    User Login
    :param request:
    :return:
        :   -1  User name or password is null
        :   0   Wrong user name or password
        :   1   Login successfully
    """
    login_data = parse_qs(str(request.body, encoding='utf-8'))
    user = login_data.get('user', [None])[0]
    pwd = login_data.get('pwd', [None])[0]

    if user and pwd:
        motor_db = motor_base.get_db()
        data = await motor_db.user.find_one({'user': user})
        if data:
            # add the token of website to password (application security)
            password_to_handle = hashlib.md5((CONFIG.WEBSITE["TOKEN"] + pwd).encode("utf-8")).hexdigest()
            password = hashlib.md5(password_to_handle.encode("utf-8")).hexdigest()
            # check whether a registered user(password is right)
            if password == data.get('password'):
                response = json({'status': 1})
                # Get the role of user
                user_role = data.get("role")
                user_email = data.get("email")
                # store session_id in cookies
                date = datetime.datetime.now()
                response.cookies['quickReading_cookie'] = request['session'].sid
                # Set the expires date of cookies: 30 days
                response.cookies['quickReading_cookie']['expires'] = date + datetime.timedelta(days=30)
                response.cookies['quickReading_cookie']['httponly'] = True
                # set server session
                # Store user name and role in the sessions
                request['session']['user'] = user
                request['session']['role'] = user_role
                # response.cookies['user']['expires'] = date + datetime.timedelta(days=30)
                #
                # check whether admin!
                if user_role == "Admin":
                    print("Admin Login")
                    return response
                else:
                    if user_role == "VIP User":
                        # 验证是否需要续费(定时发送邮件待实现)
                        expire_date = data.get("expireDate")
                        expire_date = dt.strptime(str(expire_date), "%Y-%m-%d %H:%M:%S")
                        date_now = dt.now()
                        rest_time = (expire_date - date_now).days
                        print(rest_time)
                        # **********************************************************
                        # whether user VIP service is almost over（2 days）send email
                        if rest_time > 0 & rest_time < 2:
                            if rest_time < 2 & rest_time > 0:
                                RECIPIENT = user_email
                                # Create message container - the correct MIME type is multipart/alternative.
                                msg = MIMEMultipart('alternative')
                                msg['Subject'] = SUBJECT2
                                msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                                msg['To'] = RECIPIENT
                                # Comment or delete the next line if you are not using a configuration set
                                # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

                                # Record the MIME types of both parts - text/plain and text/html.
                                part2 = MIMEText(renewLetter.format(User=user, day=rest_time), 'html')

                                # Attach parts into message container.
                                # According to RFC 2046, the last part of a multipart message, in this case
                                # the HTML message, is best and preferred.
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
                                return response
                        elif rest_time < 0:
                            await motor_db.user.update_one({'user': user}, {'$set': {'role': "General User"}},
                                                           upsert=True)
                            await motor_db.user.update_one({'user': user}, {'$unset': {'expireDate': 1}})
                            return response
                        else:
                            return response
                            # end of sending renew email function
                        return response
                return response
            else:
                return json({'status': -2})
        return json({'status': -1})
    else:
        return json({'status': 0})


@operate_bp.route("/logout", methods=['GET'])
async def quickreading_logout(request):
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
        del response.cookies['quickReading_cookie']
        return response
    else:
        return json({'status': 0})


@operate_bp.route("/register", methods=['POST'])
async def user_register(request):
    """
    User Register 不允许重名
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
                    "role": "General User"
                }
                RECIPIENT = Email
                # Create message container - the correct MIME type is multipart/alternative.
                msg = MIMEMultipart('alternative')
                msg['Subject'] = SUBJECT1
                msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                msg['To'] = RECIPIENT
                # Comment or delete the next line if you are not using a configuration set
                # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

                # Record the MIME types of both parts - text/plain and text/html.
                part2 = MIMEText(BODY_HTML.format(User=user), 'html')

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
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


@operate_bp.route("/add_bookmark", methods=['POST'])
async def quickreading_add_bookmark(request):
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


@operate_bp.route("/add_bookshelf", methods=['POST'])
async def quickreading_add_bookshelf(request):
    """
    添加书架
    :param request:
    :return:
        :   -1  用户session失效  需要重新登录
        :   0   添加书架失败
        :   1   添加书架成功
    """
    user = request['session'].get('user', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    novels_name = data.get('novels_name', '')
    chapter_url = data.get('chapter_url', '')
    last_read_url = data.get('last_read_url', '')
    if user and novels_name and chapter_url:
        url = "/chapter?url={chapter_url}&novels_name={novels_name}".format(chapter_url=chapter_url[0],
                                                                            novels_name=novels_name[0])
        time = get_time()
        try:
            motor_db = motor_base.get_db()
            res = await motor_db.user_message.update_one({'user': user}, {'$set': {'last_update_time': time}},
                                                         upsert=True)
            if res:
                await motor_db.user_message.update_one(
                    {'user': user, 'books_url.book_url': {'$ne': url}},
                    {'$push': {
                        'books_url': {'book_url': url, 'add_time': time, 'last_read_url': unquote(last_read_url[0])}}})
                LOGGER.info('You have added this page sucessfully in you bookshelf!')
                return json({'status': 1})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})


@operate_bp.route("/delete_book", methods=['POST'])
async def delete_book(request):
    """
    删除书架
    :param request:
    :return:
        :   -1  用户session失效  需要重新登录
        :   0   删除书架失败
        :   1   删除书架成功
    """
    user = request['session'].get('user', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    if user:
        if data.get('book_url', None):
            book_url = data.get('book_url', None)[0]
        else:
            novels_name = data.get('novels_name', '')
            chapter_url = data.get('chapter_url', '')
            book_url = "/chapter?url={chapter_url}&novels_name={novels_name}".format(chapter_url=chapter_url[0],
                                                                                     novels_name=novels_name[0])
        try:
            motor_db = motor_base.get_db()
            await motor_db.user_message.update_one({'user': user},
                                                   {'$pull': {'books_url': {"book_url": unquote(book_url)}}})
            LOGGER.info('You have deleted bookshelf')
            return json({'status': 1})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})


@operate_bp.route("/delete_user", methods=['POST'])
async def delete_user(request):
    user = request['session'].get('user', None)
    role = request['session'].get('role', None)
    data = parse_qs(str(request.body, encoding='utf-8'))
    motor_db = motor_base.get_db()
    if user and role == "Admin":
        if data.get('user_name', None):
            user_name_delete = data.get('user_name', None)[0]
        else:
            user_name_delete = data.get('user_name', '')
        try:
            await motor_db.user.delete_one({'user': user_name_delete})
            LOGGER.info('You have deleted the user')
            return json({'status': 1})
        except Exception as e:
            LOGGER.exception(e)
            return json({'status': 0})
    else:
        return json({'status': -1})


renewLetter = """
<html>
<head>
<style>
@page {{
    size: A4 portrait;
    margin: 70pt 60pt 70pt;

    @top-center {{
        /* Yes, you can use an image here - exactly like a background-image rule*/
        content: url(../images/headerlogos.png);

        /* and you can move it around 
        margin-top: 20pt;
        */
    }}

    @bottom-left {{
        content: string(footerContent);
        font: 9.85pt/150% 'Calibri', Arial, Tahoma, sans-serif;
    }}

    @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font: 9.85pt/150% 'Calibri', Arial, Tahoma, sans-serif;
    }}
}}

@media screen {{
  body {{
    font: 9.85pt/135% 'Cambria', serif;
  }}

  h1.footer-content {{
    line-height: 150%;
  }}

  header:after {{
      content: "";
      clear: both;
      display: table;
  }}

  header address, 
  header .date, 
  header .letter-reference {{
      text-align: right;
  }}

  /* Style any address like elements to be block */
  header address *, 
  header .date, 
  header .letter-reference,
  header > [class*="address-"] > span {{
      display: block;
  }}

  header address .email, 
  header .date, 
  header .letter-reference {{
      margin-top: 9.85pt;
  }}

  header address {{
      /* Two options here - if it's only got one side to it, don't bother floating it.
      width: 4.5cm;*/
      float: right;
      width: 100%;
      font-style: normal;
  }}

  /* This is what to change if the address is not visible in the window */
  header .address-recipient {{
      float: left;
      margin-top: -2cm;
  }}

  section main p:nth-child(2) {{
      font-weight: bold;
  }}


  .signature {{
      height: 50pt;
  }}

  .headerLogo, .footerLogo {{
      max-width: 6cm;
      height: auto;
      max-height: 2cm;
  }}

/* This gives the user an idea of what the page will look like prior to the print preview */
    *, *:before, *:after {{box-sizing: border-box;}}
    body {{
        background-color: #cecece;
    }}

    .wrapper {{
        width: 80%;
        max-width: 780px;
        margin: 0 auto;

    }}

    /* Each section is a letter */
    section {{
        display: flex;
        flex-direction: column;        
        background-color: white;
        background: linear-gradient(to bottom, white, white 29.66cm, #7e7e7e 29.66cm, #7e7e7e, 29.7cm, white 29.7cm, white);
        width: 21cm;
        min-height: 29.7cm;
        padding: 20px 30px 20px;
        margin: 10px 1%;
        box-shadow: 0 0 5px 5px #bababa;
    }}

    section footer {{
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }}

    /* Stick it to the bottom of the page no matter what - margin-top auto pushes it down. */
    section footer .pageFooter {{
        margin-top: auto;
    }}
}}

@media print {{
  .noPrint {{
    display: none;
  }}

  /* Force a page break after every section or w/e element you want. */
  section:not(:last-of-type) footer {{
      page-break-after: always;
      /* counter-reset: page pages; */
  }}

  .footer-content {{
      string-set: footerContent content();
      display: none;
  }}
}}

.penNote {{
  font-family: monospace;
  background-color: #fff699;
  width: 400px;
  padding: 10px;
  margin: 0 auto;
  box-shadow: 0 0 4px 4px #bbb;
}}
</style>
</head>
<body>
<div class="penNote noPrint">
<div class="wrapper">
    <div class="bglogo"></div>
    <h1 class="footer-content">Attention! Your membership is about to expire</h1>
    <!-- Each letter will be it's own section (this chapters in a book) -->
    <section>
        <header>
            <img class="headerLogo" alt="Company logo" quickreading="https://vignette.wikia.nocookie.net/jurassicpark/images/b/b0/Ingenicon3.png/revision/latest?cb=20141208195042" />
            <!--   The address element feels OK to use here as the HTML spec states:
            The address element represents the contact information for its nearest article or body element ancestor. As this is the sender's address it is relevant to the article. -->
            <p class="address-recipient">
                <span class="address-to"> Hello! Your membership is about to expire! </span>
            </p>
        </header>
        <main>
            <p>Dear {User}</p>
            <p>You only have {day} days VIP membership!</p>
            <p>If you still want to enjoy the vip service, please renew it!</p>
        </main>
        <footer>
            <p>Yours sincerely</p>
            <p class="signature">Signature</p>
            <p>Yan Liu</p>
            <p>Final Year Projects</p>
            <p>Novels Reading and Searching Website</p>
            <p>WIT Waterford Ireland</p>
            <p>X91 HXT3</p>
            <p>E-mail: 278899085@qq.com</p>
            <div class="pageFooter">
                <img class="footerLogo" quickreading="https://vignette.wikia.nocookie.net/jurassicpark/images/b/b0/Ingenicon3.png/revision/latest?cb=20141208195042" alt="Footer Logo" />
            </div>
        </footer>
    </section>
    <h1 class="pageBreak"></h1>
</div>
</body>
</html>
            """

BODY_HTML = """
<html>
<head>
<style>
@page {{
    size: A4 portrait;
    margin: 70pt 60pt 70pt;

    @top-center {{
        /* Yes, you can use an image here - exactly like a background-image rule*/
        content: url(../images/headerlogos.png);

        /* and you can move it around 
        margin-top: 20pt;
        */
    }}

    @bottom-left {{
        content: string(footerContent);
        font: 9.85pt/150% 'Calibri', Arial, Tahoma, sans-serif;
    }}

    @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font: 9.85pt/150% 'Calibri', Arial, Tahoma, sans-serif;
    }}
}}

@media screen {{
  body {{
    font: 9.85pt/135% 'Cambria', serif;
  }}

  h1.footer-content {{
    line-height: 150%;
  }}

  header:after {{
      content: "";
      clear: both;
      display: table;
  }}

  header address, 
  header .date, 
  header .letter-reference {{
      text-align: right;
  }}

  /* Style any address like elements to be block */
  header address *, 
  header .date, 
  header .letter-reference,
  header > [class*="address-"] > span {{
      display: block;
  }}

  header address .email, 
  header .date, 
  header .letter-reference {{
      margin-top: 9.85pt;
  }}

  header address {{
      /* Two options here - if it's only got one side to it, don't bother floating it.
      width: 4.5cm;*/
      float: right;
      width: 100%;
      font-style: normal;
  }}

  /* This is what to change if the address is not visible in the window */
  header .address-recipient {{
      float: left;
      margin-top: -2cm;
  }}

  section main p:nth-child(2) {{
      font-weight: bold;
  }}


  .signature {{
      height: 50pt;
  }}

  .headerLogo, .footerLogo {{
      max-width: 6cm;
      height: auto;
      max-height: 2cm;
  }}

/* This gives the user an idea of what the page will look like prior to the print preview */
    *, *:before, *:after {{box-sizing: border-box;}}
    body {{
        background-color: #cecece;
    }}

    .wrapper {{
        width: 80%;
        max-width: 780px;
        margin: 0 auto;

    }}

    /* Each section is a letter */
    section {{
        display: flex;
        flex-direction: column;        
        background-color: white;
        background: linear-gradient(to bottom, white, white 29.66cm, #7e7e7e 29.66cm, #7e7e7e, 29.7cm, white 29.7cm, white);
        width: 21cm;
        min-height: 29.7cm;
        padding: 20px 30px 20px;
        margin: 10px 1%;
        box-shadow: 0 0 5px 5px #bababa;
    }}

    section footer {{
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }}

    /* Stick it to the bottom of the page no matter what - margin-top auto pushes it down. */
    section footer .pageFooter {{
        margin-top: auto;
    }}
}}

@media print {{
  .noPrint {{
    display: none;
  }}

  /* Force a page break after every section or w/e element you want. */
  section:not(:last-of-type) footer {{
      page-break-after: always;
      /* counter-reset: page pages; */
  }}

  .footer-content {{
      string-set: footerContent content();
      display: none;
  }}
}}

.penNote {{
  font-family: monospace;
  background-color: #fff699;
  width: 400px;
  padding: 10px;
  margin: 0 auto;
  box-shadow: 0 0 4px 4px #bbb;
}}
</style>
</head>
<body>
<div class="penNote noPrint">
<div class="wrapper">
    <div class="bglogo"></div>
    <h1 class="footer-content">Welcome to be a member of quick reading website</h1>
    <!-- Each letter will be it's own section (this chapters in a book) -->
    <section>
        <header>
            <img class="headerLogo" alt="Company logo" quickreading="https://vignette.wikia.nocookie.net/jurassicpark/images/b/b0/Ingenicon3.png/revision/latest?cb=20141208195042" />
            <!--   The address element feels OK to use here as the HTML spec states:
            The address element represents the contact information for its nearest article or body element ancestor. As this is the sender's address it is relevant to the article. -->
            <p class="address-recipient">
                <span class="address-to"> Hello! Thank you for choosing us! </span>
            </p>
        </header>
        <main>
            <p>Dear {User}</p>
            <p>You have already register your account in our quick reading website. You can login and enjoy the reading</p>
        </main>
        <footer>
            <p>Yours sincerely</p>
            <p class="signature">Signature</p>
            <p>Yan Liu</p>
            <p>Final Year Projects</p>
            <p>Novels Reading and Searching Website</p>
            <p>WIT Waterford Ireland</p>
            <p>X91 HXT3</p>
            <p>E-mail: 278899085@qq.com</p>
            <div class="pageFooter">
                <img class="footerLogo" quickreading="https://vignette.wikia.nocookie.net/jurassicpark/images/b/b0/Ingenicon3.png/revision/latest?cb=20141208195042" alt="Footer Logo" />
            </div>
        </footer>
    </section>
    <h1 class="pageBreak"></h1>
</div>
</body>
</html>
            """
