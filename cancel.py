#!/usr/bin/python
import datetime
import argparse

from binance.enums import KLINE_INTERVAL_1DAY
from binance.rmt_srv import RmtSrvObj as BnbRmtSrvObj
from okex.rmt_srv import RmtSrvObj as OkexRmtSrvObj
from mongo.db_api import DbApi
from setup import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')
    parser.add_argument('-e', help='exchange name')

    args = parser.parse_args()
    # print(args)
    base_coin = args.b
    target_coin = args.t
    exchange = args.e

    present = datetime.datetime.now()
    print('\n%s Cancel start...' % present)

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

