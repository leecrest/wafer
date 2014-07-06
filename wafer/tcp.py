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
		reactor.callFromThread(self.transport.write, data)


	def DataHandleCoroutine(self):
		iConnID = self.GetConnID()
		#获取协议头的长度
		while True:
			data = yield
			self.m_Buff += data
			while self.m_Buff.__len__() >= packet.PACKET_HEAD_LEN:
				PackInfo = packet.UnpackNet(iConnID, self.m_Buff)
				if not PackInfo:
					log.Fatal("illegal data package -- [%s]" % PackInfo)
					self.transport.loseConnection()
					break
				sProtoName, iPackLen, dProtoData = PackInfo
				self.m_Buff = self.m_Buff[packet.PACKET_HEAD_LEN + iPackLen:]
				log.Info("recv %s/%d from %d" % (sProtoName, iPackLen, iConnID))
				self.factory.DataReceived(self.GetConnID(), sProtoName, dProtoData)


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
		ret = self.m_Service.Execute(sProtoName, iConnID, data)
		if not ret or len(ret) < 2:
			return
		self.SendData(iConnID, ret[0], ret[1])


	def LoseConnection(self, iConnID):
		"""主动断开与客户端的连接"""
		conn = self.m_ConnDict.get(iConnID, None)
		if not conn:
			return
		conn.transport.loseConnection()


	def SendData(self, iConnID, sProtoName, dProtocol, bCrypt=True):
		"""
		向指定链接的客户端，发送指定协议
		:param iConnID: 客户端链接编号
		:param sProtoName: 协议名称
		:param dProtocol: 协议数据源
		:param bCrypt: 是否加密
		:return:
		"""
		if not iConnID or not sProtoName or not dProtocol:
			return
		#打包协议
		sBuff = packet.PackProto(sProtoName, dProtocol)
		if not sBuff:
			return
		#打包成网络包并发送
		if type(iConnID) == int:
			oConn = self.m_ConnDict.get(iConnID, None)
			if not oConn:
				return
			oConn.SendData(packet.PackNet(sBuff, bCrypt, iConnID))
		elif type(iConnID) in (tuple, list):
			if bCrypt:
				for iConn in iConnID:
					oConn = self.m_ConnDict.get(iConn, None)
					if not oConn:
						continue
					oConn.SendData(packet.PackNet(iConnID, sBuff, bCrypt))
			else:
				sBuff = packet.PackNet(sBuff, bCrypt)
				if not sBuff:
					return
				for iConn in iConnID:
					oConn = self.m_ConnDict.get(iConn, None)
					if not oConn:
						continue
					oConn.SendData(sBuff)


	def SendTrans(self, iConnID, iProtoID, sData, bCrypt=True):
		"""
		发送中转协议包，不需要按照本地协议规则进行打包
		:param iConnID: 客户端ID
		:param iProtoID: 协议编号
		:param sData: 协议数据
		:param bCrypt: 是否加密
		:return:
		"""
		if not iConnID or not iProtoID or not sData:
			return
		#打包协议
		sBuff = packet.PackData(iProtoID, sData)
		if not sBuff:
			return
		#打包成网络包并发送
		if type(iConnID) == int:
			oConn = self.m_ConnDict.get(iConnID, None)
			if not oConn:
				return
			oConn.SendData(packet.PackNet(sBuff, bCrypt, iConnID))
		elif type(iConnID) in (tuple, list):
			if bCrypt:
				for iConn in iConnID:
					oConn = self.m_ConnDict.get(iConn, None)
					if not oConn:
						continue
					oConn.SendData(packet.PackNet(iConnID, sBuff, bCrypt))
			else:
				sBuff = packet.PackNet(sBuff, bCrypt)
				if not sBuff:
					return
				for iConn in iConnID:
					oConn = self.m_ConnDict.get(iConn, None)
					if not oConn:
						continue
					oConn.SendData(sBuff)



def CreateServer(sName, sHost, iPort):
	obj = CNetFactory(sName, sHost, iPort)
	reactor.listenTCP(iPort, obj)
	return obj



__all__ = ["CreateServer",]
