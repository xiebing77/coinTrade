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
    CoinOrder.deleteBy(order_id=order_id)


def copy_order(from_order, to_order):
    to_order.order_id = from_order.order_id
    to_order.symbol = from_order.symbol
    to_order.create_date = from_order.create_date
    to_order.type = from_order.type
    to_order.price = from_order.price
    to_order.avg_price = from_order.avg_price
    to_order.amount = from_order.amount
    to_order.deal_amount = from_order.deal_amount
    to_order.status = from_order.status


def update_order(order):
    ret = get_order(order.order_id)
    if len(ret) == 0:
        insert_order(order)
    else:
        org_order = ret[0]
        copy_order(order, org_order)


def get_order(order_id):
    ret = CoinOrder.selectBy(order_id=order_id)
    if len(list(ret)) == 0:
        return None
    order = {}
    order_obj = ret[0]
    for i in order_obj.sqlmeta.columns.keys():
        order[i] = eval('order_obj.%s' % i)
    return order


if __name__ == "__main__":
    CoinOrder.createTable(ifNotExists=True)
    Account.createTable(ifNotExists=True)
    # dpy = Account(date='2018-3-12', coin='dpy', balance='2.222')
    print(os.path.realpath(__file__))
    print(os.path.dirname(os.path.realpath(__file__)))
