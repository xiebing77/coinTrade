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


def update_obj(from_item, to_obj):
    for i in from_item:
        exec('to_obj.%s = from_item["%s"]' % (i, i))


def update_order(order):
    org_order = get_order_obj(order['order_id'])
    if org_order is None:
        insert_order(order)
    else:
        update_obj(order, org_order)


def get_order_obj(order_id):
    """
    return an CoinOrder obj
    """
    ret = CoinOrder.selectBy(order_id=order_id)
    if len(list(ret)) == 0:
        return None
    else:
        return ret[0]


def get_order(order_id):
    """
    return a dict
    """
    ret = CoinOrder.selectBy(order_id=order_id)
    if len(list(ret)) == 0:
        return None
    order = {}
    order_obj = ret[0]
    for i in order_obj.sqlmeta.columns.keys():
        order[i] = eval('order_obj.%s' % i)
    return order


def get_account():
    ret = Account.select()
    if len(list(ret)) == 0:
        return None

    accounts = []
    for account_obj in ret:
        account = {}
        for i in account_obj.sqlmeta.columns.keys():
            account[i] = eval('account_obj.%s' % i)
        accounts.append(account)
    return accounts


if __name__ == "__main__":
    CoinOrder.createTable(ifNotExists=True)
    Account.createTable(ifNotExists=True)
    # dpy = Account(date='2018-3-12', coin='eth', balance='2.222')
    print(os.path.realpath(__file__))
    print(os.path.dirname(os.path.realpath(__file__)))
    print(get_account())
