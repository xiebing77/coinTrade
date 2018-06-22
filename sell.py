#!/usr/bin/python
import datetime
import argparse

from binance.enums import KLINE_INTERVAL_1DAY
from binance.rmt_srv import RmtSrvObj as BnbRmtSrvObj
from okex.rmt_srv import RmtSrvObj as OkexRmtSrvObj
from mongo.db_api import DbApi
from common.lib import send_report
from setup import *
from policy.policy import Policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')
    parser.add_argument('-a', help='target amount digits')
    parser.add_argument('-d', help='base amount digits')
    parser.add_argument('-p', help='price digits')
    parser.add_argument('-g', help='price gap')
    parser.add_argument('-n', help='price gap num')
    parser.add_argument('-r', help='target coin reserve')
    parser.add_argument('-s', help='base coin reserve')
    parser.add_argument('-e', help='exchange name')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b
    target_coin = args.t
    target_amount_digits = int(args.a)
    base_amount_digits = int(args.d)
    price_digits = int(args.p)
    price_gap = float(args.g)
    price_gap_num = int(args.n)
    target_coin_reserve = float(args.r)
    base_coin_reserve = float(args.s)
    exchange = args.e

    present = datetime.datetime.now()
    print('\n%s Main start...' % present)

    if exchange == 'binance':
        base_coin = base_coin.upper()
        target_coin = target_coin.upper()
        pair = '%s%s' % (target_coin, base_coin)
        print("The pair is %s " % pair)
        rmt_srv = BnbRmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7, debug=True)
    elif exchange == 'okex':
        pair = '%s_%s' % (target_coin, base_coin)
        print("The pair is %s " % pair)
        rmt_srv = OkexRmtSrvObj(pair, '1day', 7, debug=True)
    else:
        print('Wrong exchange name: %s' % exchange)
        pair = None
        rmt_srv = None
        exit(1)

    db_name = exchange
    db_api = DbApi(db_url, db_name, mongo_user, mongo_pwd)

    # cancel all unfinished orders
    print('Cancel all orders')
    rmt_srv.cancel_orders()
    rmt_srv.update_account()

    # update pending orders in database
    print('Update pending orders')
    orders = db_api.get_pending_orders(pair)
    for item in orders:
        order = rmt_srv.get_order(item['order_id'])
        if order is not None:
            db_api.update_order(order)

    # re-order
    print('Send new orders:')
    policy = Policy(db_api=db_api, rmt_srv=rmt_srv, target_coin=target_coin,
                    base_coin=base_coin, target_amount_digits=target_amount_digits,
                    base_amount_digits=base_amount_digits, price_digits=price_digits,
                    price_gap=price_gap, price_gap_num=price_gap_num,
                    base_coin_reserve=base_coin_reserve, target_coin_reserve=target_coin_reserve
                    )
    policy.sell_policy()

    # insert new account snapshot in database
    print('Updating account...')
    db_api.insert_account(rmt_srv.get_balance(base_coin))
    db_api.insert_account(rmt_srv.get_balance(target_coin))
    # for i in rmt_srv.get_available_coins():
    #     db_api.insert_account(i)

    # send report
    print('Send report')
    # local time is a little different from server time
    end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    begin_time = end_time - datetime.timedelta(days=5)
    orders = db_api.get_orders_by_time(pair, begin_time.timestamp(), end_time.timestamp())
    accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp(), coins=[base_coin, target_coin])
    for i in accounts:
        if i['balance'] < 0.001:
            accounts.remove(i)
    send_report(orders, accounts, email_receiver, subject='Coin Trade Daily Report - %s' % pair)
