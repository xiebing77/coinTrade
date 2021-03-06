#!/usr/bin/python

from common.base_obj import BaseObj
from binance.enums import *
from binance.client import Client
import os
from datetime import datetime
import pandas as pd

api_key = os.environ.get('BINANCE_API_KEY')
secret_key = os.environ.get('BINANCE_SECRET_KEY')


class RmtSrvObj(BaseObj):
    def __init__(self, symbol, line_type, size=0, since='', debug=False, balance_min=0.01):
        self.rmt_srv_obj = Client(api_key, secret_key)
        self.balance_min = balance_min
        super(RmtSrvObj, self).__init__(symbol, line_type, size, since, debug)

    def get_kline(self):
        return self.rmt_srv_obj.get_klines(symbol=self.symbol, interval=self.type,limit=self.size)

    def get_kline_pd(self):
        return pd.DataFrame(self.get_kline(),columns=['open_time', 'open','high','low','close','volume','close_time',
            'quote_asset_volume','number_of_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume','ignore'])

    def balance(self, coin=''):
        balance = {'free': 0, 'frozen': 0}
        for item in self.account:
            if coin == item['asset']:
                balance = {'free': item['free'], 'frozen': item['locked']}
                break
        return balance

    """
    'balances': 
    [{'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'}, 
    {'asset': 'ETH', 'free': '0.43767306', 'locked': '2.74720975'}, 
    {'asset': 'ICO', 'free': '0.00000000', 'locked': '0.00000000'}]
    """
    def get_account(self):
        user = self.rmt_srv_obj.get_account()
        # print(user)
        regular_user = user['balances']
        return regular_user

    def get_balance(self, coin):
        coin_info = {'coin': coin, 'free': 0, 'frozen': 0, 'balance': 0}
        for item in self.account:
            if item['asset'] == coin:
                coin_info['free'] = float(item['free'])
                coin_info['frozen'] = float(item['locked'])
                coin_info['balance'] = coin_info['free'] + coin_info['frozen']
                break
        return coin_info

    def get_available_coins(self):
        coins = []
        for item in self.account:
            free_coin = float(item['free'])
            frozen_coin = float(item['locked'])
            balance = free_coin + frozen_coin
            if balance > self.balance_min:
                coins.append({'coin': item['asset'], 'free': free_coin, 'frozen': frozen_coin, 'balance': balance})
        return coins

    def get_all_orders(self):
        return self.rmt_srv_obj.get_all_orders(symbol=self.symbol)

    def get_order(self, order_id):
        order = self.rmt_srv_obj.get_order(symbol=self.symbol, orderId=order_id)
        if not order:
            return None

        new_order = {}
        if order['status'] == 'CANCELED':
            new_order['status'] = 'Cancelled'
        elif order['status'] == 'NEW':
            new_order['status'] = 'Not deal'
        elif order['status'] == 'PARTIALLY_FILLED':
            new_order['status'] = 'Part dealt'
        elif order['status'] == 'FILLED':
            new_order['status'] = 'Dealt'
        elif order['status'] == 'REJECTED':
            new_order['status'] = 'Rejected'
        elif order['status'] == 'EXPIRED':
            new_order['status'] = 'Expired'
        else:
            new_order['status'] = 'Error'

        if order['side'] == 'BUY':
            new_order['type'] = 'buy'
        else:
            new_order['type'] = 'sell'
        new_order['symbol'] = order['symbol']
        new_order['timestamp'] = order['time']/1000
        new_order['create_date'] = datetime.fromtimestamp(new_order['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        new_order['order_id'] = str(order['orderId'])
        new_order['amount'] = order['origQty']
        new_order['avg_price'] = order['price']
        new_order['deal_amount'] = order['executedQty']
        new_order['price'] = order['price']
        return new_order

    def buy(self, price, amount):
        self.debug('Buy order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = self.rmt_srv_obj.create_order(symbol=self.symbol, side=SIDE_BUY,
                                            type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC,
                                            price=price, quantity=amount)
        # self.debug(ret)
        try:
            if ret['orderId']:
                # self.debug('Return buy order ID: %s' % ret['orderId'])
                return ret['orderId']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def sell(self, price, amount):
        self.debug('Sell order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = self.rmt_srv_obj.create_order(symbol=self.symbol, side=SIDE_SELL,
                                            type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC,
                                            price=price, quantity=amount)
        # self.debug(ret)
        try:
            if ret['orderId']:
                # self.debug('Return sell order ID: %s' % ret['orderId'])
                return ret['orderId']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def cancel_orders(self):
        orders = self.rmt_srv_obj.get_open_orders(symbol=self.symbol)
        for order in orders:
            self.rmt_srv_obj.cancel_order(symbol=self.symbol, orderId=order['orderId'])
