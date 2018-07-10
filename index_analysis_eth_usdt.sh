#!/bin/bash

# -a target amount digits
# -d base amount digits
# -p price digits
# -g price gap
# -n price gap num
# -r target coin reserve
# -s base coin reserve
# -e exchange name

source ~/.profile
base_dir=$(cd `dirname $0`; pwd)

python3.6 $base_dir/index_analysis.py -t eth -b usdt -a 4 -d 2 -p 2 -e binance -s 600 -limit 100 -i 1
