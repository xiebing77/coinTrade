#!/usr/bin/python
import os

from common.email_obj import EmailObj
from okex.spot_obj import RmtSrvObj as okexSpotClass
import common.db_api as db_api
from jinja2 import Environment, FileSystemLoader

from setup import *

PRICE_GAP = 0.05
PARTITION_NUM = 4
MIN_COIN_AMOUNT = 10
BASE_COIN_RESERVE = 0
TARGET_COIN_RESERVE = 0

SELL_BATCH_RATIO = [PRICE_GAP, PRICE_GAP * 2, PRICE_GAP * 4, PRICE_GAP * 5, PRICE_GAP * 6]
BUY_BATCH_RATIO = [PRICE_GAP, PRICE_GAP * 2, PRICE_GAP * 4, PRICE_GAP * 5, PRICE_GAP * 6]


def run_policy(spot_instance, float_digits, target_coin, base_coin):
    sell_policy(spot_instance, float_digits, target_coin)
    buy_policy(spot_instance, float_digits, base_coin)


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
        db_api.insert_order(spot_instance.get_order(order_id))
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
        db_api.insert_order(spot_instance.get_order(order_id))
        rest -= amount
        if rest < MIN_COIN_AMOUNT:
            return


def send_report(orders, accounts, to_addr, subject='Coin Trade Daily Report', cc_addr=''):
    # 构造html
    env = Environment(
        loader=FileSystemLoader(template_dir),
    )
    template = env.get_template('template.html')
    html = template.render(orders=orders, accounts=accounts)
    # print(html)
    email_obj = EmailObj(email_srv, email_user, email_pwd)
    email_obj.send_mail(subject, html, email_user, to_addr, cc_addr)


if __name__ == "__main__":
    pair = 'dpy_eth'
    target_coin = 'dpy'
    base_coin = 'eth'
    # create a new instance
    okSpot = okexSpotClass(pair, '1day', 7, debug=True)
    sell_policy(okSpot, 8, target_coin)
    # buy_policy(okSpot, 8, base_coin)
    # print(okSpot.balance('dpy'))
    # print(okSpot.balance('eth'))
    # init_database()
    # order = okSpot.get_order('3229114')
    # print(order)
    # order = db_api.get_order('3229114')
    # print(order)
    # account = db_api.get_account()
    # print(account)
    # order['symbol'] = 'gw_eth'

    # db_api.update_order(order)
    # for i in order[0]:
    #     print(i)
    # # order[0].symbol = 'btc_eth'
    # orders = [order]
    # send_report(orders, account, 'test', 'pkguowu@yahoo.com')
    # insert_order(order)
    # okSpot.cancel_orders()
    # print(okSpot.get_order('3071976'))
    # orders = db_api.get_pending_orders()
    # print(orders)
