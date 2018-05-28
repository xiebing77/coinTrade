#!/bin/bash

# -a target amount digits
# -p price digits
# -r profit ratio
# -f fee ratio

source ~/.profile
/usr/bin/python ~/coinTrade/binance/check.py -t eth -b usdt -a 3 -p 2 -r 0.05 -f 0.001

/usr/bin/python ~/coinTrade/binance/check.py -t eos -b usdt -a 2 -p 3 -r 0.05 -f 0.001

/usr/bin/python ~/coinTrade/binance/check.py -t blz -b eth -a 0 -p 8 -r 0.05 -f 0.001
