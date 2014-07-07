# coding=utf-8
"""
@author : leecrest
@time   : 2014/7/4 9:55
@brief  : 属性
"""
import wafer


class CAttributeRow:
	"""
	属性行，对应每个数据表中的一行
	比如每个角色的基础数据，就是一行，每个角色对象将持有此类的一个实例
	"""
	def __init__(self, oTable, iIndex):
		self.m_ID       = iIndex    #索引
		self.m_Data     = None      #本地缓存数据，最新数据
		self.m_Inited   = False     #是否初始化
		self.m_FuncList = []        #回调函数列表
		self.m_Table    = oTable
		self.m_Update   = False     #脏标记，为True表示需要更新


	def Load(self, data):
		self.m_Data = data
		self.m_Inited = True
		self.m_Update = False
		sFuncList = self.m_FuncList
		self.m_FuncList = []
		for func in sFuncList:
			func(self)


	def UnLoad(self):
		self.m_Table = None
		self.m_Inited = False
		self.m_Data = None


	def ListIterator(self, cbFunc, *args):
		if type(self.m_Data) != list:
			return
		for Value in self.m_Data:
			cbFunc(Value, *args)


	def ListValues(self):
		if type(self.m_Data) != list:
			return
		return self.m_Data


	def ListAppend(self, data):
		if type(self.m_Data) != list:
			return
		self.m_Data.append(data)
		self.Update()


	def ListRemove(self, data):
		if type(self.m_Data) != list:
			return
		self.m_Data.remove(data)
		self.Update()


	def DictSet(self, sKey, sValue):
		if type(self.m_Data) != dict:
			return
		if sKey in self.m_Data and self.m_Data[sKey] == sValue:
			return
		self.m_Data[sKey] = sValue
		self.Update()


	def DictGet(self, sKey, default=None):
		if type(self.m_Data) != dict:
			return
		return self.m_Data.get(sKey, default)


	def DictKeys(self):
		if type(self.m_Data) != dict:
			return
		return self.m_Data.keys()


	def DictIterator(self, cbFunc, *args):
		if type(self.m_Data) != dict:
			return
		for k,v in self.m_Data.iteritems():
			cbFunc(k, v, *args)


	def Update(self):
		self.m_Update = True
		self.m_Table.SaveRow(self)


	def Updated(self):
		self.m_Update = False


	def CheckUpdate(self):
		return self.m_Update



class CAttributeTable:
	"""
	属性表，对应数据库中的每一张表，比如role表
	"""
	def __init__(self, sTableName):
		self.m_Name     = sTableName        #数据表名称
		self.m_Redis    = wafer.GetModule("redis")
		self.m_RowDict  = {}


	def __del__(self):
		self.SaveAll()
		for oRow in self.m_RowDict.itervalues():
			oRow.UnLoad()
		self.m_RowDict = {}


	def GetRow(self, iIndex, bCreate):
		if iIndex in self.m_RowDict:
			return self.m_RowDict[iIndex]
		return self.LoadRow(iIndex, bCreate)


	def LoadRow(self, iIndex, bCreate):
		data = self.m_Redis.hget(self.m_Name, iIndex)
		if data is None and not bCreate:
			return
		oRow = CAttributeRow(self, iIndex)
		oRow.Load(data)
		self.m_RowDict[iIndex] = oRow
		return oRow


	def UnLoadRow(self, iIndex):
		oRow = self.m_RowDict.get(iIndex, None)
		if not oRow:
			return
		del self.m_RowDict[iIndex]
		if oRow.CheckUpdate():
			self.m_Redis.hset(self.m_Name, oRow.m_ID, oRow.m_Data)
			oRow.Updated()
		oRow.UnLoad()


	def SaveRow(self, oRow):
		if not oRow.m_ID in self.m_RowDict:
			return
		self.m_Redis.hset(self.m_Name, oRow.m_ID, oRow.m_Data)
		oRow.Updated()


	def SaveAll(self):
		for iIndex, oRow in self.m_RowDict.iteritems():
			if not oRow.CheckUpdate():
				continue
			self.m_Redis.hset(self.m_Name, iIndex, oRow.m_Data)
			oRow.Updated()


	def DeleteRow(self, iIndex):
		if iIndex in self.m_RowDict:
			del self.m_RowDict[iIndex]
		self.m_Redis.hdel(self.m_Name, iIndex)


if not "g_AttributeTables" in globals():
	g_AttributeTables = {}



def LoadAttributeRow(sTable, iIndex, bCreate=False):
	"""
	加载属性行，如果已经加载了，直接引用
	:param sTable: 数据表的名称
	:param iIndex: 在表中的索引
	:param bCreate: 当行不存在时，是否创建行
	:return:
	"""
	global g_AttributeTables
	oTable = g_AttributeTables.get(sTable, None)
	if not oTable:
		oTable = CAttributeTable(sTable)
		g_AttributeTables[sTable] = oTable
	return oTable.GetRow(iIndex, bCreate)


def UnLoadAttributeRow(sTable, iIndex):
	"""
	卸载属性行
	:param sTable: 数据表的名称
	:param iIndex: 在表中的索引
	:return:
	"""
	global g_AttributeTables
	oTable = g_AttributeTables.get(sTable, None)
	if not oTable:
		return
	oTable.UnLoadRow(iIndex)


def DeleteAttributeRow(sTable, iIndex):
	"""
	删除属性行
	:param sTable: 数据表的名称
	:param iIndex: 在表中的索引
	:return:
	"""
	global g_AttributeTables
	oTable = g_AttributeTables.get(sTable, None)
	if not oTable:
		oTable = CAttributeTable(sTable)
		g_AttributeTables[sTable] = oTable
	return oTable.DeleteRow(iIndex)


__all__ = ["LoadAttributeRow", "UnLoadAttributeRow", "DeleteAttributeRow"]