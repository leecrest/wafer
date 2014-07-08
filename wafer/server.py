#coding=utf-8
"""
@author : leecrest
@time   : 14-1-31 下午12:05
@brief  :
"""

"""
服务器的基础组件有：tcp_server，rpc_server，rpc_client，dbpool
服务器类型划分为2类：
1、FrontEnd，前端服务器
	对外提供链接接口，管理客户端连接、负责客户端和BackEnd的通信等。
	必需组件：tcp_server，rpc_client
	可选组件：dbpool
2、BackEnd，后端服务器
	实现游戏逻辑玩法等。
	必需组件：rpc_client
	可选组件：dbpool

每个服务器的属性有：
frontend：true/false，是否前端服务器
log：日志路径
net：[{"type"：网络协议类型，"host"：主机ip，"port"：网络端口}]
rpc：[{"name"：名称，"host"：主机ip，"port"：端口，"server"：true/false，是否server}]
import：["xxxx","yyyy"]，初始化服务器时加载的文件列表
"""


from twisted.internet import reactor
from wafer.utils import *
import wafer.log as log


#服务器状态
SERVER_STATE_NONE       = 0 #默认状态，未初始化
SERVER_STATE_INIT       = 1 #完成了初始化
SERVER_STATE_START      = 2 #已经启动
SERVER_STATE_STOP       = 3 #已经停止

#网络类型
NET_TYPE_TCP            = "tcp"     #使用tcp协议通信
NET_TYPE_WEBSOCKET      = "web"     #使用websocket协议通信
NET_TYPE_HTTP           = "http"    #使用http协议通信


class CServer(object):
	__metaclass__ = CSingleton


	def __init__(self):
		self.m_Name         = ""
		self.m_bFrontEnd    = False
		self.m_State        = SERVER_STATE_NONE
		self.m_LogPath      = ""
		self.m_RpcDict      = {}
		self.m_NetType      = NET_TYPE_TCP
		self.m_Handler      = {}
		self.m_Modules      = {}


	def GetModule(self, sName):
		return self.m_Modules.get(sName, None)


	def InitConfig(self, sName, dConfig):
		if "name" in dConfig:
			sName = dConfig["name"]
		self.m_Name = sName
		#服务器配置
		self.m_bFrontEnd = dConfig.get("frontend", False)
		#执行根目录
		sPath = dConfig.get("path", None)
		if sPath:
			import os, sys
			os.chdir(sPath)
			sys.path.insert(0, sPath)
			log.Info("server(%s) change root path to (%s)" % (self.m_Name, sPath))

		#日志路径
		self.m_LogPath = dConfig.get("log", "./")
		log.InitLog(self.m_LogPath)

		#初始化net，目前仅有前端服务器支持net参数
		if self.m_bFrontEnd:
			dNetCfg = dConfig.get("net", None)
			if not dNetCfg:
				log.Fatal("server(%s) need config about network" % self.m_Name)
				return
			sNetType = dNetCfg["type"].lower()
			if sNetType == NET_TYPE_TCP:
				import wafer.tcp
				self.m_NetType = NET_TYPE_TCP
				self.m_Modules["net"] = wafer.tcp.CreateServer(self.m_Name, dNetCfg["host"], dNetCfg["port"])
				log.Info("%s(%s) listen at %d" % (self.m_Name, sNetType, dNetCfg["port"]))
			elif sNetType == NET_TYPE_HTTP:
				self.m_NetType = NET_TYPE_HTTP
			elif sNetType == NET_TYPE_WEBSOCKET:
				self.m_NetType = NET_TYPE_WEBSOCKET

		#初始化web
		dWebCfg = dConfig.get("web", None)
		if dWebCfg:
			import wafer.web
			sHost = dWebCfg.get("url", "127.0.0.1")
			self.m_Modules["web"] = wafer.web.CreateWebServer(sHost, dWebCfg["port"])
			log.Info("server(%s) listen web port at %s:%d" % (self.m_Name, sHost, dWebCfg["port"]))


		#RPC初始化
		dRpcList = dConfig.get("rpc", [])
		if dRpcList:
			import wafer.rpc
			for dRpcCfg in dRpcList:
				sRpcName = dRpcCfg["name"]
				if dRpcCfg.get("server", False):
					oRpcNode = wafer.rpc.CreateRpcServer(sRpcName, dRpcCfg["port"])
					log.Info("%s(rpc) listen at %d" % (sRpcName, dRpcCfg["port"]))
				else:
					tAddress = (dRpcCfg["host"], dRpcCfg["port"])
					oRpcNode = wafer.rpc.CreateRpcClient(self.m_Name, sRpcName, tAddress)
					log.Info("%s create rpc_client to %s" % (self.m_Name, sRpcName))
				self.m_RpcDict[sRpcName] = oRpcNode

		#redis
		dCfg = dConfig.get("redis", None)
		if dCfg:
			import redis
			self.m_Modules["redis"] = redis.Redis(
				host=dCfg.get("host", "localhost"),
			    port=dCfg.get("port", 6379),
			    db=dCfg.get("db", 0),
			)
			log.Info("server(%s) start redis" % self.m_Name)


		#每个进程配置init选项，启动时将加载此文件
		sInitFile = dConfig.get("init", None)
		mod = self.Import(sInitFile)
		if hasattr(mod, "ServerStart"):
			self.m_Handler["ServerStart"] = mod.ServerStart
		if hasattr(mod, "ServerStop"):
			self.m_Handler["ServerStop"] = mod.ServerStop
		if self.m_NetType == NET_TYPE_TCP:
			oNetNode = self.m_Modules.get("net", None)
			if oNetNode:
				if hasattr(mod, "ConnectionLost"):
					oNetNode.GetService().SetCallback("__OnConnectionLost", mod.ConnectionLost)
				if hasattr(mod, "ConnectionMade"):
					oNetNode.GetService().SetCallback("__OnConnectionMade", mod.ConnectionMade)
		self.m_State = SERVER_STATE_INIT
		log.Info("server(%s) init success!" % self.m_Name)


	@staticmethod
	def Import(sFile):
		if sFile.endswith(".__init__"):
			sFile = sFile[:-9]
		mod = __import__(sFile)
		sList = sFile.split(".")
		for sItem in sList[1:]:
			mod = getattr(mod, sItem)
		return mod


	def Start(self):
		if self.m_State == SERVER_STATE_NONE:
			log.Fatal("server need init first")
			return
		elif self.m_State == SERVER_STATE_START:
			log.Fatal("server(%s) already started" % self.m_Name)
			return
		log.Info("Server(%s) start now" % self.m_Name)
		reactor.callLater(1, self.ServerStart)
		reactor.run()


	def ServerStart(self):
		cbFunc = self.m_Handler.get("ServerStart", None)
		if cbFunc:
			cbFunc(self)


	def Stop(self):
		if self.m_State != SERVER_STATE_START:
			log.Fatal("server(%s) has not started, cannot stop!" % self.m_Name)
			return
		self.m_State = SERVER_STATE_STOP
		log.Info("server(%s) stopped!" % self.m_Name)
		cbFunc = self.m_Handler.get("ServerStop", None)
		if cbFunc:
			cbFunc(self)
		reactor.stop()




#=======================================================================================================================
#初始化函数
def InitWeb(dConfig):
	svr = CServer().GetModule("web")
	if not svr:
		return
	for sName, oSite in dConfig.iteritems():
		svr.putChild(sName, oSite)


def InitNetService(dConfig, cbDefault):
	obj = CServer().GetModule("net")
	if not obj:
		return
	svr = obj.GetService()
	svr.SetCallbacks(dConfig)
	svr.SetDefaultCallback(cbDefault)


def InitRpcClient(sRpcName, dLocal, dRemote):
	node = CServer().m_RpcDict.get(sRpcName, None)
	if not node or node.m_bServer:
		return
	node.SetLocals(dLocal)
	node.SetRemotes(dRemote)


def InitRpcServer(sRpcName, dLocal, dRemote):
	node = CServer().m_RpcDict.get(sRpcName, None)
	if not node or not node.m_bServer:
		return
	node.SetLocals(dLocal)
	node.SetRemotes(dRemote)


#=======================================================================================================================
def CallRpcServer(sRpcName, key, *args, **kw):
	obj = CServer().m_RpcDict.get(sRpcName, None)
	if not obj or obj.m_bServer:
		return
	obj.CallServer(key, *args, **kw)


def CallRpcClient(sRpcName, sClientName, key, *args, **kwargs):
	obj = CServer().m_RpcDict.get(sRpcName, None)
	if not obj or not obj.m_bServer:
		return
	obj.CallClient(sClientName, key, *args, **kwargs)


#=======================================================================================================================
#发送数据包
def PackSend(iConnID, sProtoName, dProtocol, bCrypt=True):
	"""
	发送网络协议。非前端服务器不允许加密发送
	:param iConnID: 客户端链接编号，可以是int，也可以是list
	:param sProtoName: 协议名称
	:param dProtocol: 协议内容
	:param bCrypt: 是否加密发送
	:return:
	"""
	if not iConnID or not sProtoName or not dProtocol:
		return
	app = CServer()
	if not app.m_bFrontEnd and bCrypt:
		bCrypt = False
	obj = app.GetModule("net")
	if not obj:
		return
	obj.SendData(iConnID, sProtoName, dProtocol, bCrypt)


def PackTrans(iConnID, iProtoID, sData, bCrypt=True):
	"""
	转发网络协议，用于进行服务器之间的协议转发。非前端服务器不允许加密发送
	:param iConnID: 客户端链接编号，可以是int，也可以是list
	:param iProtoID: 协议编号
	:param sData: 协议内容
	:param bCrypt: 是否加密发送
	:return:
	"""
	if not iConnID or not iProtoID or not sData:
		return
	app = CServer()
	if not app.m_bFrontEnd and bCrypt:
		bCrypt = False
	obj = app.GetModule("net")
	if not obj:
		return
	obj.SendTrans(iConnID, iProtoID, sData, bCrypt)


def CreateServer(sName, dConfig):
	app = CServer()
	app.InitConfig(sName, dConfig)
	return app


def GetServer():
	return CServer()


def GetModule(sName):
	app = CServer()
	return app.GetModule(sName)



__all__ = ["PackSend", "PackTrans", "CallRpcClient", "CallRpcServer",
           "InitWeb", "InitNetService", "InitRpcClient", "InitRpcServer",
           "CreateServer", "GetServer", "GetModule"]


