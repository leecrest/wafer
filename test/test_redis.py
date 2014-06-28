# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/25 23:27
@brief  : 
"""

import redis

r = redis.Redis(host="localhost", port=6379, db=1)

r.hsetnx("Test", "ID", 1001)
b = r.hget("Test", "ID")
print b, type(b)
r.delete("Test")


