#!/usr/bin/python

from common.base_obj import BaseObj
from okex.OkcoinSpotAPI import OKCoinSpot
import json
import os
from datetime import datetime
import pandas as pd

api_key = os.environ.get('OKEX_API_KEY')
secret_key = os.environ.get('OKEX_SECRET_KEY')
rest_url = 'www.okex.com'
# rest_url = '104.25.20.25'


class RmtSrvObj(BaseObj):
    def __init__(self, symbol, line_type, size=0, since='', debug=False, balance_min=0.01):
        self.rmt_srv_obj = OKCoinSpot(rest_url, api_key, secret_key)
        self.balance_min = balance_min
        super(RmtSrvObj, self).__init__(symbol, line_type, size, since, debug)

    def get_kline(self):
        kline = self.rmt_srv_obj.get_kline(self.symbol, self.type, self.size, self.since)
        df = pd.DataFrame(kline,columns=['open_time', 'open','high','low','close','volume'])
        return df

    def get_account(self):
        user = json.loads(self.rmt_srv_obj.userinfo())
        regular_user = {'free': user['info']['funds']['free'], 'frozen': user['info']['funds']['freezed']}
        return regular_user

    def get_balance(self, coin):
        free = self.account['free']
        frozen = self.account['frozen']
        free_coin = float(free[coin])
        frozen_coin = float(frozen[coin])
        balance = free_coin + frozen_coin
        return {'coin': coin, 'free': free_coin, 'frozen': frozen_coin, 'balance': balance}

    def get_available_coins(self):
        free = self.account['free']
        frozen = self.account['frozen']
        coins = []
        for coin in free:
            free_coin = float(free[coin])
            frozen_coin = float(frozen[coin])
            balance = free_coin + frozen_coin
            if balance > self.balance_min:
                coins.append({'coin': coin, 'free': free_coin, 'frozen': frozen_coin, 'balance': balance})
        return coins

    def get_order(self, order_id):
        ret = json.loads(self.rmt_srv_obj.orderinfo(self.symbol, order_id))['orders']
        if not ret:
            return None

        order = ret[0]
        new_order = {}
        if order['status'] == -1:
            new_order['status'] = 'Cancelled'
        elif order['status'] == 0:
            new_order['status'] = 'Not deal'
        elif order['status'] == 1:
            new_order['status'] = 'Part dealt'
        elif order['status'] == 2:
            new_order['status'] = 'Dealt'
        elif order['status'] == 3:
            new_order['status'] = 'Cancelling'
        else:
            new_order['status'] = 'Error'

        new_order['symbol'] = order['symbol']
        new_order['type'] = order['type']
        new_order['timestamp'] = order['create_date']/1000
        new_order['create_date'] = datetime.fromtimestamp(order['create_date']/1000).strftime("%Y-%m-%d %H:%M:%S")
        new_order['order_id'] = str(order['order_id'])
        new_order['amount'] = str(order['amount'])
        new_order['avg_price'] = str(order['avg_price'])
        new_order['deal_amount'] = str(order['deal_amount'])
        new_order['price'] = str(order['price'])
        return new_order

    def buy(self, price, amount):
        self.debug('Buy order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = json.loads(self.rmt_srv_obj.trade(self.symbol, 'buy', price=str(price), amount=str(amount)))
        # self.debug(ret)
        try:
            if ret['result']:
                # self.debug('Return buy order ID: %s' % ret['order_id'])
                return ret['order_id']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def sell(self, price, amount):
        self.debug('Sell order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))
        ret = json.loads(self.rmt_srv_obj.trade(self.symbol, 'sell', price=str(price), amount=str(amount)))
        # self.debug(ret)
        try:
            if ret['result']:
                # self.debug('Return sell order ID: %s' % ret['order_id'])
                return ret['order_id']
            else:
                self.debug('Place order failed')
                return None
        except Exception:
            self.debug('Error result: %s' % ret)
            return None

    def cancel_orders(self):
        orders = json.loads(self.rmt_srv_obj.orderinfo(self.symbol, '-1'))['orders']
        for order in orders:
            self.rmt_srv_obj.cancelOrder(self.symbol, order['order_id'])

