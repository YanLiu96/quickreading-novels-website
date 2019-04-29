"""
Latest modified by Yan Liu at 2019.4.15 20：47
This file is the back-end of user login, logout, register, add or delete bookmark and bookshelf
"""
from sanic import Blueprint
from sanic.response import json, html, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
from quickreading.database.mongodb import MotorBase
from quickreading.crawler.function import get_time
import paypalrestsdk
from quickreading.config import LOGGER, CONFIG
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
from datetime import datetime, timedelta

payment_bp = Blueprint('payment_blueprint')
payment_bp.static('/static/payment', CONFIG.BASE_DIR + '/static/payment')

SENDER = 'quickreadingnovelswebsite@gmail.com'
SENDERNAME = 'Yan Liu'

# reference amazon office document
# Amazon SES SMTP user name.
USERNAME_SMTP = "AKIAZFQQSWKGREV4YKVF"
# Amazon SES SMTP password.
PASSWORD_SMTP = "BJQu3MFe1a6d3cO1+8wiBbJ7nRdFa5nbC3G8+mGB4Bdx"
HOST = "email-smtp.eu-west-1.amazonaws.com"
PORT = 587

# The subject line of the email.
SUBJECT1 = 'Becoming VIP successfully'
SUBJECT2 = 'Renew VIP successfully'

# pay pal rest sdk configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": "AaF3e62lDn44mSmuWdc9g4jLwyWVkow22M24mHMak57LzGM76BJ1AUCdkJu3XDR342U8eo5ldkaHY998",
    "client_secret": "EFb9ipDk_i7UbtnODGGlXbBinYtRABcIaZWAKFQ-4Mqvs_Dd0Iv3Qb0eHYHpbd9c1JYmOtw9gnVZr6ux"})

env = Environment(
    loader=PackageLoader('views.payment_blueprint', '../templates/payment'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


@payment_bp.listener('before_server_start')
def setup_db(payment_bp, loop):
    global motor_base
    motor_base = MotorBase()


@payment_bp.listener('after_server_stop')
def close_connection(payment_bp, loop):
    motor_base = None


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@payment_bp.route('/pay')
async def pay(request):
    """
    Payment page (based on different roles)
    :param request: payment.html
    :return:
        is_VIP: role is Vip user
        is_admin: role is Admin
    """
    user = request['session'].get('user', None)
    if user:
        motor_db = motor_base.get_db()
        user_data = await motor_db.user.find_one({'user': user})
        user_role = user_data.get('role', None)
        if user_role == 'Admin':
            return template('payment.html', is_login=1, is_admin=1)
        elif user_role == 'VIP User':
            expire_date = user_data.get('expireDate', None)
            return template('payment.html', is_login=1, is_VIP=1, expire_date=expire_date)
        else:
            return template('payment.html', is_login=1)
    else:
        return redirect('/')


@payment_bp.route('/payOneMonth', methods=['POST'])
async def payment(request):
    """
    Pay for one month vip service
    :param request:
    :return:
        paymentID: the payment id (payment create successfully)
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/payOneMonth/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "One month vip",
                    "sku": "item",
                    "price": "0.1",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "0.1",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("One Month Service Payment created successfully")
    else:
        # the error of creating payment
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@payment_bp.route('/paySixMonth', methods=['POST'])
async def payment(request):
    """
    Pay for six month vip service
    :param request:
    :return:
            paymentID: the payment id (payment create successfully)
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/paySixMonth/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "0.2",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "0.2",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("Six Month ServicePayment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@payment_bp.route('/payOneYear', methods=['POST'])
async def payment(request):
    """
    Pay for one year vip service
    :param request:
    :return:
        paymentID: the payment id (payment create successfully)
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/payOneYear/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "0.3",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "0.3",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("One Year Service Payment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@payment_bp.route('/executeOneMonth', methods=['POST'])
async def execute(request):
    """
    Execute one month vip service payment
    :param request:
        payerID: the pay's id of the payment
    :return:
        success: The payment is successful and the transaction is completed
    """
    success = False
    payment = paypalrestsdk.Payment.find(request.form.get('paymentID'))
    if payment.execute({'payer_id': request.form.get('payerID')}):
        print('Execute success!')
        success = True
        user = request['session'].get('user', None)
        motor_db = motor_base.get_db()
        user_data = await motor_db.user.find_one({'user': user})
        user_role = user_data.get("role")
        if user:
            # if user is general user
            if user_role == "General User":
                try:
                    become_vip_time = get_time()
                    res = await motor_db.user.update_one({'user': user}, {'$set': {'become_vip_time': become_vip_time}},
                                                         upsert=True)
                    if res:
                        date_vip = datetime.strptime(str(become_vip_time), "%Y-%m-%d %H:%M:%S")
                        new_expire_date = (date_vip + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                        await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}},
                                                       upsert=True)
                        await motor_db.user.update_one({'user': user}, {'$set': {'role': "VIP User"}}, upsert=True)
                        request['session']['role'] = "VIP User"
                        LOGGER.info('VIP information have store in database ')
                        # send Successful payment mail
                        user_information = await motor_db.user.find_one({'user': user})
                        user_email = user_information.get("email")
                        try:
                            # send email
                            RECIPIENT = user_email
                            # Create message container - the correct MIME type is multipart/alternative.
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = SUBJECT1
                            msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                            msg['To'] = RECIPIENT
                            part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="paid 30 days"), 'html')
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
                                print("Payment Email sent successfully!")
                        except Exception as e3:
                            print("Error: ", e3)

                    else:
                        return json({"Do not store  in database"})
                except Exception as e:
                    LOGGER.exception(e)
            elif user_role == "VIP User":
                try:
                    motor_db = motor_base.get_db()
                    user_information = await motor_db.user.find_one({'user': user})
                    user_email = user_information.get("email")

                    old_expire_date1 = user_information.get("expireDate")
                    old_expire_date2 = datetime.strptime(str(old_expire_date1), "%Y-%m-%d %H:%M:%S")
                    new_expire_date = (old_expire_date2 + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                    await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}},
                                                   upsert=True)
                    LOGGER.info('VIP Service has been renewed')
                    # send Successful renew mail
                    try:
                        # send email
                        RECIPIENT = user_email
                        # Create message container - the correct MIME type is multipart/alternative.
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = SUBJECT2
                        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                        msg['To'] = RECIPIENT
                        # Comment or delete the next line if you are not using a configuration set
                        # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

                        # Record the MIME types of both parts - text/plain and text/html.
                        part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="renew 30 days"), 'html')

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
                            print("Payment Email sent successfully!")
                    except Exception as e3:
                        print("Error: ", e3)
                except Exception as e:
                    LOGGER.exception(e)

        else:
            return json({"Do not have this user in database"})
    else:
        print(payment.error)
    return json({'success': success})


@payment_bp.route('/executeSixMonth', methods=['POST'])
async def execute(request):
    """
    Execute six month vip service payment
    :param request:
        payerID: the pay's id of the payment
    :return:
        success: The payment is successful and the transaction is completed
    """
    success = False
    payment = paypalrestsdk.Payment.find(request.form.get('paymentID'))
    if payment.execute({'payer_id': request.form.get('payerID')}):
        print('Execute success!')
        success = True
        user = request['session'].get('user', None)
        motor_db = motor_base.get_db()
        user_data = await motor_db.user.find_one({'user': user})
        user_role = user_data.get("role")
        if user:
            if user_role == "General User":
                try:
                    become_vip_time = get_time()
                    motor_db = motor_base.get_db()
                    res = await motor_db.user.update_one({'user': user}, {'$set': {'become_vip_time': become_vip_time}},
                                                         upsert=True)
                    if res:
                        date_vip = datetime.strptime(str(become_vip_time), "%Y-%m-%d %H:%M:%S")
                        new_expire_date = (date_vip + timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
                        await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}},
                                                       upsert=True)
                        await motor_db.user.update_one({'user': user}, {'$set': {'role': "VIP User"}}, upsert=True)
                        request['session']['role'] = "VIP User"
                        print("the role is :")
                        print()
                        LOGGER.info('VIP information have store in database ')
                        # send Successful payment mail
                        user_information = await motor_db.user.find_one({'user': user})
                        user_email = user_information.get("email")
                        try:
                            # send email
                            RECIPIENT = user_email
                            # Create message container - the correct MIME type is multipart/alternative.
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = SUBJECT1
                            msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                            msg['To'] = RECIPIENT
                            part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="paid six months "), 'html')
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
                                print("Payment Email sent successfully!")
                        except Exception as e3:
                            print("Error: ", e3)

                    else:
                        return json({"Do not store  in database"})
                except Exception as e:
                    LOGGER.exception(e)

            elif user_role == "VIP User":
                try:
                    motor_db = motor_base.get_db()
                    user_information = await motor_db.user.find_one({'user': user})
                    user_email = user_information.get("email")
                    old_expire_date1 = user_information.get("expireDate")
                    old_expire_date2 = datetime.strptime(str(old_expire_date1), "%Y-%m-%d %H:%M:%S")
                    new_expire_date = (old_expire_date2 + timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
                    await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}}
                                                   , upsert=True)
                    LOGGER.info('VIP Service has been renewed')
                    # send Successful renew mail
                    try:
                        # send email
                        RECIPIENT = user_email
                        # Create message container - the correct MIME type is multipart/alternative.
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = SUBJECT2
                        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                        msg['To'] = RECIPIENT
                        # Comment or delete the next line if you are not using a configuration set
                        # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

                        # Record the MIME types of both parts - text/plain and text/html.
                        part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="renew six months")
                                         , 'html')

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
                            print("Payment Email sent successfully!")
                    except Exception as e3:
                        print("Error: ", e3)
                except Exception as e:
                    LOGGER.exception(e)

        else:
            return json({"Do not have this user in database"})
    else:
        print(payment.error)
    return json({'success': success})


@payment_bp.route('/executeOneYear', methods=['POST'])
async def execute(request):
    """
    Execute one year vip service payment
    :param request:
        payerID: the pay's id of the payment
    :return:
        success: The payment is successful and the transaction is completed
    """
    success = False
    payment = paypalrestsdk.Payment.find(request.form.get('paymentID'))
    if payment.execute({'payer_id': request.form.get('payerID')}):
        print('Execute success!')
        success = True
        user = request['session'].get('user', None)
        motor_db = motor_base.get_db()
        user_data = await motor_db.user.find_one({'user': user})
        user_role = user_data.get("role")
        if user:
            if user_role == "General User":
                try:
                    become_vip_time = get_time()
                    motor_db = motor_base.get_db()
                    res = await motor_db.user.update_one({'user': user}, {'$set': {'become_vip_time': become_vip_time}},
                                                         upsert=True)
                    if res:
                        date_vip = datetime.strptime(str(become_vip_time), "%Y-%m-%d %H:%M:%S")
                        new_expire_date = (date_vip + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
                        await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}},
                                                       upsert=True)
                        await motor_db.user.update_one({'user': user}, {'$set': {'role': "VIP User"}}, upsert=True)
                        # very important
                        request['session']['role'] = "VIP User"
                        LOGGER.info('VIP information have store in database ')
                        # send Successful payment mail
                        user_information = await motor_db.user.find_one({'user': user})
                        user_email = user_information.get("email")
                        try:
                            # send email
                            RECIPIENT = user_email
                            # Create message container - the correct MIME type is multipart/alternative.
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = SUBJECT1
                            msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                            msg['To'] = RECIPIENT
                            part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="paid one year"), 'html')
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
                                print("Payment Email sent successfully!")
                        except Exception as e3:
                            print("Error: ", e3)

                    else:
                        return json({"Do not store  in database"})
                except Exception as e:
                    LOGGER.exception(e)

            elif user_role == "VIP User":
                try:
                    motor_db = motor_base.get_db()
                    user_information = await motor_db.user.find_one({'user': user})
                    user_email = user_information.get("email")
                    old_expire_date1 = user_information.get("expireDate")
                    old_expire_date2 = datetime.strptime(str(old_expire_date1), "%Y-%m-%d %H:%M:%S")
                    new_expire_date = (old_expire_date2 + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
                    await motor_db.user.update_one({'user': user}, {'$set': {'expireDate': new_expire_date}},
                                                   upsert=True)
                    LOGGER.info('One Year VIP Service has been renewed')
                    # send Successful renew mail
                    try:
                        # send email
                        RECIPIENT = user_email
                        # Create message container - the correct MIME type is multipart/alternative.
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = SUBJECT2
                        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                        msg['To'] = RECIPIENT
                        part2 = MIMEText(BODY_HTML.format(Usernamefor=user, message="renew one year"), 'html')
                        # Attach parts into message container.
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
                            print("Payment Email sent successfully!")
                    except Exception as e3:
                        print("Error: ", e3)
                except Exception as e:
                    LOGGER.exception(e)

        else:
            return json({"Do not have this user in database"})
    else:
        print(payment.error)
    return json({'success': success})


@payment_bp.route("/user/personal/info")
async def get_personal_information(request):
    """
    Get the user's information
    :param request: user name (session)
    :return: userInformation.html based on different roles
    """
    user = request['session'].get('user', None)
    # role = request['session'].get('role', None)
    if user:
        try:
            motor_db = motor_base.get_db()
            user_information = await motor_db.user.find_one({'user': user})
            user_role = user_information.get('role')
            user_name = user_information.get("user")
            user_emial = user_information.get("email")
            register_time = user_information.get("register_time")

            item_result = {}
            result = []
            item_result['userName'] = user_name
            item_result['userEmial'] = user_emial
            item_result['role'] = user_role
            item_result['register_time'] = register_time

            if user_role == 'Admin':
                result.append(item_result)
                message = "Honorable administrator"
                item_result['admin_message'] = message
                return template('userInformation.html',
                                title='Admin information',
                                is_login=1,
                                user=user,
                                result=result, role=user_role)
            elif user_role == "VIP User":
                user_become_vip_time = user_information.get("become_vip_time")
                use_expire_date = user_information.get("expireDate")
                item_result['user_become_vip_time'] = user_become_vip_time
                item_result['expireDate'] = use_expire_date
                result.append(item_result)
                return template('userInformation.html',
                                title='VIP user information',
                                is_login=1,
                                user=user,
                                result=result, role=user_role)

            else:
                warning_message = "Sorry,you are not VIP!"
                item_result['warning_message'] = warning_message
                result.append(item_result)
                return template('userInformation.html',
                                title='General user information',
                                is_login=1,
                                user=user,
                                result=result, role=user_role)
        except Exception as e:
            LOGGER.error(e)
            return redirect('/')


# The HTML body of the email. referce: https://realpython.com/python-send-email/#including-html-content
BODY_HTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width" />
  <style>
    #outlook a {{ 
      padding:0; 
    }} 

    body{{ 
      width:100% !important; 
      min-width: 100%;
      -webkit-text-size-adjust:100%; 
      -ms-text-size-adjust:100%; 
      margin:0; 
      padding:0;
    }}

    .ExternalClass {{ 
      width:100%;
    }} 

    .ExternalClass, 
    .ExternalClass p, 
    .ExternalClass span, 
    .ExternalClass font, 
    .ExternalClass td, 
    .ExternalClass div {{ 
      line-height: 100%; 
    }} 

    #backgroundTable {{ 
      margin:0; 
      padding:0; 
      width:100% !important; 
      line-height: 100% !important; 
    }}

    img {{ 
      outline:none; 
      text-decoration:none; 
      -ms-interpolation-mode: bicubic;
      width: auto;
      max-width: 100%; 
      float: left; 
      clear: both; 
      display: block;
    }}

    center {{
      width: 100%;
      min-width: 580px;
    }}

    a img {{ 
      border: none;
    }}

    p {{
      margin: 0 0 0 10px;
    }}

    table {{
      border-spacing: 0;
      border-collapse: collapse;
    }}

    td {{ 
      word-break: break-word;
      -webkit-hyphens: auto;
      -moz-hyphens: auto;
      hyphens: auto;
      border-collapse: collapse !important; 
    }}

    table, tr, td {{
      padding: 0;
      vertical-align: top;
      text-align: left;
    }}

    hr {{
      color: #d9d9d9; 
      background-color: #d9d9d9; 
      height: 1px; 
      border: none;
    }}

    /* Responsive Grid */

    table.body {{
      height: 100%;
      width: 100%;
    }}

    table.container {{
      width: 580px;
      margin: 0 auto;
      text-align: inherit;
    }}

    table.row {{ 
      padding: 0px; 
      width: 100%;
      position: relative;
    }}

    table.container table.row {{
      display: block;
    }}

    td.wrapper {{
      padding: 10px 20px 0px 0px;
      position: relative;
    }}

    table.columns,
    table.column {{
      margin: 0 auto;
    }}

    table.columns td,
    table.column td {{
      padding: 0px 0px 10px; 
    }}

    table.columns td.sub-columns,
    table.column td.sub-columns,
    table.columns td.sub-column,
    table.column td.sub-column {{
      padding-right: 10px;
    }}

    td.sub-column, td.sub-columns {{
      min-width: 0px;
    }}

    table.row td.last,
    table.container td.last {{
      padding-right: 0px;
    }}

    table.one {{ width: 30px; }}
    table.two {{ width: 80px; }}
    table.three {{ width: 130px; }}
    table.four {{ width: 180px; }}
    table.five {{ width: 230px; }}
    table.six {{ width: 280px; }}
    table.seven {{ width: 330px; }}
    table.eight {{ width: 380px; }}
    table.nine {{ width: 430px; }}
    table.ten {{ width: 480px; }}
    table.eleven {{ width: 530px; }}
    table.twelve {{ width: 580px; }}

    table.one center {{ min-width: 30px; }}
    table.two center {{ min-width: 80px; }}
    table.three center {{ min-width: 130px; }}
    table.four center {{ min-width: 180px; }}
    table.five center {{ min-width: 230px; }}
    table.six center {{ min-width: 280px; }}
    table.seven center {{ min-width: 330px; }}
    table.eight center {{ min-width: 380px; }}
    table.nine center {{ min-width: 430px; }}
    table.ten center {{ min-width: 480px; }}
    table.eleven center {{ min-width: 530px; }}
    table.twelve center {{ min-width: 580px; }}

    table.one .panel center {{ min-width: 10px; }}
    table.two .panel center {{ min-width: 60px; }}
    table.three .panel center {{ min-width: 110px; }}
    table.four .panel center {{ min-width: 160px; }}
    table.five .panel center {{ min-width: 210px; }}
    table.six .panel center {{ min-width: 260px; }}
    table.seven .panel center {{ min-width: 310px; }}
    table.eight .panel center {{ min-width: 360px; }}
    table.nine .panel center {{ min-width: 410px; }}
    table.ten .panel center {{ min-width: 460px; }}
    table.eleven .panel center {{ min-width: 510px; }}
    table.twelve .panel center {{ min-width: 560px; }}

    .body .columns td.one,
    .body .column td.one {{ width: 8.333333%; }}
    .body .columns td.two,
    .body .column td.two {{ width: 16.666666%; }}
    .body .columns td.three,
    .body .column td.three {{ width: 25%; }}
    .body .columns td.four,
    .body .column td.four {{ width: 33.333333%; }}
    .body .columns td.five,
    .body .column td.five {{ width: 41.666666%; }}
    .body .columns td.six,
    .body .column td.six {{ width: 50%; }}
    .body .columns td.seven,
    .body .column td.seven {{ width: 58.333333%; }}
    .body .columns td.eight,
    .body .column td.eight {{ width: 66.666666%; }}
    .body .columns td.nine,
    .body .column td.nine {{ width: 75%; }}
    .body .columns td.ten,
    .body .column td.ten {{ width: 83.333333%; }}
    .body .columns td.eleven,
    .body .column td.eleven {{ width: 91.666666%; }}
    .body .columns td.twelve,
    .body .column td.twelve {{ width: 100%; }}

    td.offset-by-one {{ padding-left: 50px; }}
    td.offset-by-two {{ padding-left: 100px; }}
    td.offset-by-three {{ padding-left: 150px; }}
    td.offset-by-four {{ padding-left: 200px; }}
    td.offset-by-five {{ padding-left: 250px; }}
    td.offset-by-six {{ padding-left: 300px; }}
    td.offset-by-seven {{ padding-left: 350px; }}
    td.offset-by-eight {{ padding-left: 400px; }}
    td.offset-by-nine {{ padding-left: 450px; }}
    td.offset-by-ten {{ padding-left: 500px; }}
    td.offset-by-eleven {{ padding-left: 550px; }}

    td.expander {{
      visibility: hidden;
      width: 0px;
      padding: 0 !important;
    }}

    table.columns .text-pad,
    table.column .text-pad {{
      padding-left: 10px;
      padding-right: 10px;
    }}

    table.columns .left-text-pad,
    table.columns .text-pad-left,
    table.column .left-text-pad,
    table.column .text-pad-left {{
      padding-left: 10px;
    }}

    table.columns .right-text-pad,
    table.columns .text-pad-right,
    table.column .right-text-pad,
    table.column .text-pad-right {{
      padding-right: 10px;
    }}

    /* Block Grid */

    .block-grid {{
      width: 100%;
      max-width: 580px;
    }}

    .block-grid td {{
      display: inline-block;
      padding:10px;
    }}

    .two-up td {{
      width:270px;
    }}

    .three-up td {{
      width:173px;
    }}

    .four-up td {{
      width:125px;
    }}

    .five-up td {{
      width:96px;
    }}

    .six-up td {{
      width:76px;
    }}

    .seven-up td {{
      width:62px;
    }}

    .eight-up td {{
      width:52px;
    }}

    /* Alignment & Visibility Classes */

    table.center, td.center {{
      text-align: center;
    }}

    h1.center,
    h2.center,
    h3.center,
    h4.center,
    h5.center,
    h6.center {{
      text-align: center;
    }}

    span.center {{
      display: block;
      width: 100%;
      text-align: center;
    }}

    img.center {{
      margin: 0 auto;
      float: none;
    }}

    .show-for-small,
    .hide-for-desktop {{
      display: none;
    }}

    /* Typography */

    body, table.body, h1, h2, h3, h4, h5, h6, p, td {{ 
      color: #222222;
      font-family: "Helvetica", "Arial", sans-serif; 
      font-weight: normal; 
      padding:0; 
      margin: 0;
      text-align: left; 
      line-height: 1.3;
    }}

    h1, h2, h3, h4, h5, h6 {{
      word-break: normal;
    }}

    h1 {{font-size: 40px;}}
    h2 {{font-size: 36px;}}
    h3 {{font-size: 32px;}}
    h4 {{font-size: 28px;}}
    h5 {{font-size: 24px;}}
    h6 {{font-size: 20px;}}
    body, table.body, p, td {{font-size: 14px;line-height:19px;}}

    p.lead, p.lede, p.leed {{
      font-size: 18px;
      line-height:21px;
    }}

    p {{ 
      margin-bottom: 10px;
    }}

    small {{
      font-size: 10px;
    }}

    a {{
      color: #2ba6cb; 
      text-decoration: none;
    }}

    a:hover {{ 
      color: #2795b6 !important;
    }}

    a:active {{ 
      color: #2795b6 !important;
    }}

    a:visited {{ 
      color: #2ba6cb !important;
    }}

    h1 a, 
    h2 a, 
    h3 a, 
    h4 a, 
    h5 a, 
    h6 a {{
      color: #2ba6cb;
    }}

    h1 a:active, 
    h2 a:active,  
    h3 a:active, 
    h4 a:active, 
    h5 a:active, 
    h6 a:active {{ 
      color: #2ba6cb !important; 
    }} 

    h1 a:visited, 
    h2 a:visited,  
    h3 a:visited, 
    h4 a:visited, 
    h5 a:visited, 
    h6 a:visited {{ 
      color: #2ba6cb !important; 
    }} 

    /* Panels */

    .panel {{
      background: #f2f2f2;
      border: 1px solid #d9d9d9;
      padding: 10px !important;
    }}

    .sub-grid table {{
      width: 100%;
    }}

    .sub-grid td.sub-columns {{
      padding-bottom: 0;
    }}

    /* Buttons */

    table.button,
    table.tiny-button,
    table.small-button,
    table.medium-button,
    table.large-button {{
      width: 100%;
      overflow: hidden;
    }}

    table.button td,
    table.tiny-button td,
    table.small-button td,
    table.medium-button td,
    table.large-button td {{
      display: block;
      width: auto !important;
      text-align: center;
      background: #2ba6cb;
      border: 1px solid #2284a1;
      color: #ffffff;
      padding: 8px 0;
    }}

    table.tiny-button td {{
      padding: 5px 0 4px;
    }}

    table.small-button td {{
      padding: 8px 0 7px;
    }}

    table.medium-button td {{
      padding: 12px 0 10px;
    }}

    table.large-button td {{
      padding: 21px 0 18px;
    }}

    table.button td a,
    table.tiny-button td a,
    table.small-button td a,
    table.medium-button td a,
    table.large-button td a {{
      font-weight: bold;
      text-decoration: none;
      font-family: Helvetica, Arial, sans-serif;
      color: #ffffff;
      font-size: 16px;
    }}

    table.tiny-button td a {{
      font-size: 12px;
      font-weight: normal;
    }}

    table.small-button td a {{
      font-size: 16px;
    }}

    table.medium-button td a {{
      font-size: 20px;
    }}

    table.large-button td a {{
      font-size: 24px;
    }}

    table.button:hover td,
    table.button:visited td,
    table.button:active td {{
      background: #2795b6 !important;
    }}

    table.button:hover td a,
    table.button:visited td a,
    table.button:active td a {{
      color: #fff !important;
    }}

    table.button:hover td,
    table.tiny-button:hover td,
    table.small-button:hover td,
    table.medium-button:hover td,
    table.large-button:hover td {{
      background: #2795b6 !important;
    }}

    table.button:hover td a,
    table.button:active td a,
    table.button td a:visited,
    table.tiny-button:hover td a,
    table.tiny-button:active td a,
    table.tiny-button td a:visited,
    table.small-button:hover td a,
    table.small-button:active td a,
    table.small-button td a:visited,
    table.medium-button:hover td a,
    table.medium-button:active td a,
    table.medium-button td a:visited,
    table.large-button:hover td a,
    table.large-button:active td a,
    table.large-button td a:visited {{
      color: #ffffff !important; 
    }}

    table.secondary td {{
      background: #e9e9e9;
      border-color: #d0d0d0;
      color: #555;
    }}

    table.secondary td a {{
      color: #555;
    }}

    table.secondary:hover td {{
      background: #d0d0d0 !important;
      color: #555;
    }}

    table.secondary:hover td a,
    table.secondary td a:visited,
    table.secondary:active td a {{
      color: #555 !important;
    }}

    table.success td {{
      background: #5da423;
      border-color: #457a1a;
    }}

    table.success:hover td {{
      background: #457a1a !important;
    }}

    table.alert td {{
      background: #c60f13;
      border-color: #970b0e;
    }}

    table.alert:hover td {{
      background: #970b0e !important;
    }}

    table.radius td {{
      -webkit-border-radius: 3px;
      -moz-border-radius: 3px;
      border-radius: 3px;
    }}

    table.round td {{
      -webkit-border-radius: 500px;
      -moz-border-radius: 500px;
      border-radius: 500px;
    }}

    /* Outlook First */

    body.outlook p {{
      display: inline !important;
    }}

    /*  Media Queries */

    @media only screen and (max-width: 600px) {{

      table[class="body"] img {{
        width: auto !important;
        height: auto !important;
      }}

      table[class="body"] center {{
        min-width: 0 !important;
      }}

      table[class="body"] .container {{
        width: 95% !important;
      }}

      table[class="body"] .row {{
        width: 100% !important;
        display: block !important;
      }}

      table[class="body"] .wrapper {{
        display: block !important;
        padding-right: 0 !important;
      }}

      table[class="body"] .columns,
      table[class="body"] .column {{
        table-layout: fixed !important;
        float: none !important;
        width: 100% !important;
        padding-right: 0px !important;
        padding-left: 0px !important;
        display: block !important;
      }}

      table[class="body"] .wrapper.first .columns,
      table[class="body"] .wrapper.first .column {{
        display: table !important;
      }}

      table[class="body"] table.columns td,
      table[class="body"] table.column td {{
        width: 100% !important;
      }}

      table[class="body"] .columns td.one,
      table[class="body"] .column td.one {{ width: 8.333333% !important; }}
      table[class="body"] .columns td.two,
      table[class="body"] .column td.two {{ width: 16.666666% !important; }}
      table[class="body"] .columns td.three,
      table[class="body"] .column td.three {{ width: 25% !important; }}
      table[class="body"] .columns td.four,
      table[class="body"] .column td.four {{ width: 33.333333% !important; }}
      table[class="body"] .columns td.five,
      table[class="body"] .column td.five {{ width: 41.666666% !important; }}
      table[class="body"] .columns td.six,
      table[class="body"] .column td.six {{ width: 50% !important; }}
      table[class="body"] .columns td.seven,
      table[class="body"] .column td.seven {{ width: 58.333333% !important; }}
      table[class="body"] .columns td.eight,
      table[class="body"] .column td.eight {{ width: 66.666666% !important; }}
      table[class="body"] .columns td.nine,
      table[class="body"] .column td.nine {{ width: 75% !important; }}
      table[class="body"] .columns td.ten,
      table[class="body"] .column td.ten {{ width: 83.333333% !important; }}
      table[class="body"] .columns td.eleven,
      table[class="body"] .column td.eleven {{ width: 91.666666% !important; }}
      table[class="body"] .columns td.twelve,
      table[class="body"] .column td.twelve {{ width: 100% !important; }}

      table[class="body"] td.offset-by-one,
      table[class="body"] td.offset-by-two,
      table[class="body"] td.offset-by-three,
      table[class="body"] td.offset-by-four,
      table[class="body"] td.offset-by-five,
      table[class="body"] td.offset-by-six,
      table[class="body"] td.offset-by-seven,
      table[class="body"] td.offset-by-eight,
      table[class="body"] td.offset-by-nine,
      table[class="body"] td.offset-by-ten,
      table[class="body"] td.offset-by-eleven {{
        padding-left: 0 !important;
      }}

      table[class="body"] table.columns td.expander {{
        width: 1px !important;
      }}

      table[class="body"] .right-text-pad,
      table[class="body"] .text-pad-right {{
        padding-left: 10px !important;
      }}

      table[class="body"] .left-text-pad,
      table[class="body"] .text-pad-left {{
        padding-right: 10px !important;
      }}

      table[class="body"] .hide-for-small,
      table[class="body"] .show-for-desktop {{
        display: none !important;
      }}

      table[class="body"] .show-for-small,
      table[class="body"] .hide-for-desktop {{
        display: inherit !important;
      }}
    }}
  </style>
  <style>
    table.facebook td {{
      background: #3b5998;
      border-color: #2d4473;
    }}

    table.facebook:hover td {{
      background: #2d4473 !important;
    }}

    table.twitter td {{
      background: #00acee;
      border-color: #0087bb;
    }}

    table.twitter:hover td {{
      background: #0087bb !important;
    }}

    table.google-plus td {{
      background-color: #DB4A39;
      border-color: #CC0000;
    }}

    table.google-plus:hover td {{
      background: #CC0000 !important;
    }}

    .template-label {{
      color: #ffffff;
      font-weight: bold;
      font-size: 11px;
    }}

    .callout .wrapper {{
      padding-bottom: 20px;
    }}

    .callout .panel {{
      background: #ECF8FF;
      border-color: #b9e5ff;
    }}

    .header {{
      background: #999999;
    }}

    .footer .wrapper {{
      background: #ebebeb;
    }}

    .footer h5 {{
      padding-bottom: 10px;
    }}

    table.columns .text-pad {{
      padding-left: 10px;
      padding-right: 10px;
    }}

    table.columns .left-text-pad {{
      padding-left: 10px;
    }}

    table.columns .right-text-pad {{
      padding-right: 10px;
    }}

    @media only screen and (max-width: 600px) {{

      table[class="body"] .right-text-pad {{
        padding-left: 10px !important;
      }}

      table[class="body"] .left-text-pad {{
        padding-right: 10px !important;
      }}
    }}
  </style>
</head>

<body>
  <table class="body">
    <tr>
      <td class="center" align="center" valign="top">
              </td>
            </tr>
          </table>

          <table class="container">
            <tr>
              <td>
                <table class="row">
                  <tr>
                    <td class="wrapper last">

                      <table class="twelve columns">
                        <tr>
                          <td>
                            <h3>Dear {Usernamefor}</h3>
                            <p class="lead">You have already {message} VIP Service</p>
                            <p>This email aim to notify you that the payment has been completed and you have became the VIP in quick reading website</p>
                            <p>You can use the bookshelf function and download the novels you want to read</p>
                            <p>However, you only have 30 days for the membership. After the deadline, your cache record will be deleted. In order to avoid affecting your reading, please renew your account in time </p>
                            <br>
                            <p>Yours sincerely</p>
                            <p>Yan Liu</p>
                            <p>Final Year Projects</p>
                            <p>Novels Reading and Searching Website</p>
                            <p>WIT Waterford Ireland</p>
                            <p>X91 HXT3</p>
                            <p>E-mail: 278899085@qq.com</p>
                          </td>
                          <td class="expander"></td>
                        </tr>
                      </table>

                    </td>
                  </tr>
                </table>

                <table class="row callout">
                  <tr>
                    <td class="wrapper last">

                      <table class="twelve columns">
                        <tr>
                          <td class="panel">
                            <p>Now turn to the website and enjoy reading! <a href="https://wwww.quickreading.net">Click it!</a></p>
                          </td>
                          <td class="expander"></td>
                        </tr>
                      </table>

                    </td>
                  </tr>
                </table>

                <table class="row footer">
                  <tr>
                    <td class="wrapper">

                      <table class="six columns">
                        <tr>
                          <td class="left-text-pad">

                            <h5>Connect With Me:</h5>

                            <table class="tiny-button facebook">
                              <tr>
                                <td>
                                  <a href="https://www.facebook.com/profile.php?id=100028064701381">Facebook</a>
                                </td>
                              </tr>
                            </table>

                            <br>

                            <table class="tiny-button twitter">
                              <tr>
                                <td>
                                  <a href="https://twitter.com/YanLiu1996">Twitter</a>
                                </td>
                              </tr>
                            </table>

                            <br>

                            <table class="tiny-button google-plus">
                              <tr>
                                <td>
                                  <a href="https://plus.google.com/101510431121969326477">Google +</a>
                                </td>
                              </tr>
                            </table>

                          </td>
                          <td class="expander"></td>
                        </tr>
                      </table>

                    </td>
                    <td class="wrapper last">

                      <table class="six columns">
                        <tr>
                          <td class="last right-text-pad">
                            <h5>Contact Info:</h5>
                            <p>Phone: 0833863840</p>
                            <p>Email: <a href="quickreadingnovelswebsite@gmail.com">quickreadingnovelswebsite@gmail.com</a></p>
                          </td>
                          <td class="expander"></td>
                        </tr>
                      </table>

                    </td>
                  </tr>
                </table>
                <table class="row">
                  <tr>
                    <td class="wrapper last">
                      <table class="twelve columns">
                        <tr>
                          <td align="center">
                            <center>
                              <p style="text-align:center;"><a href="#">Terms</a> | <a href="#">Privacy</a> | <a href="#">Unsubscribe</a></p>
                            </center>
                          </td>
                          <td class="expander"></td>
                        </tr>
                      </table>

                    </td>
                  </tr>
                </table>

                <!-- container end below -->
              </td>
            </tr>
          </table>

        </center>
      </td>
    </tr>
  </table>
</body>

</html>
            """
