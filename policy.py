#!/usr/bin/python
from okex.spot_obj import SpotClass as okexSpotClass
from common.db_api import *

PRICE_GAP = 0.05
PRICE_RATIO_1 = PRICE_GAP
PRICE_RATIO_2 = PRICE_GAP * 2
PRICE_RATIO_3 = PRICE_GAP * 3
PRICE_RATIO_4 = PRICE_GAP * 4
PARTITION_NUM = 4
MIN_COIN_AMOUNT = 10
BASE_COIN_RESERVE = 0
TARGET_COIN_RESERVE = 700

SELL_BATCH_RATIO = [PRICE_RATIO_1, PRICE_RATIO_2, PRICE_RATIO_3, PRICE_RATIO_4]
BUY_BATCH_RATIO = [PRICE_RATIO_1, PRICE_RATIO_2, PRICE_RATIO_3, PRICE_RATIO_4]


def buy_policy(spot_instance, float_digits, coin):
    """
    coin: base coin, like ETH
    """
    print('Begin to send buy order...')
    medium_price = spot_instance.medium_price
    current_price = spot_instance.current_price
    base_price = min(medium_price, current_price)
    print('Medium price: %s' % medium_price)
    print('Current price: %s' % current_price)

    total = float(spot_instance.balance(coin)['free']) - BASE_COIN_RESERVE
    rest = total

    for i in BUY_BATCH_RATIO:
        price = round(base_price * (1 - i), float_digits)
        if rest < MIN_COIN_AMOUNT * price:
            return
        amount = round(max(round(total/(len(BUY_BATCH_RATIO) * price)), MIN_COIN_AMOUNT))
        order_id = spot_instance.buy(price, round(min(rest/price, amount)))
        if order_id is None:
            continue
        # insert new order into database
        insert_order(spot_instance.get_order(order_id))
        rest -= amount * price
    return


def sell_policy(spot_instance, float_digits, coin):
    """
    coin: target coin, like DPY
    """
    print('Begin to send sell order...')
    medium_price = spot_instance.medium_price
    current_price = spot_instance.current_price
    base_price = max(medium_price, current_price)
    print('Medium price: %s' % medium_price)
    print('Current price: %s' % current_price)

    total = float(spot_instance.balance(coin)['free']) - TARGET_COIN_RESERVE
    rest = total

    if rest < MIN_COIN_AMOUNT:
        return
    amount = round(max(round(total/len(SELL_BATCH_RATIO), float_digits), MIN_COIN_AMOUNT))
    for i in SELL_BATCH_RATIO:
        price = round(base_price * (1 + i), float_digits)
        order_id = spot_instance.sell(price, round(min(rest, amount)))
        if order_id is None:
            continue
        # insert new order into database
        insert_order(spot_instance.get_order(order_id))
        rest -= amount
        if rest < MIN_COIN_AMOUNT:
            return


if __name__ == "__main__":
    pair = 'dpy_eth'
    target_coin = 'dpy'
    base_coin = 'eth'
    # create a new instance
    okSpot = okexSpotClass(pair, '1day', 7, debug=True)
    sell_policy(okSpot, 8, target_coin)
    # buy_policy(okSpot, 8, base_coin)
    # print(okSpot.balance('dpy'))
    # print(okSpot.balance('eth'))
    # init_database()
    order = okSpot.get_order('3174391')
    print(order)
    # insert_order(order)
