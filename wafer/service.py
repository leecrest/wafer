#coding=utf-8
"""
@author : leecrest
@time   : 14-1-15 上午12:03
@brief  : 
"""

from twisted.internet import defer, threads
import threading


class CService():
	"""
	服务组件
	每个服务器进程都将拥有一个服务，每个服务中可以注册多个回调函数，按照协议编号进行协议的回调处理
	"""

	RUN_STYLE_SINGLE = 1        #单独运行
	RUN_STYLE_PARALLEL = 2      #平行运行


	def __init__(self, sName, iRunStyle=RUN_STYLE_SINGLE):
		self.m_sName = sName
		self.m_iRunStyle = iRunStyle
		self.m_Lock = threading.RLock()
		self.m_FuncDict = {}
		self.m_Default = None


	def Name(self):
		return self.m_sName


	def SetCallback(self, key, cbFunc):
		if not key:
			key = cbFunc.__name__
		self.m_Lock.acquire()
		if cbFunc:
			self.m_FuncDict[key] = cbFunc
		elif key in self.m_FuncDict:
			del self.m_FuncDict[key]
		self.m_Lock.release()


	def SetCallbacks(self, dConfig):
		for key, cbFunc in dConfig.iteritems():
			self.SetCallback(key, cbFunc)


	def SetDefaultCallback(self, cbFunc):
		self.m_Default = cbFunc


	def GetCallback(self, key):
		self.m_Lock.acquire()
		cbFunc = self.m_FuncDict.get(key, self.m_Default)
		self.m_Lock.release()
		return cbFunc


	def Execute(self, key, *args, **kwargs):
		cbFunc = self.GetCallback(key)
		if not cbFunc:
			return
		ret = None
		self.m_Lock.acquire()
		try:
			if self.m_iRunStyle == self.RUN_STYLE_SINGLE:
				ret = cbFunc(*args, **kwargs)
			else:
				ret = threads.deferToThread(cbFunc, *args, **kwargs)
		finally:
			self.m_Lock.release()
		return ret



class CSimpleService():
	"""
	服务组件
	每个服务器进程都将拥有一个服务，每个服务中可以注册多个回调函数，按照协议编号进行协议的回调处理
	"""

	def __init__(self, sName):
		self.m_sName = sName
		self.m_FuncDict = {}
		self.m_Default = None


	def Name(self):
		return self.m_sName


	def SetCallback(self, key, cbFunc):
		if not key:
			key = cbFunc.__name__
		if cbFunc:
			self.m_FuncDict[key] = cbFunc
		elif key in self.m_FuncDict:
			del self.m_FuncDict[key]


	def SetCallbacks(self, dConfig):
		for key, cbFunc in dConfig.iteritems():
			self.SetCallback(key, cbFunc)


	def SetDefaultCallback(self, cbFunc):
		self.m_Default = cbFunc


	def Execute(self, key, *args, **kwargs):
		if key in self.m_FuncDict:
			cbFunc = self.m_FuncDict[key]
			ret = cbFunc(*args, **kwargs)
		elif self.m_Default:
			ret = self.m_Default(key, *args, **kwargs)
		else:
			return
		if not ret:
			return
		oDefer = defer.Deferred()
		oDefer.callback(ret)
