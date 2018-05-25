#!/usr/bin/python

from binance.enums import *
from binance.spot_obj import RmtSrvObj

if __name__ == "__main__":
    pair = 'ETHUSDT'
    rmt_srv = RmtSrvObj(pair, KLINE_INTERVAL_1DAY, 7)

    # ret = rmt_srv.get_kline()
    # print(ret)

    # print(rmt_srv.get_available_coins())

    # print(rmt_srv.get_all_orders())
    print(rmt_srv.get_order(72632872))
    print(rmt_srv.get_order(72619361))
