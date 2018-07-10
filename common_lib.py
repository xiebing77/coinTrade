#!/usr/bin/python
import time
import datetime
import argparse

from binance.enums import KLINE_INTERVAL_1DAY
from binance.rmt_srv import RmtSrvObj as BnbRmtSrvObj

def get_common_cmd_parser():
    parser = argparse.ArgumentParser(description='coin trade')
    parser.add_argument('-b', help='base coin')
    parser.add_argument('-t', help='target coin')
    parser.add_argument('-a', help='target amount digits')
    parser.add_argument('-d', help='base amount digits')
    parser.add_argument('-p', help='price digits')
    parser.add_argument('-e', help='exchange name')
    parser.add_argument('-s', help='tick second')
    parser.add_argument('-r', help='email receiver')
    parser.add_argument('-i', help='instance No')
    return parser

def get_common_args(args):
    present = datetime.datetime.now()
    print('\n%s Main start...' % present)

    exchange = args.e
    arg_dict = {}
    if exchange == 'binance':
        arg_dict['base_coin'] = args.b.upper()
        arg_dict['target_coin'] = args.t.upper()
        pair = '%s%s' % (arg_dict['target_coin'], arg_dict['base_coin'])
        print("The pair is %s " % pair)
        rmt_srv = BnbRmtSrvObj(pair, KLINE_INTERVAL_1DAY, 300, debug=True)
    elif exchange == 'okex':
        arg_dict['base_coin'] = args.b
        arg_dict['target_coin'] = args.t
        pair = '%s%s' % (arg_dict['target_coin'], arg_dict['base_coin'])
        print("The pair is %s " % pair)
        rmt_srv = OkexRmtSrvObj(pair, '1day', 7, debug=True)
    else:
        print('Wrong exchange name: %s' % exchange)
        pair = None
        rmt_srv = None
        exit(1)

    return rmt_srv,arg_dict


