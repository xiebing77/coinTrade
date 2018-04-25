from datetime import datetime


class BaseObj(object):
    """
    define the common API
    """
    def __init__(self, symbol, line_type, size=0, since='', debug=False):
        """
        :param symbol:
        :param line_type:
            1min
            3min
            5min
            15min
            30min
            1day
            3day
            1week
            1hour
            2hour
            4hour
            6hour
            12hour
        :param size: Integer
        :param since: Long
        """
        self.symbol = symbol
        self.type = line_type
        self.size = size
        self.since = since
        self.debug_flag = debug
        self.kline = self.get_kline()
        self.account = self.get_account()
        self.top_price = self.get_top_price()
        self.bottom_price = self.get_bottom_price()
        self.medium_price = self.get_medium_price()
        self.current_price = self.get_current_price()

    def update_account(self):
        self.account = self.get_account()

    def get_kline(self):
        """
        :return:
        list[0]: UTC
        list[1]: start price
        list[2]: top price
        list[3]: bottom price
        list[4]: close price
        list[5]: volume
        """
        return []

    def get_account(self):
        return {}

    def debug(self, string):
        if self.debug_flag is True:
            print(string)

    # def get_top_price(self):
    #     p = float(self.kline[0][2])
    #     for i in self.kline:
    #         tmp = float(i[2])
    #         date = datetime.fromtimestamp(int(i[0])/1000).strftime("%Y-%m-%d %H:%M:%S")
    #         self.debug("%s: top price is %s" % (date, tmp))
    #         if p < tmp:
    #             p = tmp
    #     return p
    #
    # def get_bottom_price(self):
    #     p = float(self.kline[0][3])
    #     for i in self.kline:
    #         tmp = float(i[3])
    #         date = datetime.fromtimestamp(int(i[0])/1000).strftime("%Y-%m-%d %H:%M:%S")
    #         self.debug("%s: bottom price is %s" % (date, tmp))
    #         if p > tmp:
    #             p = tmp
    #     return p

    # get top close price
    def get_top_price(self):
        pos = self.kline[0]
        p = float(pos[4])
        for i in self.kline:
            tmp = float(i[4])
            if p < tmp:
                p = tmp
                pos = i
        date = datetime.fromtimestamp(int(pos[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        self.debug("%s: top price is %s" % (date, p))
        return p

    # get bottom close price
    def get_bottom_price(self):
        pos = self.kline[0]
        p = float(pos[4])
        for i in self.kline:
            tmp = float(i[4])
            if p > tmp:
                p = tmp
                pos = i
        date = datetime.fromtimestamp(int(pos[0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        self.debug("%s: bottom price is %s" % (date, p))
        return p

    def get_medium_price(self):
        return (self.top_price + self.bottom_price)/2

    def get_current_price(self):
        return float(self.kline[-1][4])

    def buy(self, price, amount):
        self.debug('Order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))

    def sell(self, price, amount):
        self.debug('Order: pair(%s), price(%s), amount(%s)' % (self.symbol, price, amount))

    def balance(self, coin=''):
        balance = {'free': self.account['free'][coin], 'frozen': self.account['frozen'][coin]}
        return balance

    def get_order(self, order_id):
        pass

    def history_orders(self, ):
        pass

    def cancel_orders(self):
        pass
