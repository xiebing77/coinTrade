#!/usr/bin/python
from common.db_table import *


def init_database():
    CoinOrder.createTable(ifNotExists=True)
    Account.createTable(ifNotExists=True)


def insert_order(order):
    CoinOrder(
        order_id=order['order_id'],
        symbol=order['symbol'],
        create_date=order['create_date'],
        type=order['type'],
        price=order['price'],
        avg_price=order['avg_price'],
        amount=order['amount'],
        deal_amount=order['deal_amount'],
        status=order['status']
    )


def delete_order(order_id):
    pass


def update_order(order_id):
    pass


def get_order(order_id):
    pass


if __name__ == "__main__":
    CoinOrder.createTable(ifNotExists=True)
    Account.createTable(ifNotExists=True)
    # dpy = Account(date='2018-3-12', coin='dpy', balance='2.222')
    print(os.path.realpath(__file__))
    print(os.path.dirname(os.path.realpath(__file__)))
