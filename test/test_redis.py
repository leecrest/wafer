# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/25 23:27
@brief  : 
"""

import redis

r = redis.Redis(host="localhost", port=6379, db=0)
print r
v = r.get("hello")
if not v:
	print "get hello -> None"
	r["hello"] = "world"
	print "set hello -> world"
print "dbsize = ", r.dbsize()
print "get hello ->", r.get("hello")

r.save()


pool = redis.ConnectionPool(host="localhost", port=6379, db=1)
r = redis.Redis(connection_pool=pool)
print r
print r.get("hello")
print r.dbsize()