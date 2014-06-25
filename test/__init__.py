#coding=utf-8
"""
@author : leecrest
@time   : 14-6-16 下午11:22
@brief  : 
"""

from wafer.db.mongodb import *


obj = CDBPool()
print obj.Init({
	"port" : 1234,
    "db" : "test",
})

print obj.m_Database
