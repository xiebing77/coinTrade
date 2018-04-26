#!/usr/bin/python
import datetime
from setup import *
import okex.spot_obj as spot_obj
from common import db_api
from policy import send_report
from common.lib import reserve_float
from conf import FLOAT_DIGITS

PROFIT_RATIO = 0.1
FEE_RATIO = 0.002

if __name__ == "__main__":
    pair = 'dpy_eth'
    target_coin = 'dpy'
    base_coin = 'eth'
    ok_spot = spot_obj.RmtSrvObj(pair, '1day', 7, debug=True)
    update_flag = False

    # check if any order is dealt
    print('Check if any order is dealt')
    orders = db_api.get_pending_orders()
    for item in orders:
        order = ok_spot.get_order(item['order_id'])
        # print(item['order_id'])
        # order['status'] = 'Dealt'
        # order['deal_amount'] = item['amount']
        # order['avg_price'] = order['price']
        if order is None:
            print("Not find order from exchanger, need to delete it in database: " + item)
        elif order['status'] == 'Dealt':
            print(order)
            amount = reserve_float(order['deal_amount'] * (1 - FEE_RATIO))
            # print(amount)
            db_api.update_order(order)
            if amount < 10:
                continue
            update_flag = True
            print('%s order is dealt: pair(%s), price(%s), amount(%s)' % (order['type'], pair, order['avg_price'],
                                                                          order['deal_amount']))
            if order['type'] == 'buy':
                price = reserve_float(order['avg_price'] * (1 + PROFIT_RATIO), FLOAT_DIGITS)
                order_id = ok_spot.sell(price, amount)
            else:
                price = reserve_float(order['avg_price'] * (1 - PROFIT_RATIO), FLOAT_DIGITS)
                new_amount = reserve_float(order['avg_price'] * amount / price)
                order_id = ok_spot.buy(price, new_amount)

            if order_id is not None:
                # insert new order into database
                db_api.insert_order(ok_spot.get_order(order_id))

    # insert new account snapshot in database
    if update_flag:
        print('Updating account...')
        for i in ok_spot.get_available_coins():
            db_api.insert_account(i)

        # send report
        print('Sending report...')
        # local time is a little different from server time
        end_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        begin_time = end_time - datetime.timedelta(days=3)
        orders = db_api.get_orders_by_time(begin_time.timestamp(), end_time.timestamp())
        accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
        send_report(orders, accounts, email_receiver)
