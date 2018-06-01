#!/bin/bash

# -a target amount digits
# -d base amount digits
# -p price digits
# -g price gap
# -n price gap num
# -r target coin reserve
# -s base coin reserve

source ~/.profile

#/usr/bin/python ~/coinTrade/binance/main.py -t eth -b usdt -a 3 -d 2 -p 2 -g 0.04 -n 10 -r 0 -s 0

#/usr/bin/python ~/coinTrade/binance/main.py -t eos -b usdt -a 2 -d 2 -p 3 -g 0.04 -n 10 -r 0 -s 0

#/usr/bin/python ~/coinTrade/binance/main.py -t blz -b eth -a 0 -d 8 -p 8 -g 0.04 -n 8 -r 2500 -s 0

/usr/bin/python ~/coinTrade/binance/main.py -t wan -b eth -a 0 -d 8 -p 6 -g 0.04 -n 5 -r 300 -s 0
