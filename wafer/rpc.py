#coding=utf-8
"""
@author : leecrest
@time   : 14-4-16 下午9:50
@brief  : RPC
"""

from twisted.spread import pb
from twisted.internet import reactor

from wafer.service import CService
import wafer.log as log


reactor = reactor


#=======================================================================================================================
if not "g_ClientDict" in globals():
	g_ClientDict = {}


def CreateRpcClient(sClientName, sServerName, tAddress):
	global g_ClientDict
	if sServerName in g_ClientDict:
		raise "CreateRpcClient err, %s is existed in %s!" % (sServerName, g_ClientDict.keys())
	oClient = CRpcClient(sClientName, sServerName, tAddress)
	g_ClientDict[sServerName] = oClient
	oClient.Connect()
	return oClient


#=======================================================================================================================
def CallServerRequest(oRemote, sFuncName, *args, **kw):
	"""全局远程调用函数
	@param sFuncName: str 远程方法
	"""
	return oRemote.callRemote(sFuncName, *args, **kw)


def CallServerResult(result, bSuccess, sName, key, *args, **kw):
	"""服务端反馈，将反馈转发给sName客户端"""
	oClient = g_ClientDict.get(sName, None)
	if not oClient:
		return
	if not bSuccess:
		log.Info("CallFailed(%s, %s):%s" % (sName, key, result))
		return
	oClient.CallResult(key, result, *args, **kw)


#=======================================================================================================================
def ConnectServerSuccess(oRemote, sName):
	"""连接服务器成功"""
	oClient = g_ClientDict.get(sName, None)
	if not oClient:
		return
	log.Info("%s(rpc) connect to RpcServer_%s%s success" % (sName, oClient.m_Server, oClient.m_Address))
	oRemote.callRemote("AddClient", oClient.m_Name, oClient.m_Local)


def ConnectServerFailed(error, sName):
	log.Info("connect failed, %s" % error.getErrorMessage())
	reactor.callLater(1, ReConnectServer, sName)


def ReConnectServer(sName):
	oClient = g_ClientDict.get(sName, None)
	if not oClient:
		return
	oClient.ReConnect()


class CClientFactory(pb.PBClientFactory):
	def __init__(self, sName):
		pb.PBClientFactory.__init__(self)
		self.m_Name = sName

	def clientConnectionLost(self, connector, reason, reconnecting=0):
		pb.PBClientFactory.clientConnectionLost(self, connector, reason, reconnecting)
		log.Info(u"和RPC[%s]的链接断开了，尝试重连...", self.m_Name)
		ReConnectServer(self.m_Name)


#=======================================================================================================================
class CClientService(pb.Referenceable):
	"""客户端的服务函数集合，提供给服务器调用"""

	def __init__(self, sName):
		self.m_Service = CService(sName)


	def remote_CallService(self, key, *args, **kwargs):
		return self.m_Service.Execute(key, *args, **kwargs)



#=======================================================================================================================
class CRpcClient(object):
	"""RPC客户端，可以调用服务器上的函数"""
	m_bServer = False

	def __init__(self, sClientName, sServerName, tAddress):
		self.m_Name     = sClientName
		self.m_Server   = sServerName
		self.m_Factory  = CClientFactory(sServerName)
		self.m_Local    = CClientService("%s.Local" % self.m_Name)   #提供给服务端调用的服务
		self.m_Remote   = CService("%s.Remote" % self.m_Name)        #调用服务端函数的回调
		self.m_Address  = tAddress


	def Name(self):
		return self.m_Name


	def SetLocals(self, dConfig):
		"""设置回调函数集合，提供给服务器调用"""
		self.m_Local.m_Service.SetCallbacks(dConfig)


	def SetRemotes(self, dConfig):
		self.m_Remote.SetCallbacks(dConfig)


	def Connect(self):
		"""
		连接到RPC服务器
		@return:
		"""
		reactor.connectTCP(self.m_Address[0], self.m_Address[1], self.m_Factory)
		log.Info("%s(rpc) try connect to %s%s" % (self.m_Name, self.m_Server, self.m_Address))
		#向RPC服务器注册自己的服务列表，方便服务器调用
		oDefer = self.m_Factory.getRootObject()
		oDefer.addCallback(ConnectServerSuccess, self.m_Server)
		oDefer.addErrback(ConnectServerFailed, self.m_Server)


	def ReConnect(self):
		"""重新连接"""
		self.Connect()


	def CallServer(self, key, *args, **kw):
		"""远程调用服务端上的接口"""
		oDefer = self.m_Factory.getRootObject()
		oDefer.addCallback(CallServerRequest, "CallService", self.m_Name, key, *args, **kw)
		oDefer.addCallback(CallServerResult, True, self.m_Server, key, *args, **kw)
		oDefer.addErrback(CallServerResult, False, self.m_Server, key)


	def CallResult(self, key, result, *args, **kw):
		"""远程调用的结果"""
		self.m_Remote.Execute(key, result, *args, **kw)






#=======================================================================================================================
if not "g_ServerDict" in globals():
	g_ServerDict = {}


def CreateRpcServer(sName, iPort):
	root = CRpcServer(sName)
	g_ServerDict[sName] = root
	reactor.listenTCP(iPort, CRpcFactory(root))
	return root


def CallClientResult(result, bSuccess, sServer, sClient, key, *args, **kw):
	global g_ServerDict
	root = g_ServerDict.get(sServer, None)
	if not root:
		return
	if not bSuccess:
		log.Error("call rpc_client(%s, %s) failed, %s" % (sClient, key, result.getErrorMessage()))
		return
	root.CallResult(sClient, key, result, *args, **kw)



#=======================================================================================================================
class CRpcConnection(pb.Broker):

	def connectionLost(self, reason):
		iClientID = self.transport.sessionno
		self.factory.root.RemoveClientByID(iClientID)
		pb.Broker.connectionLost(self, reason)



#=======================================================================================================================
class CRpcFactory(pb.PBServerFactory):
	"""
	Rpc工厂，初始化时，需要传入CRpcServer实例
	"""
	protocol = CRpcConnection



#=======================================================================================================================
class CRpcServer(pb.Root):
	"""
	Rpc服务端，管理Rpc客户端，并且在服务端和客户端之间相互调用
	"""
	m_bServer = True

	def __init__(self, sName):
		self.m_Name = sName
		self.m_ClientDict = {}
		self.m_Local = CService("%s.Local"%sName)
		self.m_Remote = CService("%s.Remote"%sName)


	def Name(self):
		return self.m_Name


	def SetLocals(self, dConfig):
		"""设置向客户端提供的服务"""
		self.m_Local.SetCallbacks(dConfig)


	def SetRemotes(self, dConfig):
		self.m_Remote.SetCallbacks(dConfig)


	def remote_AddClient(self, sName, oClient):
		log.Info("add rpc_client(%s)" % sName)
		oOld = self.m_ClientDict.get(sName, None)
		if oOld:
			self.RemoveClient(sName)
		self.m_ClientDict[sName] = oClient
		self.OnClientConnect(sName, oClient)


	def OnClientConnect(self, sName, oClient):
		pass


	def remote_CallService(self, sName, key, *args, **kwargs):
		"""
		处理来自客户端的调用请求
		@param sName:客户端名称
		@param key:服务编号
		@param args:调用参数
		@param kwargs:调用参数字典
		@return:
		"""
		return self.m_Local.Execute(key, sName, *args, **kwargs)


	def RemoveClient(self, sName):
		if not sName in self.m_ClientDict:
			return
		log.Info("remove rpc_client %s" % sName)
		oClient = self.m_ClientDict[sName]
		del self.m_ClientDict[sName]
		self.OnClientLostConnect(sName, oClient)


	def OnClientLostConnect(self, sName, oClient):
		pass


	def RemoveClientByID(self, iClientID):
		sName = ""
		for k, v in self.m_ClientDict.items():
			if v.broker.transport.sessionno == iClientID:
				sName = k
				break
		self.RemoveClient(sName)


	def CallClient(self, sName, key, *args, **kwargs):
		"""请求调用客户端的服务"""
		if not sName in self.m_ClientDict:
			return
		oClient = self.m_ClientDict[sName]
		oDefer = oClient.callRemote("CallService", key, *args, **kwargs)
		oDefer.addCallback(CallClientResult, True, self.m_Name, sName, key, *args, **kwargs)
		oDefer.addErrback(CallClientResult, False, self.m_Name, sName, key)
		return oDefer


	def CallResult(self, sClient, key, result, *args, **kw):
		self.m_Remote.Execute(key, sClient, result, *args, **kw)


	def GetClientList(self):
		return self.m_ClientDict.keys()


__all__ = ["CreateRpcClient", "CreateRpcServer",]
