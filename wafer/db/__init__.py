#coding=utf-8
"""
@author : leecrest
@time   : 14-1-14 下午11:35
@brief  : 
"""

from wafer.utils import log
#import mysql

DBModule = {
	#"mysql" : mysql.CDBPool,
}


def CreateDB(dConfig):
	sType = dConfig.get("type", "mysql")
	sType = sType.lower()
	if not sType in DBModule:
		log.Fatal("CreateDB failed! db type(%s) unsupported, dConfig=%s" % (sType, dConfig))
		raise "check db config!"
	obj = DBModule[sType]()
	obj.Init(dConfig)
	return obj


__all__ = ["CreateDB"]