#!/usr/bin/python
import argparse
import datetime

from binance.enums import KLINE_INTERVAL_1DAY
from setup import *
from binance.rmt_srv import RmtSrvObj
from common.lib import reserve_float, send_report
from mongo.db_api import DbApi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')
    parser.add_argument('-a', help='target amount digits')
    parser.add_argument('-p', help='price digits')
    parser.add_argument('-r', help='profit ratio')
    parser.add_argument('-f', help='fee ratio')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b.upper()
    target_coin = args.t.upper()
    target_amount_digits = int(args.a)
    price_digits = int(args.p)
    profit_ratio = float(args.r)
    fee_ratio = float(args.f)

    present = datetime.datetime.now()
    print('\n%s Check if any order is dealt' % present)

    pair = '%s%s' % (target_coin, base_coin)
    print("The pair is %s " % pair)
    rmt_srv = RmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7, debug=True)
    update_flag = False

    db_url = "mongodb://localhost:27017/"
    db_name = "binance"
    db_api = DbApi(db_url, db_name, mongo_user, mongo_pwd)

    # check if any order is dealt
    orders = db_api.get_pending_orders(pair)
    for item in orders:
        order = rmt_srv.get_order(item['order_id'])
        # print(item['order_id'])
        # order['status'] = 'Dealt'
        # order['deal_amount'] = item['amount']
        # order['avg_price'] = order['price']
        if order is None:
            print("Not find order from exchanger, need to delete it in database: ")
            print(item)
            db_api.delete_order(item['symbol'], item['order_id'])
        elif order['status'] == 'Dealt':
            print("\n the order is done:")
            print(order)
            amount = reserve_float(float(order['deal_amount']) * (1 - fee_ratio), target_amount_digits)
            # print(amount)
            db_api.update_order(order)
            update_flag = True
            print('%s order is dealt: pair(%s), price(%s), amount(%s)' % (order['type'], pair, order['avg_price'],
                                                                          order['deal_amount']))
            if order['type'] == 'buy':
                price = reserve_float(float(order['avg_price']) * (1 + profit_ratio), price_digits)
                order_id = rmt_srv.sell(price, amount)
            else:
                price = reserve_float(float(order['avg_price']) * (1 - profit_ratio), price_digits)
                new_amount = reserve_float(float(order['avg_price']) * amount / price, target_amount_digits)
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
        begin_time = end_time - datetime.timedelta(days=2)
        orders = db_api.get_orders_by_time(pair, begin_time.timestamp(), end_time.timestamp())
        accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
        send_report(orders, accounts, email_receiver, subject='Coin Trade Check Report - %s' % pair)
