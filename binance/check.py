#!/usr/bin/python
import argparse
import datetime

from binance.enums import KLINE_INTERVAL_1DAY
from setup import *
import binance.spot_obj as spot_obj
from common import db_api
from policy import send_report
from common.lib import reserve_float
from conf import FLOAT_DIGITS

PROFIT_RATIO = 0.1
FEE_RATIO = 0.002

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b
    target_coin = args.t

    pair = '%s%s' % (target_coin.upper(), base_coin.upper())
    print("The pair is %s " % pair)
    rmt_srv = spot_obj.RmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7, debug=True)
    update_flag = False

    # check if any order is dealt
    print('Check if any order is dealt')
    orders = db_api.get_pending_orders()
    for item in orders:
        order = rmt_srv.get_order(item['order_id'])
        # print(item['order_id'])
        # order['status'] = 'Dealt'
        # order['deal_amount'] = item['amount']
        # order['avg_price'] = order['price']
        if order is None:
            print("Not find order from exchanger, need to delete it in database: ")
            print(item)
            db_api.delete_order(item['order_id'])
        elif order['status'] == 'Dealt':
            print("\n the order is done:")
            print(order)
            amount = reserve_float(order['deal_amount'] * (1 - FEE_RATIO))
            # print(amount)
            db_api.update_order(order)
            if amount < 10:
                continue
            update_flag = True
            print('%s order is dealt: pair(%s), price(%s), amount(%s)' % (order['type'], pair, order['avg_price'],
                                                                          order['deal_amount']))
            if order['type'] == 'buy':
                price = reserve_float(order['avg_price'] * (1 + PROFIT_RATIO), FLOAT_DIGITS)
                order_id = rmt_srv.sell(price, amount)
            else:
                price = reserve_float(order['avg_price'] * (1 - PROFIT_RATIO), FLOAT_DIGITS)
                new_amount = reserve_float(order['avg_price'] * amount / price)
                order_id = rmt_srv.buy(price, new_amount)

            if order_id is not None:
                # insert new order into database
                db_api.insert_order(rmt_srv.get_order(order_id))

    # insert new account snapshot in database
    if update_flag:
        print('Updating account...')
        for i in rmt_srv.get_available_coins():
            db_api.insert_account(i)

        # send report
        print('Sending report...')
        # local time is a little different from server time
        end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        begin_time = end_time - datetime.timedelta(days=3)
        orders = db_api.get_orders_by_time(begin_time.timestamp(), end_time.timestamp())
        accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
        send_report(orders, accounts, email_receiver)
