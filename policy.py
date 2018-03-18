#!/usr/bin/python
import os

from common.email_obj import EmailObj
from okex.spot_obj import SpotClass as okexSpotClass
import common.db_api as dbApi

PRICE_GAP = 0.05
PRICE_RATIO_1 = PRICE_GAP
PRICE_RATIO_2 = PRICE_GAP * 2
PRICE_RATIO_3 = PRICE_GAP * 3
PRICE_RATIO_4 = PRICE_GAP * 4
PARTITION_NUM = 4
MIN_COIN_AMOUNT = 10
BASE_COIN_RESERVE = 0
TARGET_COIN_RESERVE = 700

SELL_BATCH_RATIO = [PRICE_RATIO_1, PRICE_RATIO_2, PRICE_RATIO_3, PRICE_RATIO_4]
BUY_BATCH_RATIO = [PRICE_RATIO_1, PRICE_RATIO_2, PRICE_RATIO_3, PRICE_RATIO_4]


def buy_policy(spot_instance, float_digits, coin):
    """
    coin: base coin, like ETH
    """
    print('Begin to send buy order...')
    medium_price = spot_instance.medium_price
    current_price = spot_instance.current_price
    base_price = min(medium_price, current_price)
    print('Medium price: %s' % medium_price)
    print('Current price: %s' % current_price)

    total = float(spot_instance.balance(coin)['free']) - BASE_COIN_RESERVE
    rest = total

    for i in BUY_BATCH_RATIO:
        price = round(base_price * (1 - i), float_digits)
        if rest < MIN_COIN_AMOUNT * price:
            return
        amount = round(max(round(total/(len(BUY_BATCH_RATIO) * price)), MIN_COIN_AMOUNT))
        order_id = spot_instance.buy(price, round(min(rest/price, amount)))
        if order_id is None:
            continue
        # insert new order into database
        insert_order(spot_instance.get_order(order_id))
        rest -= amount * price
    return


def sell_policy(spot_instance, float_digits, coin):
    """
    coin: target coin, like DPY
    """
    print('Begin to send sell order...')
    medium_price = spot_instance.medium_price
    current_price = spot_instance.current_price
    base_price = max(medium_price, current_price)
    print('Medium price: %s' % medium_price)
    print('Current price: %s' % current_price)

    total = float(spot_instance.balance(coin)['free']) - TARGET_COIN_RESERVE
    rest = total

    if rest < MIN_COIN_AMOUNT:
        return
    amount = round(max(round(total/len(SELL_BATCH_RATIO), float_digits), MIN_COIN_AMOUNT))
    for i in SELL_BATCH_RATIO:
        price = round(base_price * (1 + i), float_digits)
        order_id = spot_instance.sell(price, round(min(rest, amount)))
        if order_id is None:
            continue
        # insert new order into database
        insert_order(spot_instance.get_order(order_id))
        rest -= amount
        if rest < MIN_COIN_AMOUNT:
            return


if __name__ == "__main__":
    """
    pair = 'dpy_eth'
    target_coin = 'dpy'
    base_coin = 'eth'
    # create a new instance
    okSpot = okexSpotClass(pair, '1day', 7, debug=True)
    # sell_policy(okSpot, 8, target_coin)
    # buy_policy(okSpot, 8, base_coin)
    # print(okSpot.balance('dpy'))
    # print(okSpot.balance('eth'))
    # init_database()
    order = okSpot.get_order('3229114')
    print(order)
    order = dbApi.get_order('3229114')
    order[0].symbol = 'btc_eth'
    print(order)
    # insert_order(order)
    """
    email_srv = os.environ.get('EMAIL_SMTP')
    email_user = os.environ.get('EMAIL_FROM')
    email_pwd = os.environ.get('EMAIL_PWD')

    # 构造html
    a = '200'
    html = """\
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <body>
    <div id="container">
      <div id="content">
       <table width="500" border="2" bordercolor="red" cellspacing="2">
      <tr>
        <td><strong>站点</strong></td>
      </tr>
      <tr>
        <td>node</td>
        <td>""" + a + """</td>
      </tr>
    </table>
      </div>
    </div>
    </div>
    </body>
    </html>
    """
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    env = Environment(
        loader=FileSystemLoader('common'),
    )
    template = env.get_template('template.html')
    orders = [{"amount":18,"avg_price":0,"create_date":1520585015000,"deal_amount":0,"order_id":3072019,"orders_id":3072019,"price":0.0023532,"status":0,"symbol":"dpy_eth","type":"sell"},
              {"amount": 18, "avg_price": 0, "create_date": 1520585015000, "deal_amount": 0, "order_id": 3072019,
               "orders_id": 3072019, "price": 0.0023532, "status": 0, "symbol": "dpy_eth", "type": "sell"}]
    html = template.render(orders=orders)
    print(html)
    email_obj = EmailObj(email_srv, email_user, email_pwd)
    email_obj.send_mail('test', html, email_user, 'pkguowu@yahoo.com', email_user)
