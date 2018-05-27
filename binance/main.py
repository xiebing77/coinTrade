#!/usr/bin/python
import datetime
import argparse

from binance.enums import KLINE_INTERVAL_1DAY
from binance.rmt_srv import RmtSrvObj
from mongo.db_api import DbApi
from common.lib import send_report
from setup import *
from binance.policy import Policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')
    # parser.add_argument('-f', help='float digits')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b.upper()
    target_coin = args.t.upper()
    # float_digits = args.f

    present = datetime.datetime.now()
    print('\n%s Main start...' % present)

    pair = '%s%s' % (target_coin, base_coin)
    print("The pair is %s " % pair)
    rmt_srv = RmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7, debug=True)

    db_url = "mongodb://localhost:27017/"
    db_name = "binance"
    db_api = DbApi(db_url, db_name)

    # cancel all unfinished orders
    print('Cancel all orders')
    rmt_srv.cancel_orders()
    rmt_srv.update_account()

    # update pending orders in database
    print('Update pending orders')
    orders = db_api.get_pending_orders()
    for item in orders:
        order = rmt_srv.get_order(item['order_id'])
        if order is not None:
            db_api.update_order(order)

    # re-order
    print('Send new orders')
    policy = Policy(db_api=db_api, rmt_srv=rmt_srv, target_coin=target_coin,
                    base_coin=base_coin, target_amount_digits=3,
                    base_amount_digits=2, price_digits=2
                    )
    policy.run_policy()

    # insert new account snapshot in database
    print('Update account')
    for i in rmt_srv.get_available_coins():
        db_api.insert_account(i)

    # send report
    print('Send report')
    # local time is a little different from server time
    end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    begin_time = end_time - datetime.timedelta(days=3)
    orders = db_api.get_orders_by_time(begin_time.timestamp(), end_time.timestamp())
    accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
    for i in accounts:
        if i['balance'] < 0.001:
            accounts.remove(i)
    send_report(orders, accounts, email_receiver, subject='Coin Trade Daily Report - binance')
