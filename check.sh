#!/bin/bash

# -a target amount digits
# -p price digits
# -r profit ratio
# -f fee ratio
# -e exchange name

source ~/.profile

base_dir=$(cd `dirname $0`; pwd)

#python $base_dir/check.py -t eth -b usdt -a 3 -p 2 -r 0.08 -f 0.001 -e binance
#python $base_dir/check.py -t eos -b usdt -a 2 -p 3 -r 0.05 -f 0.001 -e binance
#python $base_dir/check.py -t wan -b eth -a 0 -p 8 -r 0.1 -f 0.001 -e binance
python $base_dir/check.py -t blz -b eth -a 0 -p 8 -r 0.05 -f 0.001 -e binance
python $base_dir/check.py -t dpy -b eth -a 0 -p 8 -r 0.08 -f 0.001 -e okex
python $base_dir/check.py -t lba -b eth -a 0 -p 8 -r 0.08 -f 0.001 -e okex
