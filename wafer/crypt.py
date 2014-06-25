#coding=utf-8
"""
@author : leecrest
@time   : 14-6-13 上午8:27
@brief  : 加密与解密
"""

g_KeyDict = {}      #记录每个链接的Key，数据格式：{ 连接编号：Key }
g_ReuseList = []    #回收列表


def CreateKey(iConnID):
	"""
	为每个连接生成不同的key
	:param iConnID: 链接编号
	:return: key
	"""
	global g_KeyDict
	if g_ReuseList:
		sKey = g_ReuseList.pop(0)
	else:
		#重新生成
		sKey = ""
	g_KeyDict[iConnID] = sKey
	return sKey


def ReleaseKey(iConnID):
	"""
	回收Key，在链接确认断开时调用。断线重练不需要调用。
	:param iConnID: 链接编号
	:return:
	"""
	if not iConnID in g_KeyDict:
		return
	sKey = g_KeyDict[iConnID]
	del g_KeyDict[iConnID]
	g_ReuseList.append(sKey)



def Encrypt(sKey, sText):
	"""
	加密
	:param sKey: 加密key
	:param sText: 明文
	:return: 密文
	"""
	return sText


def Decrypt(sKey, sText):
	"""
	解密
	:param sKey: 解密key
	:param sText: 密文
	:return: 明文
	"""
	return sText


__all__ = ["CreateKey", "ReleaseKey", "Encrypt", "Decrypt"]

