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
	m_AttrConfig = None

	def __init__(self, iIndex):
		self.m_ID       = iIndex
		self.m_Redis    = wafer.GetModule("redis")
		self.m_Inited   = False
		self.m_Update   = False
		self.m_New      = True
		self.InitAttr()
		self.Load()


	def Load(self):
		data = self.m_Redis.hget(self.m_TableName, self.m_ID)
		if data is None:
			self.m_Inited = False
			self.m_New = True
		else:
			self.m_Data.update(data)
			self.m_Inited = True
			self.m_New = False
		self.m_Update = False


	def InitAttr(self):
		if not self.m_AttrConfig:
			return
		dAttrCfg = self.m_AttrConfig.get("Attr", {})
		for dCfg in dAttrCfg.iteritems():
			self.m_Data[dCfg["Name"]] = dCfg["Default"]


	def New(self):
		if not self.m_New:
			return
		self.m_New = False
		self.m_Inited = True
		self.m_Data = {}
		self.InitAttr()
		self.Update()


	def Delete(self):
		if self.m_New:
			return
		self.m_Redis.hdel(self.m_TableName, self.m_ID)
		self.m_New = True
		self.m_Data = None
		self.m_Inited = False
		self.m_Update = False


	def SetAttr(self, sKey, sValue):
		if not self.m_Inited:
			return
		dAttrCfg = self.m_AttrConfig.get("Attr", {})[sKey]
		if dAttrCfg and not sValue is None:
			iMin = dAttrCfg.get("Min", None)
			if not iMin is None and sValue < iMin:
				sValue = iMin
			iMax = dAttrCfg.get("Max", None)
			if not iMax is None and sValue > iMax:
				sValue = iMax
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


	def GetAttrByName(self, sName):
		if not self.m_Inited:
			return
		return self.m_Data.get(sName, None)


	def GetAttrByID(self, iAttrID):
		if not self.m_Inited:
			return
		sName = self.m_AttrConfig["ID2Name"][str(iAttrID)]
		return self.m_Data.get(sName, None)


	def DelAttr(self, sKey):
		if not self.m_Inited or not sKey in self.m_Data:
			return
		del self.m_Data[sKey]
		self.Update()


	def Clear(self):
		if not self.m_Inited:
			return
		self.m_Data = {}
		self.Update()


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