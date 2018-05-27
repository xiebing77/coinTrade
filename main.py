#!/usr/bin/python
import datetime
import argparse

from setup import *
import okex.rmt_srv as spot_obj
from common import db_api
from policy import run_policy, send_report
from conf import FLOAT_DIGITS


if __name__ == "__main__":
    # pair = 'dpy_eth'
    # target_coin = 'dpy'
    # base_coin = 'eth'

    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b
    target_coin = args.t

    pair = '%s_%s' % (target_coin, base_coin)
    print("The pair is %s " % pair)
    ok_spot = spot_obj.RmtSrvObj(pair, '1day', 7, debug=True)

    # cancel all unfinished orders
    print('Cancel all orders')
    ok_spot.cancel_orders()
    ok_spot.update_account()

    # update pending orders in database
    print('Update pending orders')
    orders = db_api.get_pending_orders()
    for item in orders:
        order = ok_spot.get_order(item['order_id'])
        if order is not None:
            db_api.update_order(order)

    # re-order
    print('Send new orders')
    run_policy(ok_spot, float_digits=FLOAT_DIGITS, target_coin=target_coin, base_coin=base_coin)

    # insert new account snapshot in database
    print('Update account')
    for i in ok_spot.get_available_coins():
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
    send_report(orders, accounts, email_receiver)
