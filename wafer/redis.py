# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/25 23:22
@brief  : 
"""


import redis


class CRedisWrapper:
	"""
	redis.Redis的包装器，调用更简易
	"""
	def __init__(self, dConfig):
		self.m_Redis = redis.Redis(
			host = dConfig.get("host", "localhost"),
		    port = dConfig.get("port", 6379),
		    db = dConfig.get("db", 0),
		)


	def Get(self, sKey, default=None):
		value = self.m_Redis.get(sKey)
		if value:
			return value
		return default


	def Set(self, sKey, Value):
		self.m_Redis.set(sKey, Value)



def CreateRedis(dConfig):
	r = redis.Redis(
		host = dConfig.get("host", "localhost"),
	    port = dConfig.get("port", 6379),
	    db = dConfig.get("db", 0),
	)
	return r


