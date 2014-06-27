#coding=utf-8
"""
@author : leecrest
@time   : 14-1-29 下午2:52
@brief  : 网络定义
"""

import wafer.log as log
import struct
import json


"""
协议格式：
+--------+-------+--------+
|   id   |  len  |  body  |
+--------+-------+--------+

1.id：2byte，协议编号，唯一标示
2.len：2byte，body的长度
3.body：协议的二进制内容
"""
PACKET_HEAD_LEN		= 4
PACKET_MAX_SIZE		= 2 ** 16


#数据类型，格式：{"类型名称":(解析格式,长度),}
DATA_TYPE = {
	"bool": ("?", 1),
    "int8": ("b", 1), "int16": ("h", 2), "int32": ("i", 4), "long": ("l", 8),
	"uint8": ("B", 1), "uint16": ("H", 2), "uint32": ("I", 4), "ulong": ("L", 8),
}



class CWritePacket:
	def __init__(self, iIndex=0):
		self.m_Index = iIndex
		self.m_Len = 0
		self.m_Data = ""


	def Write(self, sType, value):
		if not self.m_Index:
			return
		if sType != "string":
			sFormat, iLen = DATA_TYPE[sType]
			if self.m_Len + iLen > PACKET_MAX_SIZE:
				return
			self.m_Data += struct.pack(sFormat, value)
			self.m_Len += iLen
		else:
			iLen = len(value)
			if self.m_Len + iLen + 1 > PACKET_MAX_SIZE:
				return
			self.m_Data += struct.pack("B%ds" % iLen, iLen, value)
			self.m_Len += iLen + 1
		return True


	def Pack(self):
		if not self.m_Index:
			return
		data = struct.pack("!HH", self.m_Index, self.m_Len) + self.m_Data
		self.m_Index = 0
		self.m_Len = 0
		self.m_Data = ""
		return data



class CReadPacket:
	def __init__(self, data):
		self.m_Offset = 0
		self.m_Data = data
		self.m_Len = len(data)


	def Read(self, sType):
		if sType != "string":
			sFormat, iLen = DATA_TYPE[sType]
		else:
			iLen = self.Read("uint8")
			sFormat = "%ds" % iLen
		if self.m_Offset + iLen > self.m_Len:
			return
		value = struct.unpack_from(sFormat, self.m_Data, self.m_Offset)
		self.m_Offset += iLen
		return value[0]


if not "g_ReadPacket" in globals():
	g_ReadPacket = CReadPacket("")
	g_WritePacket = CWritePacket()
	g_Name2ID = None
	g_ID2Name = None
	g_PtoConfig = None


#以下为对外接口
def InitNetConfig(sConfigFile):
	"""
	指定网络协议格式
	:param sConfigFile:配置文件
	:return:
	"""
	global g_PtoConfig, g_Name2ID, g_ID2Name
	data = json.load(open(sConfigFile, "r"))
	g_PtoConfig = data["ProConfig"]
	g_Name2ID = data["Name2ID"]
	g_ID2Name = data["ID2Name"]


#读数据
def UnpackNet(iConnID, sBuff):
	#对原数据进行解密

	#解析包头，判断数据有效性
	if len(sBuff) <= PACKET_HEAD_LEN:
		return
	try :
		iIndex, iLen = struct.unpack("!HH", sBuff[:PACKET_HEAD_LEN])
	except Exception, err:
		log.Fatal(str(err))
		return
	if len(sBuff) < PACKET_HEAD_LEN + iLen:
		log.Fatal("[UnpackNet] the packet is not full! iIndex=%s,iLen=%s,Data=%s" % (iIndex, iLen, sBuff))
		return

	#将数据加载到读内存中
	g_ReadPacket.__init__(sBuff[PACKET_HEAD_LEN:PACKET_HEAD_LEN+iLen])

	#按照指定的协议格式进行解包
	sPtoName = g_ID2Name[iIndex]
	dPtoConfig = g_PtoConfig[iIndex]
	if not dPtoConfig:
		log.Fatal("[UnpackNet] protocol %d is not supported" % iIndex)
		return
	dProtocol = {}
	for tArg in dPtoConfig["args"]:
		sName, sType = tArg[0], tArg[1]
		value = g_ReadPacket.Read(sType)
		if value == None:
			log.Fatal("[UnpackNet] protocol %d is error at (%s, %s)" % (iIndex, sName, sType))
			raise "[UnpackNet] protocol %d is error at (%s, %s)" % (iIndex, sName, sType)
		dProtocol[sName] = value
	return sPtoName, iLen, dProtocol


#写数据
def PackNet(iConnID, sName, data):
	"""
	压包，将源数据按照iIndex的协议格式进行压包
	:param sName:协议名称
	:param data:
	:return:
	"""
	#准备
	iIndex = g_Name2ID[sName]
	g_WritePacket.__init__(iIndex)
	#按照协议进行打包
	dPtoConfig = g_PtoConfig[iIndex]
	if not dPtoConfig:
		log.Fatal("[PackNet] protocol %d is not supported" % iIndex)
		return
	for tArg in dPtoConfig["args"]:
		sName, sType = tArg[0], tArg[1]
		if not sName in data:
			log.Fatal("[PackNet] protocol %d need (%s)" % (iIndex, sName))
			raise "[PackNet] protocol %d need (%s)" % (iIndex, sName)
		value = data[sName]
		if not g_WritePacket.Write(sType, value):
			log.Fatal("[PacketNet] protocol %d write failed at (%s=%s)" % (iIndex, sName, value))
	sData = g_WritePacket.Pack()
	#将整个数据进行加密
	return sData


__all__ = ["PACKET_HEAD_LEN", "DATA_TYPE", "InitNetConfig", "PackNet", "UnpackNet", ]