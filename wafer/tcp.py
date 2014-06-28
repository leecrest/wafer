#coding=utf-8
"""
@author : leecrest
@time   : 14-1-14 下午10:14
@brief  : 网络协议处理
"""

from twisted.internet import protocol, reactor
from wafer.service import CService
import wafer.log as log
import wafer.packet as packet

reactor = reactor


def DefferedErrorHandle(e):
	"""延迟对象的错误处理"""
	log.Fatal(str(e))
	return



class CNetConnection(protocol.Protocol):
	"""网络连接"""

	def __init__(self):
		self.m_Buff = ""
		self.m_DataHandler = None


	def GetConnID(self):
		return self.transport.sessionno


	def connectionMade(self):
		"""建立连接后的处理"""
		log.Info("Client %d login at [%s,%d]" % (
			self.transport.sessionno, self.transport.client[0], self.transport.client[1]))
		self.factory.ConnectionMade(self)
		self.m_DataHandler = self.DataHandleCoroutine()
		self.m_DataHandler.next()


	def connectionLost(self, reason=protocol.connectionDone):
		log.Info("Client %d logout" % self.transport.sessionno)
		self.factory.ConnectionLost(self.transport.sessionno)


	def SendData(self, data):
		"""线程安全的向客户端发送数据
		@param data: str 要向客户端写的数据
		"""
		if not self.transport.connected or not data:
			return
		sProto, dProto = data[0], data[1]
		if type(dProto) == str:
			sData = packet.PackData(sProto, dProto)
		elif type(dProto) == dict:
			sData = packet.PackProto(sProto, dProto)
		else:
			return
		reactor.callFromThread(self.transport.write, sData)


	def DataHandleCoroutine(self):
		#获取协议头的长度
		iLength = packet.PACKET_HEAD_LEN
		while True:
			data = yield
			self.m_Buff += data
			while self.m_Buff.__len__() >= iLength:
				unpack = packet.UnpackProto(self.m_Buff)
				if not unpack:
					log.Fatal("illegal data package -- [%s]"%unpack)
					self.transport.loseConnection()
					break
				sProtoName, iPackLen, dPackData = unpack
				log.Info("recv %s/%d from %d" % (sProtoName, iPackLen, self.GetConnID()))
				self.m_Buff = self.m_Buff[iLength + iPackLen:]
				d = self.factory.DataReceived(self.GetConnID(), sProtoName, dPackData)
				if not d:
					continue
				d.addCallback(self.SendData)
				d.addErrback(DefferedErrorHandle)


	def dataReceived(self, data):
		"""数据到达处理
		@param data: str 客户端传送过来的数据
		"""
		self.m_DataHandler.send(data)



class CNetFactory(protocol.ServerFactory):
	"""协议工厂"""

	protocol = CNetConnection


	def __init__(self, sName, sHost, iPort):
		self.m_Name = sName
		self.m_Service = CService(sName)
		self.m_sHost = sHost
		self.m_iPort = iPort
		self.m_ConnDict = {}


	def GetService(self):
		return self.m_Service


	def ConnectionMade(self, conn):
		"""当连接建立时的处理"""
		iConnID = conn.GetConnID()
		if iConnID in self.m_ConnDict:
			return
		self.m_ConnDict[iConnID] = conn
		self.m_Service.Execute("__OnConnectionMade", iConnID)


	def ConnectionLost(self, iConnID):
		"""连接断开时的处理"""
		if iConnID in self.m_ConnDict:
			del self.m_ConnDict[iConnID]
		self.m_Service.Execute("__OnConnectionLost", iConnID)


	def DataReceived(self, iConnID, sProtoName, data):
		"""数据到达时的处理"""
		return self.m_Service.Execute(sProtoName, iConnID, data)


	def LoseConnection(self, iConnID):
		"""主动断开与客户端的连接"""
		conn = self.m_ConnDict.get(iConnID, None)
		if not conn:
			return
		conn.transport.loseConnection()


	def SendData(self, iConnID, sProtoName, dProtocol):
		"""
		向指定链接的客户端，发送指定协议
		:param iConnID: 客户端链接编号
		:param sProtoName: 协议名称
		:param dProtocol: 协议数据源
		:return:
		"""
		if not dProtocol:
			return
		conn = self.m_ConnDict.get(iConnID, None)
		if not conn:
			return
		data = packet.PackProto(sProtoName, dProtocol)
		conn.SendData(data)


	def SendTrans(self, iConnID, iProtoID, sData):
		"""
		发送中转协议包，不需要按照本地协议规则进行打包
		:param iConnID: 客户端ID
		:param iProtoID: 协议编号
		:param sData: 协议数据
		:return:
		"""
		if not sData:
			return
		conn = self.m_ConnDict.get(iConnID, None)
		if not conn:
			return
		#打包数据
		data = packet.PackData(iProtoID, sData)
		#加密
		#发送
		conn.SendData(data)





__all__ = ["CNetConnection", "CNetFactory"]
