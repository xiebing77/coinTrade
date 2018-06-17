#!/bin/bash

# -t target coin
# -b base coin
# -e exchange name

source ~/.profile

base_dir=$(cd `dirname $0`; pwd)

python3.6 $base_dir/calc_revenue.py -t blz -b eth -e binance
python3.6 $base_dir/calc_revenue.py -t lba -b eth -e okex
