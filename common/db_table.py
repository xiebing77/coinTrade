#!/usr/bin/python
import os
from sqlobject import *
from sqlobject.sqlite import builder
from setup import *

conn = builder()(db_name)


class CoinOrder(SQLObject):
    _connection = conn
    order_id = StringCol(alternateID=True)  #unique
    symbol = StringCol()
    create_date = StringCol()
    type = StringCol()
    price = StringCol()
    avg_price = StringCol()
    amount = StringCol()
    deal_amount = StringCol()
    status = StringCol()


class Account(SQLObject):
    _connection = conn
    date = StringCol()
    coin = StringCol()
    balance = StringCol()


if __name__ == "__main__":
    CoinOrder.createTable(ifNotExists=True)
    Account.createTable(ifNotExists=True)
    # dpy = Account(date='2018-3-12', coin='dpy', balance='2.222')
    print(os.path.realpath(__file__))
    print(os.path.dirname(os.path.realpath(__file__)))
