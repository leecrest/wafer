#coding=utf-8
"""
@author : leecrest
@time   : 14-3-29 下午10:03
@brief  : 事件系统
"""

#目前支持的事件列表
g_EventList = ("获得物品",)


class CEventMgr:

	def __init__(self, iID):
		self.m_ID = iID
		self.m_EventDict = {}    #事件监听器管理

	def AddEvent(self, sEventName, bSync, cbFunc):
		"""
		添加事件监听器
		@param sEventName：string，事件名称
		@param bSync：bool，是否同步处理
		@param cbFunc：function，回调函数
		"""
		global g_EventList
		if not sEventName in g_EventList:
			raise "事件%s不支持，请检查" % sEventName
		tInfo = (bSync, cbFunc)
		tEventList = self.m_EventDict.get(sEventName, [])
		if tInfo in tEventList:
			raise "事件%s %s 重复注册，请检查" % (sEventName, tInfo)
		tEventList.append(tInfo)
		self.m_EventDict[sEventName] = tEventList

	def RemoveEvent(self, sEventName, bSync, cbFunc):
		"""
		删除事件监听器
		@param sEventName：string，事件名称
		@param bSync：bool，是否同步处理
		@param cbFunc：function，回调函数
		"""
		tInfo = (bSync, cbFunc)
		if not sEventName in self.m_EventDict:
			return
		tEventList = self.m_EventDict[sEventName]
		if not tInfo in tEventList:
			return
		tEventList.remove(tInfo)
		self.m_EventDict[sEventName] = tEventList

	def FireEvent(self, sEventName, *args):
		"""
		触发事件
		@param sEventName：string，事件名称
		@param args：tuple，事件参数
		"""
		tEventList = self.m_EventDict.get(sEventName, [])
		if not tEventList:
			return
		for tEvent in tEventList:
			bSync, cbFunc = tEvent
			#过滤掉异步监听
			if not bSync:
				continue
			cbFunc(*args)
		#在下一个周期中执行异步监听的触发
		#self.FireEventAsync(sEventName, *args)

	def FireEventAsync(self, sEventName, *args):
		tEventList = self.m_EventDict.get(sEventName, [])
		if not tEventList:
			return
		for tEvent in tEventList:
			bSync, cbFunc = tEvent
			if bSync:
				continue
			cbFunc(*args)
