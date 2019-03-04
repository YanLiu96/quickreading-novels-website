from sanic import Blueprint
from sanic.response import json, html
from jinja2 import Environment, PackageLoader, select_autoescape
from src.database.mongodb import MotorBase
from urllib.parse import parse_qs, unquote
from src.fetcher.function import get_time
import paypalrestsdk
from src.config import CONFIG, LOGGER


paypal_bp = Blueprint('paypal_blueprint')
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AaF3e62lDn44mSmuWdc9g4jLwyWVkow22M24mHMak57LzGM76BJ1AUCdkJu3XDR342U8eo5ldkaHY998",
  "client_secret": "EFb9ipDk_i7UbtnODGGlXbBinYtRABcIaZWAKFQ-4Mqvs_Dd0Iv3Qb0eHYHpbd9c1JYmOtw9gnVZr6ux"})

env = Environment(
    loader=PackageLoader('views.paypal_blueprint', '../templates/payment'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


@paypal_bp.listener('before_server_start')
def setup_db(operate_bp, loop):
    global motor_base
    motor_base = MotorBase()


@paypal_bp.listener('after_server_stop')
def close_connection(operate_bp, loop):
    motor_base = None


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@paypal_bp.route('/pay')
async def pay(request):
    return template('paypal.html')

"""
@paypal_bp.route('/payment', methods=['POST'])
async def payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/payment/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "5.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "5.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})

"""


@paypal_bp.route('/paymentOneMonth', methods=['POST'])
async def payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/paymentOneMonth/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "One month vip",
                    "sku": "item",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "10.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@paypal_bp.route('/paymentSixMonth', methods=['POST'])
async def payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/paymentOneMonth/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "50.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "5.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@paypal_bp.route('/paymentOneYear', methods=['POST'])
async def payment(request):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://0.0.0.0:8001/paymentOneMonth/execute",
            "cancel_url": "http://0.0.0.0:8001/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "90.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "5.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})
    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)
    print(payment.id)
    return json({'paymentID': payment.id})


@paypal_bp.route('/execute', methods=['POST'])
async def execute(request):
    success = False
    payment = paypalrestsdk.Payment.find(request.form.get('paymentID'))
    if payment.execute({'payer_id': request.form.get('payerID')}):
        print('Execute success!')
        success = True
        user = request['session'].get('user', None)
        # data = parse_qs(str(request.body, encoding='utf-8'))
        if user:
            try:
                become_vip_time = get_time()
                motor_db = motor_base.get_db()
                res = await motor_db.user.update_one({'user': user}, {'$set': {'become_vip_time': become_vip_time}},
                                                     upsert=True)
                if res:
                    await motor_db.user.update_one({'user': user}, {'$set': {'vip_duration': 30}}, upsert=True)
                    LOGGER.info('VIP information have store in database ')
                else:
                    return json({"Do not store  in database"})
            except Exception as e:
                LOGGER.exception(e)
        else:
            return json({"Do not have this user in database"})
    else:
        print(payment.error)
    return json({'success': success})

