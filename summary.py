#!/usr/bin/python
import argparse
from datetime import datetime, timedelta
import time

from binance.enums import KLINE_INTERVAL_1DAY
from setup import *
from binance.rmt_srv import RmtSrvObj as BnbRmtSrvObj
from okex.rmt_srv import RmtSrvObj as OkexRmtSrvObj
from common.lib import reserve_float, send_profit_report
from mongo.db_api import DbApi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-e', help='exchange name')

    args = parser.parse_args()
    # print(args)
    exchange = args.e
    base_coin = 'usdt'
    target_coin = 'eth'

    if exchange == 'binance':
        base_coin = base_coin.upper()
        target_coin = target_coin.upper()
        pair = '%s%s' % (target_coin, base_coin)
        print("The pair is %s " % pair)
        rmt_srv = BnbRmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7)
    elif exchange == 'okex':
        pair = '%s_%s' % (target_coin, base_coin)
        print("The pair is %s " % pair)
        rmt_srv = OkexRmtSrvObj(pair, '1day', 7)
    else:
        print('Wrong exchange name: %s' % exchange)
        pair = None
        rmt_srv = None
        exit(1)

    coins = rmt_srv.get_available_coins()

    update_flag = False
    db_name = exchange
    db_api = DbApi(db_url, db_name, mongo_user, mongo_pwd)

    for coin in coins:
        db_api.insert_account(coin)

    # check if any order is dealt
    buy_orders = db_api.get_orders({'symbol': pair, "status": "Dealt", "type": "buy"})
    sell_orders = db_api.get_orders({'symbol': pair, "status": "Dealt", "type": "sell"})

    buy_target_coin = 0
    sell_base_coin = 0
    sell_target_coin = 0
    buy_base_coin = 0
    for order in buy_orders:
        print("%4s: %10s %18s" % (order['type'], order['amount'], order['avg_price']))
        buy_target_coin += float(order['amount'])
        sell_base_coin += float(order['amount']) * float(order['avg_price'])

    for order in sell_orders:
        print("%4s: %10s %18s" % (order['type'], order['amount'], order['avg_price']))
        sell_target_coin += float(order['amount'])
        buy_base_coin += float(order['amount']) * float(order['avg_price'])

    profit = dict(symbol=pair)
    profit['timestamp'] = time.time()
    profit['create_date'] = datetime.fromtimestamp(profit['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
    profit['target_coin'] = reserve_float(buy_target_coin - sell_target_coin, 8)
    profit['base_coin'] = reserve_float(sell_base_coin - buy_base_coin, 8)
    profit['balance'] = reserve_float(rmt_srv.current_price * profit['target_coin'], 8)
    profit['profit'] = reserve_float(profit['balance'] - profit['base_coin'], 8)
    profit['ratio'] = reserve_float((profit['profit'] / profit['base_coin']) * 100, 2)
    profit['current_price'] = rmt_srv.current_price
    profit['cost_price'] = reserve_float(profit['base_coin'] / profit['target_coin'], 8)

    db_api.insert_profit(profit)
    print("*" * 40)
    print(profit['create_date'])
    print(" Buy %s: %s" % (target_coin, profit['target_coin']))
    print(" Cost %s: %s" % (base_coin, profit['base_coin']))
    print(" Current price: %s" % rmt_srv.current_price)
    print(" Cost price: %s" % profit['cost_price'])
    print(" Balance: %s" % profit['balance'])
    print(" Profit: %s" % profit['profit'])
    print(" Profit ratio: %s" % profit['ratio'] + r'%')

    # send report
    print('Send report')
    # local time is a little different from server time
    end_time = datetime.now() + timedelta(hours=1)
    begin_time = end_time - timedelta(days=5)
    profits = db_api.get_profits_by_time(pair, begin_time.timestamp(), end_time.timestamp())
    send_profit_report(profits, email_receiver, subject='Coin Profit Report - %s' % pair)
