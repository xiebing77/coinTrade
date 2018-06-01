#!/usr/bin/python
import time

from binance.enums import KLINE_INTERVAL_1DAY
from binance.rmt_srv import RmtSrvObj
from common.lib import reserve_float

PRICE_GAP = 0.04
PRICE_GAP_NUM = 10


class Policy(object):
    def __init__(self, db_api, rmt_srv, target_coin, base_coin,
                 target_amount_digits, base_amount_digits, price_digits,
                 price_gap=PRICE_GAP, price_gap_num=PRICE_GAP_NUM,
                 base_coin_reserve=0, target_coin_reserve=0):
        self.db_api = db_api
        self.rmt_srv = rmt_srv
        self.target_coin = target_coin
        self.base_coin = base_coin
        self.target_amount_digits = target_amount_digits
        self.base_amount_digits = base_amount_digits
        self.price_digits = price_digits
        self.base_coin_reserve = base_coin_reserve
        self.target_coin_reserve = target_coin_reserve
        self.price_gap = []
        for i in range(1, price_gap_num + 1):
            self.price_gap.append(price_gap * i)

    def run_policy(self):
        self.sell_policy()
        self.buy_policy()

    def buy_policy(self):
        """
        coin: base coin, like USDT
        """
        print('Begin to send buy order...')
        medium_price = self.rmt_srv.medium_price
        current_price = self.rmt_srv.current_price
        # base_price = min(medium_price, current_price)
        base_price = current_price
        print('Medium price: %s' % medium_price)
        print('Current price: %s' % current_price)

        total = float(self.rmt_srv.balance(self.base_coin)['free']) - self.base_coin_reserve
        base_amount = reserve_float(total / len(self.price_gap), self.base_amount_digits)

        for i in self.price_gap:
            try:
                price = reserve_float(base_price * (1 - i), self.price_digits)
                amount = reserve_float(base_amount/price, self.target_amount_digits)
                if amount == 0:
                    print("amount is 0")
                    return
                order_id = self.rmt_srv.buy(price, amount)
                if order_id is None:
                    continue
                # insert new order into database
                time.sleep(0.5)
                self.db_api.insert_order(self.rmt_srv.get_order(order_id))
            except Exception as e:
                print(e)
                continue
        return

    def sell_policy(self):
        """
        coin: target coin, like ETH
        """
        print('Begin to send sell order...')
        medium_price = self.rmt_srv.medium_price
        current_price = self.rmt_srv.current_price
        base_price = max(medium_price, current_price)
        # base_price = current_price
        print('Medium price: %s' % medium_price)
        print('Current price: %s' % current_price)

        total = float(self.rmt_srv.balance(self.target_coin)['free']) - self.target_coin_reserve
        amount = reserve_float(total / len(self.price_gap), self.target_amount_digits)
        if amount == 0:
            print("amount is 0")
            return

        for i in self.price_gap:
            try:
                price = reserve_float(base_price * (1 + i), self.price_digits)
                order_id = self.rmt_srv.sell(price, amount)
                if order_id is None:
                    continue
                # insert new order into database
                time.sleep(0.5)
                self.db_api.insert_order(self.rmt_srv.get_order(order_id))
            except Exception as e:
                print(e)
                continue


if __name__ == "__main__":
    pair = 'ETHUSDT'
    target_coin = 'ETH'
    base_coin = 'USDT'
    # create a new instance
    rmt_srv = RmtSrvObj(pair, line_type=KLINE_INTERVAL_1DAY, size=7, debug=True)
    db_url = "mongodb://localhost:27017/"
    db_name = "binance"
    db_api = DbApi(db_url, db_name)
    policy = Policy(db_api, rmt_srv=rmt_srv, target_coin=target_coin,
                    base_coin=base_coin, target_amount_digits=3,
                    base_amount_digits=2, price_digits=2
                    )

    policy.sell_policy()
    # buy_policy(okSpot, 8, base_coin)
    # print(okSpot.balance('dpy'))
    # print(okSpot.balance('eth'))
    # init_database()
    # order = okSpot.get_order('3229114')
    # print(order)
    # order = db_api.get_order('3229114')
    # print(order)
    # account = db_api.get_account()
    # print(account)
    # order['symbol'] = 'gw_eth'

    # db_api.update_order(order)
    # for i in order[0]:
    #     print(i)
    # # order[0].symbol = 'btc_eth'
    # orders = [order]
    # send_report(orders, account, 'test', 'pkguowu@yahoo.com')
    # insert_order(order)
    # okSpot.cancel_orders()
    # print(okSpot.get_order('3071976'))
    # orders = db_api.get_pending_orders()
    # print(orders)
