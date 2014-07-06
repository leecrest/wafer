# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/25 23:27
@brief  : 
"""

import redis

r = redis.Redis(host="localhost", port=6379, db=2)
print r.hget("role", 1101)


