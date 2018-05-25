#!/usr/bin/python

from common.base_obj import BaseObj
from binance.enums import *
from binance.client import Client
import json
import os
from datetime import datetime

api_key = os.environ.get('BINANCE_API_KEY')
secret_key = os.environ.get('BINANCE_SECRET_KEY')


class RmtSrvObj(BaseObj):
    def __init__(self, symbol, line_type, size=0, since='', debug=False):
        self.rmt_srv_obj = Client(api_key, secret_key)
        super(RmtSrvObj, self).__init__(symbol, line_type, size, since, debug)

    def get_kline(self):
        return self.rmt_srv_obj.get_klines(symbol=self.symbol, interval=self.type,
                                           limit=self.size)

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

    def get_available_coins(self):
        coins = []
        for item in self.account:
            free_coin = float(item['free'])
            frozen_coin = float(item['locked'])
            balance = free_coin + frozen_coin
            if balance:
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
        new_order['create_date'] = datetime.fromtimestamp(new_order['timestamp']/1000).strftime("%Y-%m-%d %H:%M:%S")
        new_order['order_id'] = str(order['orderId'])
        new_order['amount'] = order['origQty']
        new_order['avg_price'] = order['price']
        new_order['deal_amount'] = order['executedQty']
        new_order['price'] = order['price']
        return new_order

    def buy(self, price, amount):
        self.debug('Buy order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = json.loads(self.rmt_srv_obj.create_order(symbol=self.symbol, side=SIDE_BUY,
                                                       type=ORDER_TYPE_LIMIT, price=price, quantity=amount))
        self.debug(ret)
        try:
            if ret['result']:
                self.debug('Return buy order ID: %s' % ret['order_id'])
                return ret['order_id']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def sell(self, price, amount):
        self.debug('Sell order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = json.loads(self.rmt_srv_obj.create_order(symbol=self.symbol, side=SIDE_SELL,
                                                       type=ORDER_TYPE_LIMIT_MAKER, price=price, quantity=amount))
        self.debug(ret)
        try:
            if ret['result']:
                self.debug('Return sell order ID: %s' % ret['order_id'])
                return ret['order_id']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def cancel_orders(self):
        orders = json.loads(self.rmt_srv_obj.get_all_orders(symbol=self.symbol))['orders']
        for order in orders:
            self.rmt_srv_obj.cancel_order(symbol=self.symbol, orderId=order['order_id'])

