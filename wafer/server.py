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
from twisted.web import vhost
from wafer.utils import *
import wafer.log as log
import wafer.tcp as tcp
import wafer.rpc as rpc
import wafer.web as web


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
		self.m_RedisNode    = None
		self.m_RpcDict      = {}
		self.m_NetType      = NET_TYPE_TCP
		self.m_NetNode      = None
		self.m_WebNode      = None
		self.m_Handler      = {}


	def GetRedis(self):
		return self.m_RedisNode


	def InitConfig(self, sName, dConfig):
		if "name" in dConfig:
			sName = dConfig["name"]
		self.m_Name = sName
		#服务器配置
		self.m_bFrontEnd = dConfig.get("frontend", False)

		#日志路径
		self.m_LogPath = dConfig.get("log", "./")
		log.InitLog(self.m_LogPath)

		#初始化net，目前仅有前端服务器支持net参数
		if self.m_bFrontEnd:
			dNetCfg = dConfig.get("net", None)
			if not dNetCfg:
				log.Fatal("Server(%s) need config about network" % self.m_Name)
				return
			sNetType = dNetCfg["type"].lower()
			if sNetType == NET_TYPE_TCP:
				self.m_NetType = NET_TYPE_TCP
				self.m_NetNode = tcp.CNetFactory(self.m_Name, dNetCfg["host"], dNetCfg["port"])
				reactor.listenTCP(dNetCfg["port"], self.m_NetNode)
				log.Info("%s(%s) listen at %d" % (self.m_Name, sNetType, dNetCfg["port"]))
			elif sNetType == NET_TYPE_HTTP:
				self.m_NetType = NET_TYPE_HTTP
			elif sNetType == NET_TYPE_WEBSOCKET:
				self.m_NetType = NET_TYPE_WEBSOCKET

		#初始化web
		dWebCfg = dConfig.get("web", None)
		if dWebCfg:
			self.m_WebNode = vhost.NameVirtualHost()
			sHost = dWebCfg.get("url", "127.0.0.1")
			self.m_WebNode.addHost(sHost, "./")
			reactor.listenTCP(dWebCfg["port"], web.CDelaySite(self.m_WebNode))
			log.Info("Server(%s) listen web port at %s:%d" % (self.m_Name, sHost, dWebCfg["port"]))


		#RPC初始化
		dRpcList = dConfig.get("rpc", [])
		for dRpcCfg in dRpcList:
			sRpcName = dRpcCfg["name"]
			if dRpcCfg.get("server", False):
				oRpcNode = rpc.CreateRpcServer(sRpcName)
				reactor.listenTCP(dRpcCfg["port"], rpc.CRpcFactory(oRpcNode))
				log.Info("%s(rpc) listen at %d" % (sRpcName, dRpcCfg["port"]))
			else:
				oRpcNode = rpc.CreateRpcClient(self.m_Name, sRpcName)
				log.Info("%s create rpc_client to %s" % (self.m_Name, sRpcName))
				tAddress = (dRpcCfg["host"], dRpcCfg["port"])
				oRpcNode.Connect(tAddress)
			self.m_RpcDict[sRpcName] = oRpcNode

		#redis
		dCfg = dConfig.get("redis", None)
		if dCfg:
			import redis
			self.m_RedisNode = redis.Redis(
				host=dCfg.get("host", "localhost"),
			    port=dCfg.get("port", 6379),
			    db=dCfg.get("db", 0),
			)
			log.Info("Server(%s) start redis" % self.m_Name)


		#每个进程配置init选项，启动时将加载此文件
		sInitFile = dConfig.get("init", None)
		mod = self.Import(sInitFile)
		if hasattr(mod, "ServerStart"):
			self.m_Handler["ServerStart"] = mod.ServerStart
		if hasattr(mod, "ServerStop"):
			self.m_Handler["ServerStop"] = mod.ServerStop
		if self.m_NetType == NET_TYPE_TCP and self.m_NetNode:
			if hasattr(mod, "ConnectionLost"):
				self.m_NetNode.GetService().SetCallback("__OnConnectionLost", mod.ConnectionLost)
			if hasattr(mod, "ConnectionMade"):
				self.m_NetNode.GetService().SetCallback("__OnConnectionMade", mod.ConnectionMade)
		self.m_State = SERVER_STATE_INIT
		log.Info("Server(%s) init success!" % self.m_Name)


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
			log.Fatal("Server need init first")
			return
		elif self.m_State == SERVER_STATE_START:
			log.Fatal("Server(%s) already started" % self.m_Name)
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
			log.Fatal("Server(%s) has not started, cannot stop!" % self.m_Name)
			return
		self.m_State = SERVER_STATE_STOP
		log.Info("Server(%s) stopped!" % self.m_Name)
		cbFunc = self.m_Handler.get("ServerStop", None)
		if cbFunc:
			cbFunc(self)
		reactor.stop()




#=======================================================================================================================
#初始化函数
def InitWeb(dConfig):
	svr = CServer().m_WebNode
	if not svr:
		return
	for sName, oSite in dConfig.iteritems():
		svr.putChild(sName, oSite)


def InitNetService(dConfig, cbDefault):
	svr = CServer().m_NetNode.GetService()
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
def PackSend(iConnID, sProtoName, dProtocol):
	if type(iConnID) == int:
		CServer().m_NetNode.SendData(iConnID, sProtoName, dProtocol)
	elif type(iConnID) in (tuple, list):
		for iConn in iConnID:
			CServer().m_NetNode.SendData(iConn, sProtoName, dProtocol)


def PackTrans(iConnID, iProtoID, sData):
	if type(iConnID) == int:
		CServer().m_NetNode.SendTrans(iConnID, iProtoID, sData)
	elif type(iConnID) in (tuple, list):
		for iConn in iConnID:
			CServer().m_NetNode.SendTrans(iConn, iProtoID, sData)


def CreateServer(sName, dConfig):
	app = CServer()
	app.InitConfig(sName, dConfig)
	return app


def GetServer():
	return CServer()


__all__ = ["PackSend", "PackTrans", "CallRpcClient", "CallRpcServer",
           "InitWeb", "InitNetService", "InitRpcClient", "InitRpcServer",
           "CreateServer", "GetServer"]


