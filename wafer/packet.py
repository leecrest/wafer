#coding=utf-8
"""
@author : leecrest
@time   : 14-1-29 下午2:52
@brief  : 网络定义
"""

import wafer.log as log
import struct


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



class CWritePacket:
	def __init__(self):
		self.m_Type = 0
		self.m_Len = 0
		self.m_Data = ""


	def __Valid__(self, iLen):
		return self.m_Len + iLen <= PACKET_MAX_SIZE


	def __WriteBool__(self, value):
		if not self.__Valid__(1):
			return
		self.m_Data += struct.pack("?", value)
		self.m_Len += 1


	def __WriteInt__(self, value, iLen):
		if not self.__Valid__(iLen):
			return
		if iLen == 1:
			sFormat = "b"
		elif iLen == 2:
			sFormat = "h"
		elif iLen == 4:
			sFormat = "i"
		elif iLen == 8:
			sFormat = "l"
		else:
			sFormat = "i"
		self.m_Data += struct.pack(sFormat, value)
		self.m_Len += iLen


	def __WriteUInt__(self, value, iLen):
		if not self.__Valid__(iLen):
			return
		if iLen == 1:
			sFormat = "B"
		elif iLen == 2:
			sFormat = "H"
		elif iLen == 4:
			sFormat = "I"
		elif iLen == 8:
			sFormat = "L"
		else:
			sFormat = "I"
		self.m_Data += struct.pack(sFormat, value)
		self.m_Len += iLen


	def __WriteString__(self, value):
		if not value:
			return
		iLen = len(value)
		if not self.__Valid__(iLen+1):
			return
		self.m_Data += struct.pack("B%ds"%iLen, iLen, value)
		self.m_Len += iLen+1


	def __Pack__(self):
		data = struct.pack("!HH", self.m_Type, self.m_Len) + self.m_Data
		self.m_Type = 0
		self.m_Len = 0
		self.m_Data = ""
		return data


class CReadPacket:
	def __init__(self, data):
		self.m_Offset = 0
		self.m_Data = data
		self.m_Len = len(data)


	def __Valid__(self, iLen):
		return self.m_Offset + iLen <= self.m_Len


	def __ReadBool__(self):
		if not self.__Valid__(1):
			return
		value = struct.unpack_from("?", self.m_Data, self.m_Offset)
		self.m_Offset += 1
		return value[0]


	def __ReadInt__(self, iLen):
		if not self.__Valid__(iLen):
			return
		if iLen == 1:
			sFormat = "b"
		elif iLen == 2:
			sFormat = "h"
		elif iLen == 4:
			sFormat = "i"
		elif iLen == 8:
			sFormat = "l"
		else:
			sFormat = "i"
		value = struct.unpack_from(sFormat, self.m_Data, self.m_Offset)
		self.m_Offset += iLen
		return value[0]


	def __ReadUInt__(self, iLen):
		if not self.__Valid__(iLen):
			return
		if iLen == 1:
			sFormat = "B"
		elif iLen == 2:
			sFormat = "H"
		elif iLen == 4:
			sFormat = "I"
		elif iLen == 8:
			sFormat = "L"
		else:
			sFormat = "I"
		value = struct.unpack_from(sFormat, self.m_Data, self.m_Offset)
		self.m_Offset += iLen
		return value[0]


	def __ReadString__(self):
		iLen = self.__ReadInt__(1)
		if not iLen:
			return
		if not self.__Valid__(iLen):
			return
		value = struct.unpack_from("%ds"%iLen, self.m_Data, self.m_Offset)
		self.m_Offset += iLen
		return value[0]


if not "g_ReadPacket" in globals():
	g_ReadPacket = CReadPacket("")
	g_WritePacket = CWritePacket()
	g_PtoConfig = None


#以下为对外接口
def InitNetConfig(dPtoConfig):
	"""
	指定网络协议格式
	:param dPtoConfig:协议配置
	:return:
	"""
	global g_PtoConfig
	g_PtoConfig = dPtoConfig


#读数据
def UnpackNetData(data):
	#对原数据进行解密

	#解析包头，判断数据有效性
	if len(data) <= PACKET_HEAD_LEN:
		return
	try :
		iIndex, iLen = struct.unpack("!HH", data[:PACKET_HEAD_LEN])
	except Exception, err:
		log.critical(str(err))
		return
	if len(data) < PACKET_HEAD_LEN + iLen:
		log.critical("[UnPack] the packet is not full! iIndex=%s,iLen=%s,Data=%s" % (iIndex, iLen, data))
		return
	#将数据加载到读内存中
	g_ReadPacket.__init__(data[PACKET_HEAD_LEN:PACKET_HEAD_LEN+iLen])
	#按照指定的协议格式进行解包
	dProtocol = {}
	return iIndex, iLen, dProtocol


#写数据
def PackPrepare(iType):
	g_WritePacket.__init__()
	g_WritePacket.m_Type = iType


def PackNetData(iIndex, data):
	"""
	压包，将源数据按照iIndex的协议格式进行压包
	:param iIndex:协议编号
	:param data:
	:return:
	"""
	pass












































#=======================================================================================================================


#=======================================================================================================================



def PackBool(value):
	g_WritePacket.__WriteBool__(value)
def PackUInt8(value):
	g_WritePacket.__WriteUInt__(value, 1)
def PackUInt16(value):
	g_WritePacket.__WriteUInt__(value, 2)
def PackUInt32(value):
	g_WritePacket.__WriteUInt__(value, 4)
def PackUInt64(value):
	g_WritePacket.__WriteUInt__(value, 8)
def PackInt8(value):
	g_WritePacket.__WriteInt__(value, 1)
def PackInt16(value):
	g_WritePacket.__WriteInt__(value, 2)
def PackInt32(value):
	g_WritePacket.__WriteInt__(value, 4)
def PackInt64(value):
	g_WritePacket.__WriteInt__(value, 8)
def PackString(value):
	value = str(value)
	g_WritePacket.__WriteString__(value)



#=======================================================================================================================



def UnpackBool():
	return g_ReadPacket.__ReadBool__()
def UnpackUInt8():
	return g_ReadPacket.__ReadUInt__(1)
def UnpackUInt16():
	return g_ReadPacket.__ReadUInt__(2)
def UnpackUInt32():
	return g_ReadPacket.__ReadUInt__(4)
def UnpackUInt64():
	return g_ReadPacket.__ReadUInt__(8)
def UnpackInt8():
	return g_ReadPacket.__ReadInt__(1)
def UnpackInt16():
	return g_ReadPacket.__ReadInt__(2)
def UnpackInt32():
	return g_ReadPacket.__ReadInt__(4)
def UnpackInt64():
	return g_ReadPacket.__ReadInt__(8)
def UnpackString():
	return g_ReadPacket.__ReadString__()


def GetPackData():
	return g_WritePacket.__Pack__()


def GetUnpackData():
	return g_ReadPacket.m_Data

__all__ = ["PACKET_HEAD_LEN",

           "PackPrepare", "PackBool", "PackString",
           "PackInt8", "PackInt16", "PackInt32", "PackInt64",
           "PackUInt8", "PackUInt16", "PackUInt32", "PackUInt64",

           "UnpackPrepare", "UnpackBool", "UnpackString",
           "UnpackInt8", "UnpackInt16", "UnpackInt32", "UnpackInt64",
           "UnpackUInt8", "UnpackUInt16", "UnpackUInt32", "UnpackUInt64",

           "GetUnpackData", "GetPackData"]
