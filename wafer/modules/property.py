# coding=utf-8
"""
@author : leecrest
@time   : 2014/7/4 9:55
@brief  : 属性
"""
import wafer


class CPropertyRow:
	"""
	属性行，对应每个数据表中的一行
	比如每个角色的基础数据，就是一行，每个角色对象将持有此类的一个实例
	"""
	def __init__(self, oTable, iIndex):
		self.m_Index    = iIndex    #索引
		self.m_Data     = None        #本地缓存数据，最新数据
		self.m_Inited   = False     #是否初始化
		self.m_FuncList = []        #回调函数列表
		self.m_Table    = oTable
		self.m_Update   = False     #脏标记，为True表示需要更新


	def GetData(self):
		return self.m_Data


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


	def Update(self):
		self.m_Update = True
		self.m_Table.SaveRow(self)


	def Updated(self):
		self.m_Update = False


	def CheckUpdate(self):
		return self.m_Update



class CPropertyTable:
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
		oRow = CPropertyRow(self, iIndex)
		oRow.Load(data)
		self.m_RowDict[iIndex] = oRow
		return oRow


	def UnLoadRow(self, oRow):
		if not oRow:
			return
		if not oRow.m_Index in self.m_RowDict:
			return
		del self.m_RowDict[oRow.m_Index]
		if oRow.CheckUpdate():
			self.m_Redis.hset(self.m_Name, oRow.m_Index, oRow.m_Data)
			oRow.Updated()


	def SaveRow(self, oRow):
		if not oRow.m_Index in self.m_RowDict:
			return
		self.m_Redis.hset(self.m_Name, oRow.m_Index, oRow.m_Data)
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


if not "g_PropertyTables" in globals():
	g_PropertyTables = {}



def GetPropertyRow(sTable, iIndex, bCreate=True):
	global g_PropertyTables
	oTable = g_PropertyTables.get(sTable, None)
	if not oTable:
		oTable = CPropertyTable(sTable)
		g_PropertyTables[sTable] = oTable
	return oTable.GetRow(iIndex, bCreate)


def DeletePropertyRow(sTable, iIndex):
	global g_PropertyTables
	oTable = g_PropertyTables.get(sTable, None)
	if not oTable:
		oTable = CPropertyTable(sTable)
		g_PropertyTables[sTable] = oTable
	return oTable.DeleteRow(iIndex)


__all__ = ["GetPropertyRow", "DeletePropertyRow"]