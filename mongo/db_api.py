#!/usr/bin/python
from datetime import datetime
import time
from pymongo import MongoClient


class DbApi(object):
    def __init__(self, url, db_name):
        client = MongoClient(url)
        self.db = eval('%s.%s' % (client, db_name))

    def insert_order(self, order):
        collection = self.db.order
        collection.insert(order)

    def delete_order(self, order_id):
        collection = self.db.order
        collection.remove({"order_id": order_id})

    def update_order(self, order):
        collection = self.db.order
        collection.update({"order_id": order['order_id']}, order)

    def get_orders_by_time(self, begin, end=None):
        collection = self.db.order
        if end is None:
            end = time.time()
        ret = collection.find({"timestamp": {"$gte": begin, "$lte": end}})
        orders = []
        for i in ret:
            del(i['_id'])
            orders.append(i)
        return orders

    def get_accounts_by_time(self, begin, end=None):
        collection = self.db.account
        if end is None:
            end = time.time()
        ret = collection.find({"timestamp": {"$gte": begin, "$lte": end}})
        accounts = []
        for i in ret:
            del(i['_id'])
            accounts.append(i)
        return accounts

    def get_pending_orders(self):
        collection = self.db.order
        ret = collection.find({"status": {"$ne": ["Cancelled", "Dealt"]}})
        return ret

    def get_order(self, order_id):
        """
        return a dict
        """
        collection = self.db.order
        ret = collection.find({"order_id": order_id})
        return ret

    def insert_account(self, account):
        collection = self.db.account
        timestamp = time.time()
        collection.insert({"timestamp": timestamp,
                           "data": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                           "coin": account["coin"],
                           "balance": account["balance"]})


# if __name__ == "__main__":
#     db_api = DbApi("mongodb://localhost:27017/", 'binance')
#     acnt = {"coin": "ETH", "balance": 2000}
#     db_api.insert_account(acnt)
#     for i in db_api.get_accounts_by_time(1527402298):
#         print(i)