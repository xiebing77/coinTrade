#!/usr/bin/python
from datetime import datetime
import time
from pymongo import MongoClient


class DbApi(object):
    def __init__(self, url, db_name, user, pwd):
        client = MongoClient(url)
        self.db = eval('%s.%s' % (client, db_name))
        self.db.authenticate(user, pwd)

    def insert_order(self, order):
        collection = self.db.order
        collection.insert(order)

    def delete_order(self, symbol, order_id):
        collection = self.db.order
        collection.remove({'symbol': symbol, "order_id": order_id})

    def update_order(self, order):
        collection = self.db.order
        collection.update({'symbol': order['symbol'], "order_id": order['order_id']}, order)

    def get_orders_by_time(self, symbol, begin, end=None):
        collection = self.db.order
        if end is None:
            end = time.time()
        ret = collection.find({'symbol': symbol, "timestamp": {"$gte": begin, "$lte": end}}).sort('timestamp', -1)
        orders = []
        for i in ret:
            del(i['_id'])
            del(i['timestamp'])
            del(i['avg_price'])
            del(i['order_id'])
            orders.append(i)
        return orders

    def get_accounts_by_time(self, begin, end=None, coins=None):
        collection = self.db.account
        if end is None:
            end = time.time()

        if coins is None:
            query = {"timestamp": {"$gte": begin, "$lte": end}}
        else:
            coins_list = []
            for coin in coins:
                coins_list.append({"coin": coin})
            query = {"timestamp": {"$gte": begin, "$lte": end}, "$or": coins_list}
        ret = collection.find(query).sort('timestamp', -1)
        accounts = []
        for i in ret:
            del(i['_id'])
            del(i['timestamp'])
            accounts.append(i)
        return accounts

    def get_orders(self, query):
        collection = self.db.order
        ret = collection.find(query)
        return ret

    def get_pending_orders(self, symbol):
        collection = self.db.order
        ret = collection.find({'symbol': symbol,
                              '$and': [{'status': {'$ne': 'Cancelled'}}, {'status': {'$ne': 'Dealt'}}]})
        return ret

    def get_order(self, symbol, order_id):
        """
        return a dict
        """
        collection = self.db.order
        ret = collection.find({'symbol': symbol, "order_id": order_id})
        return ret

    def insert_account(self, account):
        collection = self.db.account
        timestamp = time.time()
        collection.insert({"timestamp": timestamp,
                           "data": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                           "coin": account["coin"],
                           "balance": account["balance"]})

