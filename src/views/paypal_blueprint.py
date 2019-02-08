from sanic import Blueprint
from sanic.response import json, html
from jinja2 import Environment, PackageLoader, select_autoescape
import paypalrestsdk

paypal_bp = Blueprint('paypal_blueprint')
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AaF3e62lDn44mSmuWdc9g4jLwyWVkow22M24mHMak57LzGM76BJ1AUCdkJu3XDR342U8eo5ldkaHY998",
  "client_secret": "EFb9ipDk_i7UbtnODGGlXbBinYtRABcIaZWAKFQ-4Mqvs_Dd0Iv3Qb0eHYHpbd9c1JYmOtw9gnVZr6ux"})

env = Environment(
    loader=PackageLoader('views.paypal_blueprint', '../templates/payment'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@paypal_bp.route('/pay')
async def pay(request):
    return template('paypal.html')


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


@paypal_bp.route('/execute', methods=['POST'])
async def execute(request):
    success = False
    print("hahhahahah")
    payment = paypalrestsdk.Payment.find(request.form.get('paymentID'))
    if payment.execute({'payer_id': request.form.get('payerID')}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)
    return json({'success': success})

