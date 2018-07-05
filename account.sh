#!/bin/bash

source ~/.profile
base_dir=$(cd `dirname $0`; pwd)
python3.6 $base_dir/summary.py -e binance
python3.6 $base_dir/summary.py -e okex
