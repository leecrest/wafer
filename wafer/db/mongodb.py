# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/25 9:48
@brief  : mongodb封装
"""

from pymongo import Connection


class CDBPool:
	def __init__(self):
		self.m_Database = None
		self.m_Inited = False


	def Init(self, dConfig):
		if self.m_Inited:
			raise Exception("DBPool has inited!")

		oConn = Connection(
			dConfig.get("host", "localhost"),
			dConfig["port"]
		)
		if not oConn:
			return False
		self.m_Database = getattr(oConn, dConfig["db"])
		if not self.m_Database:
			return False
		self.m_Inited = True
		return True




