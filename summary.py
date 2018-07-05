#!/usr/bin/python
import argparse
from datetime import datetime, timedelta
import time

from binance.enums import KLINE_INTERVAL_1DAY
from setup import *
from binance.rmt_srv import RmtSrvObj as BnbRmtSrvObj
from okex.rmt_srv import RmtSrvObj as OkexRmtSrvObj
from common.lib import reserve_float, send_profit_report, send_report, send_balance_report
from mongo.db_api import DbApi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-e', help='exchange name')

    args = parser.parse_args()
    # print(args)
    exchange = args.e
    base_coin = 'usdt'
    target_coin = 'btc'

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
    target_price = rmt_srv.current_price

    update_flag = False
    db_name = exchange
    db_api = DbApi(db_url, db_name, mongo_user, mongo_pwd)
    total_balance = 0
    usdt_balance = 0

    for coin in coins:
        db_api.insert_account(coin)
        if coin['coin'].upper() == target_coin.upper():
            total_balance += coin['balance']
        elif coin['coin'].upper() == 'USDT':
            usdt_balance += coin['balance']
        else:
            if exchange == 'binance':
                base_coin_tmp = target_coin.upper()
                target_coin_tmp = coin['coin'].upper()
                pair = '%s%s' % (target_coin_tmp, base_coin_tmp)
                print("The pair is %s " % pair)
                rmt_srv = BnbRmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7)
            elif exchange == 'okex':
                pair = '%s_%s' % (coin['coin'], target_coin)
                print("The pair is %s " % pair)
                rmt_srv = OkexRmtSrvObj(pair, '1day', 7)
            else:
                print('Wrong exchange name: %s' % exchange)
                pair = None
                rmt_srv = None
                exit(1)

            price = rmt_srv.current_price
            print('%s: %s %s' % (coin['coin'], coin['balance'], price))
            total_balance += price * coin['balance']

    print(total_balance)
    usdt_balance += total_balance * target_price
    print(usdt_balance)
    print(usdt_balance * 6.6)
    # exit()
    # send report
    print('Send report')
    # local time is a little different from server time
    end_time = datetime.now() + timedelta(hours=1)
    begin_time = end_time - timedelta(days=1)
    accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
    send_balance_report(usdt_balance, accounts, email_receiver, subject='Coin Account Report - %s' % exchange)
