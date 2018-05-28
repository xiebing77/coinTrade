#!/bin/bash

source ~/.profile
/usr/bin/python ~/coinTrade/binance/main.py -t eth -b usdt -a 3 -d 2 -p 2 -g 0.04 -n 10 -r 0 -s 0

/usr/bin/python ~/coinTrade/binance/main.py -t blz -b eth -a 0 -d 8 -p 8 -g 0.04 -n 10 -r 2500 -s 0
