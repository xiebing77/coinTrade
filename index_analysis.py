#!/usr/bin/python
import time
import datetime
import argparse
import numpy as np
import pandas as pd
import talib
import common_lib
from common.lib import reserve_float
import indicator
from common.lib import send_report
import logging

def OnTick():
    df = rmt_srv.get_kline_pd()

    '''
    orders = pd.DataFrame(rmt_srv.get_open_orders())
    print('open orders: \n',orders)

    trades = pd.DataFrame(rmt_srv.get_my_trades())
    print(' trades: \n',trades)
    '''

    '''
    account = rmt_srv.get_account()
    account = pd.DataFrame(account)
    account['free'] = account['free'].apply(pd.to_numeric)
    account['locked'] = account['locked'].apply(pd.to_numeric)
    print(account[account['free']>0])
    print(account[account['locked']>0])
    '''

    balance_base = rmt_srv.balance(arg_dict['base_coin'])
    
    logging.info('base   coin: %s;  balance: %s', arg_dict['base_coin'],   balance_base)

    balance_target = rmt_srv.balance(arg_dict['target_coin'])
    logging.info('target coin: %s;  balance: %s', arg_dict['target_coin'], balance_target)
    
    close = [float(x) for x in df['close']]
    
    # 调用talib计算10日移动平均线的值
    df['MA10_talib'] = talib.MA(np.array(close), timeperiod=10) 

    # 调用talib计算MACD指标
    df['MACD'],df['MACDsignal'],df['MACDhist'] = talib.MACD(np.array(close), fastperiod=12, slowperiod=26, signalperiod=9) 

    #
    df['close'] = pd.Series(close)
    #print(df['close'])
    df['open'] = pd.Series([float(x) for x in df['open']])
    df['high'] = pd.Series([float(x) for x in df['high']]) 
    df['low'] = pd.Series([float(x) for x in df['low']])

    # 指标计算
    #MACD(df)
  
    ''' 
    high = [float(x) for x in df['high']]
    low = [float(x) for x in df['low']]

    df['KDJ_K'],df['KDJ_D']=talib.STOCH(np.array(high),np.array(low),np.array(close),
    	fastk_period=9,slowk_period=3,slowk_matype=0,slowd_period=3,slowd_matype=0)
    '''
    indicator.KDJ(df)
    
    '''
    df['open_time'] = [(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x/1000))) for x in df['open_time']]
    df['close_time'] = [(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x/1000))) for x in df['close_time']]

    del df['quote_asset_volume']
    del df['number_of_trades']
    del df['taker_buy_base_asset_volume']
    del df['taker_buy_quote_asset_volume']
    del df['ignore']
    print(df)
    '''

    kdj_k_cur = df['kdj_k'].values[-1] 
    kdj_d_cur = df['kdj_d'].values[-1] 
    kdj_j_cur = df['kdj_j'].values[-1]
    cur_price = close[-1]
    logging.info('current price: %f;  kdj_k: %f; kdj_d: %f; kdj: %f', cur_price, kdj_k_cur, kdj_d_cur, kdj_j_cur)

    target_free_count =float(balance_target['free'])
    target_frozen_count =float(balance_target['frozen'])
    if kdj_j_cur > kdj_k_cur+1 :
        if kdj_k_cur > kdj_d_cur+1 : # j>k>d 买入信号
            logging.info('j>k>d')
            if target_free_count > 0: # 持仓
                pass
            else:                     # 空仓
                cost_base_amount = min(float(balance_base['free']), base_coin_limit)
                logging.info('cost_base_amount: %f',cost_base_amount)

                if cost_base_amount > 0: #
                    buy_target_amount = reserve_float(cost_base_amount / cur_price, int(args.a))
                    logging.info('buy target coin amount: %f', buy_target_amount)
                    limit_buy_price = reserve_float(cur_price * 1.1, int(args.p))
                    order_id = rmt_srv.buy(limit_buy_price, buy_target_amount)
                    logging.info('current price: %f;  limit buy price: %f;  order_id: %f ',cur_price, limit_buy_price, order_id)
                    # send_report(orders, accounts, args.r, subject='Coin Trade  - %s' % pair)

                else:
                    pass
        else:                      # j>k<d
            pass
    elif kdj_j_cur < kdj_k_cur-1:
        if kdj_k_cur < kdj_d_cur-1 : # j<k<d 卖出信号
            logging.info('j<k<d')
            if target_frozen_count > 0: # 有挂单
                logging.info('target_frozen_count: %f', target_frozen_count)
            else:                       # 无挂单
                if target_free_count > 0: # 持仓
                    logging.info('sell target coin num: %f',target_free_count)
                    limit_sell_price = reserve_float(cur_price * 0.9, int(args.p))
                    sell_target_amount = reserve_float(target_free_count, int(args.a))
                    order_id = rmt_srv.sell(limit_sell_price, sell_target_amount)
                    logging.info('current price: %f;  limit sell price: %f;  order_id: %f',cur_price, limit_sell_price, order_id)
 
                else:                     # 空仓
                    pass 
        else:                      # j<k>d
            pass
 

if __name__ == "__main__":

    parser=common_lib.get_common_cmd_parser()
    parser.add_argument('-limit', help='base coin limit')
    
    args = parser.parse_args()
    print(args)

    logfilename = 'log_' + args.t + '_' + args.b + '_' + args.i + '.log'
    logging.basicConfig(level=logging.NOTSET, filename=logfilename)

    base_coin_limit = float(args.limit)

    rmt_srv,arg_dict = common_lib.get_common_args(args)

    while True:
        tickStart = datetime.datetime.now() 
        logging.info('%s OnTick start...', tickStart)
        OnTick()
        tickEnd = datetime.datetime.now()
        logging.info('%s OnTick end...; tick  cost: %s', tickEnd, tickEnd-tickStart)
        time.sleep(int(args.s))
