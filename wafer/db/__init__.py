#coding=utf-8
"""
@author : leecrest
@time   : 14-1-14 下午11:35
@brief  : 
"""

from wafer.utils import log

"""
数据库封装接口：
class IDBPool:
	def Init(dConfig)
	def UnInit()


"""


def CreateDB(dConfig):
	sType = dConfig.get("type", "mysql")
	sType = sType.lower()
	if sType == "mysql":
		import mysql
		cls = mysql.CDBPool
	elif sType == "mongodb":
		import mongodb
		cls = mongodb
	else:
		log.Fatal("CreateDB failed! db type(%s) unsupported, dConfig=%s" % (sType, dConfig))
		raise "check db config!"
	obj = cls()
	if not obj.Init(dConfig):
		log.Fatal("InitDB failed!")
		raise "check db config!"
	return obj


__all__ = ["CreateDB"]