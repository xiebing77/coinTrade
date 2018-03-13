#!/usr/bin/python
import os

location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

db_name = location('database/main.db')
