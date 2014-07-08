# coding=utf-8
"""
@author : leecrest
@time   : 2014/7/4 9:55
@brief  : 属性
"""
import wafer


class CAttrBase:
	"""
	属性基类，连接数据表中的一行数据
	"""
	m_TableName = ""

	def __init__(self, iIndex):
		self.m_ID       = iIndex
		self.m_Redis    = wafer.GetModule("redis")
		self.m_Data     = self.m_Redis.hget(self.m_TableName, self.m_ID)
		if self.m_Data is None:
			self.m_Inited = False
			self.m_New = True
		else:
			self.m_Inited = True
			self.m_New = False
		self.m_Update = False


	def New(self):
		if not self.m_New:
			return
		self.m_New = False
		self.m_Inited = True
		self.m_Data = {}
		self.Update()


	def Delete(self):
		if self.m_New:
			return
		self.m_Redis.hdel(self.m_TableName, self.m_ID)
		self.m_New = True
		self.m_Data = None
		self.m_Inited = False
		self.m_Update = False


	def Set(self, sKey, sValue):
		if not self.m_Inited:
			return
		if sKey in self.m_Data:
			if self.m_Data[sKey] == sValue:
				return
			if sValue is None:
				del self.m_Data[sKey]
			else:
				self.m_Data[sKey] = sValue
		else:
			if sValue is None:
				return
			self.m_Data[sKey] = sValue
		self.Update()



	def Get(self, sKey, default=None):
		if not self.m_Inited:
			return
		return self.m_Data.get(sKey, default)


	def Del(self, sKey):
		if not self.m_Inited or not sKey in self.m_Data:
			return
		del self.m_Data[sKey]
		self.Update()


	def Clear(self):
		if not self.m_Inited:
			return
		self.m_Data = {}
		self.Update()


	def Keys(self):
		if not self.m_Inited:
			return
		return self.m_Data.keys()


	def Update(self):
		if not self.m_Inited:
			return
		self.m_Update = True


	def Save(self):
		if not self.m_Inited or not self.m_Update:
			return
		self.m_Redis.hset(self.m_TableName, self.m_ID, self.m_Data)
		self.m_Update = False




__all__ = ["CAttrBase"]