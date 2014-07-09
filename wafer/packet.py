#coding=utf-8
"""
@author : leecrest
@time   : 14-1-29 下午2:52
@brief  : 网络协议打包与解包
"""

import wafer.log as log
import struct
import json
import os


"""
协议数据包的格式：
+----------+----------+----------+
| crypt(1) |  len(2)  |   body   |
+----------+----------+----------+
1.crypt：1byte，body是否加密，0：未加密，1：加密
2.len：2byte，body的长度
3.body：协议内容

其中body的格式如下：
+----------+----------+----------+
|  id(2)   |  len(2)  |   body   |
+----------+----------+----------+

1.id：2byte，协议编号，唯一标示
2.len：2byte，body的长度
3.body：协议的二进制内容
"""
PACKET_HEAD_LEN		= 3 #包头的长度
PROTOCOL_HEAD_LEN   = 4 #协议头的长度
PACKET_MAX_SIZE		= 2 ** 16


#数据类型，格式：{"类型名称":(解析格式,长度),}
BASIC_TYPE = {
	"bool": ("?", 1),
    "int8": ("b", 1), "int16": ("h", 2), "int32": ("i", 4), "long": ("l", 8),
	"uint8": ("B", 1), "uint16": ("H", 2), "uint32": ("I", 4), "ulong": ("L", 8),
}



class CProtocolWriter:
	def __init__(self, iProtoID=0):
		self.m_ProtoID = iProtoID
		self.m_Length = 0
		self.m_Data = ""


	def __WriteString__(self, sValue, bList=False):
		#print "__WriteString__", sValue, bList
		if not self.m_ProtoID:
			return
		if bList:
			if not self.__WriteNumber__("uint8", len(sValue)):
				return
			for sItem in sValue:
				if not self.__WriteString__(sItem):
					return
		else:
			iLen = len(sValue)
			if self.m_Length + iLen + 1 > PACKET_MAX_SIZE:
				return
			self.m_Data += struct.pack("B%ds" % iLen, iLen, sValue)
			self.m_Length += iLen + 1
		return True


	def __WriteNumber__(self, sType, sValue, bList=False):
		#print "__WriteNumber__", sType, sValue, bList
		if not self.m_ProtoID or not sType in BASIC_TYPE:
			return
		if bList:
			if not self.__WriteNumber__("uint8", len(sValue)):
				return
			for sItem in sValue:
				if not self.__WriteNumber__(sType, sItem):
					return
		else:
			sFormat, iLen = BASIC_TYPE[sType]
			if self.m_Length + iLen > PACKET_MAX_SIZE:
				return
			self.m_Data += struct.pack(sFormat, sValue)
			self.m_Length += iLen
		return True


	def __WriteCustom__(self, sType, sValue, bList=False):
		if not self.m_ProtoID or not sType in g_CustomType:
			return
		if bList:
			if not self.__WriteNumber__("uint8", len(sValue)):
				return
			for sItem in sValue:
				if not self.__WriteCustom__(sType, sItem):
					return
		else:
			tArgList = g_CustomType[sType]
			if len(tArgList) != len(sValue):
				return
			iIndex = 0
			for tArg in tArgList:
				sArgName, sArgType = tArg[0], tArg[1]
				bArgList = False
				if len(tArg) >= 3:
					bArgList = tArg[2]
				if type(sValue) in (tuple, list):
					sArgVal = sValue[iIndex]
					iIndex += 1
				elif type(sValue) == dict:
					sArgVal = sValue[sArgName]
				else:
					return
				if sArgType == "string":
					if not self.__WriteString__(sArgVal, bArgList):
						return
				elif sArgType in BASIC_TYPE:
					if not self.__WriteNumber__(sArgType, sArgVal, bArgList):
						return
				elif sArgType in g_CustomType:
					if not self.__WriteCustom__(sArgType, sArgVal, bArgList):
						return
				else:
					return
		return True



	def Write(self, sType, sValue, bList=False):
		#print "<<<Write>>>", sType, sValue, bList
		if not self.m_ProtoID:
			return
		if sType == "string":
			return self.__WriteString__(sValue, bList)
		elif sType in BASIC_TYPE:
			return self.__WriteNumber__(sType, sValue, bList)
		elif sType in g_CustomType:
			return self.__WriteCustom__(sType, sValue, bList)
		else:
			log.Fatal("[WritePack]type=%s is not supported" % sType)


	def Pack(self):
		if not self.m_ProtoID:
			return
		data = struct.pack("HH", self.m_ProtoID, self.m_Length) + self.m_Data
		self.m_ProtoID = 0
		self.m_Length = 0
		self.m_Data = ""
		return data



class CProtocolReader:
	def __init__(self, data):
		self.m_Offset = 0
		self.m_Data = data
		self.m_Length = len(data)


	#读取字符串类型
	def __ReadString__(self, bList=False):
		if bList:
			iValueLen = self.__ReadNumber__("uint8")
			if iValueLen is None:
				return
			sValueList = []
			for i in xrange(iValueLen):
				sValue = self.__ReadString__()
				if sValue is None:
					return
				sValueList.append(sValue)
			return sValueList
		else:
			iValueLen = self.Read("uint8")
			sFormat = "%ds" % iValueLen
			if self.m_Offset + iValueLen > self.m_Length:
				return
			sValue = struct.unpack_from(sFormat, self.m_Data, self.m_Offset)
			self.m_Offset += iValueLen
			return sValue[0]


	#读取数字类型
	def __ReadNumber__(self, sType, bList=False):
		if not sType in BASIC_TYPE:
			return
		if bList:
			iValueLen = self.__ReadNumber__("uint8")
			if iValueLen is None:
				return
			sValueList = []
			for i in xrange(iValueLen):
				sValue = self.__ReadNumber__(sType)
				if sValue is None:
					return
				sValueList.append(sValue)
			return sValueList
		else:
			sFormat, iValueLen = BASIC_TYPE[sType]
			if self.m_Offset + iValueLen > self.m_Length:
				return
			value = struct.unpack_from(sFormat, self.m_Data, self.m_Offset)
			self.m_Offset += iValueLen
			return value[0]


	#读取自定义类型
	def __ReadCustom__(self, sType, bList=False):
		if not sType in g_CustomType:
			return
		if bList:
			iValueLen = self.__ReadNumber__("uint8")
			if iValueLen is None:
				return
			sValueList = []
			for i in xrange(iValueLen):
				sValue = self.__ReadCustom__(sType)
				if sValue is None:
					return
				sValueList.append(sValue)
			return sValueList
		else:
			dValue = {}
			for tArgs in g_CustomType[sType]:
				sArgName, sArgType = tArgs[0], tArgs[1]
				bArgList = False
				if len(tArgs) >= 3:
					bArgList = tArgs[2]
				if sArgType == "string":
					sValue = self.__ReadString__(bArgList)
				elif sArgType in BASIC_TYPE:
					sValue = self.__ReadNumber__(sArgType, bArgList)
				elif sArgType in g_CustomType:
					sValue = self.__ReadCustom__(sArgType, bArgList)
				else:
					return
				dValue[sArgName] = sValue
			return dValue


	#对外接口
	def Read(self, sType, bList=False):
		if sType == "string":
			return self.__ReadString__(bList)
		elif sType in BASIC_TYPE:
			return self.__ReadNumber__(sType, bList)
		elif sType in g_CustomType:
			return self.__ReadCustom__(sType, bList)
		else:
			log.Fatal("[ReadPack]type=%s is not supported" % sType)



if not "g_ProtocolReader" in globals():
	g_ProtocolReader = CProtocolReader("")
	g_ProtocolWriter = CProtocolWriter()
	g_Name2ID = {}
	g_ProtoCfg = {}
	g_CustomType = {}


#以下为对外接口
def InitNetProto(sProtoList, sTypeList=None):
	"""
	网络协议的初始化
	:param sProtoList:协议定义文件
	:param sTypeList:协议中的自定义类型定义文件
	:return:
	"""
	global g_ProtoCfg, g_Name2ID, g_CustomType
	if type(sProtoList) == str:
		sProtoList = [sProtoList,]
	g_ProtoCfg = {}
	g_Name2ID = {}
	g_CustomType = {}
	for sFile in sProtoList:
		if not os.path.exists(sFile) or not os.path.isfile(sFile):
			continue
		data = json.load(open(sFile, "r"))
		if not data:
			continue
		g_Name2ID.update(data["Name2ID"])
		if data["PtoCfg"]:
			for k,v in data["PtoCfg"].iteritems():
				g_ProtoCfg[int(k)] = v

	if not sTypeList:
		return
	if type(sTypeList) == str:
		sTypeList = [sTypeList,]
	for sFile in sTypeList:
		if not os.path.exists(sFile) or not os.path.isfile(sFile):
			continue
		data = json.load(open(sFile, "r"))
		if not data:
			continue
		g_CustomType.update(data)


#根据协议名称获得协议编号
def Name2ID(sName):
	return g_Name2ID.get(sName, 0)


#解析网络包
def UnpackNet(iConnID, sBuff):
	if len(sBuff) <= PACKET_HEAD_LEN:
		return
	#解析网络包
	try:
		iCrypt, iPackLen = struct.unpack("!BH", sBuff[:PACKET_HEAD_LEN])
	except Exception, err:
		log.Fatal(str(err))
		return
	if len(sBuff) < PACKET_HEAD_LEN + iPackLen:
		return
	#包体，协议数据部分
	sProtoBuff = sBuff[PACKET_HEAD_LEN : PACKET_HEAD_LEN + iPackLen]
	#解密
	if iCrypt:
		sProtoBuff = Decrypt(iConnID, sProtoBuff)
	#判断数据有效性
	if not sProtoBuff or len(sProtoBuff) <= PROTOCOL_HEAD_LEN:
		return
	try :
		iProtoID, iProtoLen = struct.unpack("HH", sProtoBuff[:PROTOCOL_HEAD_LEN])
	except Exception, err:
		log.Fatal(str(err))
		return
	if len(sProtoBuff) < PROTOCOL_HEAD_LEN + iProtoLen:
		return
	sMetaData = sProtoBuff[PROTOCOL_HEAD_LEN : PROTOCOL_HEAD_LEN + iProtoLen]
	dProtoCfg = g_ProtoCfg.get(iProtoID, None)
	if not dProtoCfg:
		#本服务器没有此协议的定义，不解包
		return "default", iPackLen, sMetaData

	#将数据加载到读内存中
	g_ProtocolReader.__init__(sMetaData)
	#按照指定的协议格式进行解包
	sProtoName = dProtoCfg["name"]
	if not dProtoCfg:
		log.Fatal("[UnpackNet] protocol %d is not supported" % iProtoID)
		return
	dProtocol = {}
	for tArg in dProtoCfg["args"]:
		sArgName, sArgType = tArg[0], tArg[1]
		bList = False
		if len(tArg) >= 3:
			bList = tArg[2]
		sArgValue = g_ProtocolReader.Read(sArgType, bList)
		if sArgValue is None:
			log.Fatal("[UnpackNet] protocol %d is error at (%s, %s)" % (iProtoID, sArgName, sArgType))
			return
		dProtocol[sArgName] = sArgValue
	return sProtoName, iPackLen, dProtocol


#打包协议
def PackProto(sProtoName, dProtocol):
	"""
	压包，将源数据按照iIndex的协议格式进行压包
	:param sProtoName:协议名称
	:param dProtocol:
	:return:
	"""
	#准备
	iProtoID = g_Name2ID[sProtoName]
	g_ProtocolWriter.__init__(iProtoID)
	#按照协议进行打包
	dProtoCfg = g_ProtoCfg[iProtoID]
	if not dProtoCfg:
		log.Fatal("[PackNet] protocol %d is not supported" % iProtoID)
		return
	for tArg in dProtoCfg["args"]:
		sName, sType = tArg[0], tArg[1]
		if not sName in dProtocol:
			log.Fatal("[PackNet] protocol %d need (%s)" % (iProtoID, sName))
			raise "[PackNet] protocol %d need (%s)" % (iProtoID, sName)
		bList = False
		if len(tArg) >= 3:
			bList = tArg[2]
		if not bList:
			sValue = dProtocol[sName]
			if not g_ProtocolWriter.Write(sType, sValue):
				log.Fatal("[PacketNet] protocol %d write failed at (%s,%s,%s)" % (iProtoID, sName, sType, sValue))
				return
		else:
			sValueList = dProtocol[sName]
			g_ProtocolWriter.Write("uint8", len(sValueList))
			for sValue in sValueList:
				if not g_ProtocolWriter.Write(sType, sValue):
					log.Fatal("[PacketNet] protocol %d write failed at (%s,%s,%s)" % (iProtoID, sName, sType, sValue))
					return
	return g_ProtocolWriter.Pack()


#直接打包协议
#def PackData(iProtoID, sBuff):
#	if not sBuff:
#		return
#	return struct.pack("HH", iProtoID, len(sBuff)) + sBuff


#打包整个网络包
def PackNet(sBuff, bCrypt, *args):
	if not sBuff:
		return
	if bCrypt and len(args) > 0:
		sBuff = Encrypt(args[0], sBuff)
		if not sBuff:
			return
	return struct.pack("!BH", int(bCrypt), len(sBuff)) + sBuff


#数据加密
def Encrypt(iConnID, sBuff):
	if not iConnID or not sBuff:
		return sBuff
	return sBuff


#数据解密
def Decrypt(iConnID, sBuff):
	if not iConnID or not sBuff:
		return sBuff
	return sBuff



__all__ = ["PACKET_HEAD_LEN", "BASIC_TYPE", "InitNetProto", "Name2ID",
           "PackProto", "PackNet", "UnpackNet"]