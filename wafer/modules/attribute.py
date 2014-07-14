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
		self.m_Data     = self.m_Redis.hget(self.m_TableName, self.m_ID)
		if self.m_Data is None:
			self.m_Inited = False
			self.m_New = True
		else:
			self.m_Inited = True
			self.m_New = False
		self.m_Update = False


	def InitAttr(self):
		tBaseCfg = self.m_AttrConfig.get("BaseAttr", [])
		for dAttrCfg in tBaseCfg:
			self.DictSet(dAttrCfg["Name"], dAttrCfg["Default"])
		tExtendCfg = self.m_AttrConfig.get("ExtendAttr", [])
		for dAttrCfg in tExtendCfg:
			self.DictSet(dAttrCfg["Name"], dAttrCfg["Default"])


	def GetAttr(self, sName):
		dName2ID = self.m_AttrConfig["Name2ID"]




	def New(self):
		if not self.m_New:
			return
		self.m_New = False
		self.m_Inited = True
		self.m_Data = None
		self.OnClear()
		self.Update()


	def OnClear(self):
		self.m_Data = {}


	def Delete(self):
		if self.m_New:
			return
		self.m_Redis.hdel(self.m_TableName, self.m_ID)
		self.m_New = True
		self.m_Data = None
		self.m_Inited = False
		self.m_Update = False


	def DictSet(self, sKey, sValue):
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



	def DictGet(self, sKey, default=None):
		if not self.m_Inited:
			return
		return self.m_Data.get(sKey, default)


	def DictDel(self, sKey):
		if not self.m_Inited or not sKey in self.m_Data:
			return
		del self.m_Data[sKey]
		self.Update()


	def Clear(self):
		if not self.m_Inited:
			return
		self.m_Data = None
		self.OnClear()
		self.Update()


	def DictKeys(self):
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