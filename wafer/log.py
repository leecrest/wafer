#coding=utf-8
"""
@author : leecrest
@time   : 14-1-12 下午3:53
@brief  : 日志系统，自行开发
"""
#设计如下：
#每个进程将拥有一组日志，
#对于一些特殊的功能日志，可以使用单独的日志文件，比如money

from wafer.utils import *
import os
import datetime
import logging


def GetTimeString():
	tCur = datetime.datetime.now()
	sTime = "%02d-%02d-%02d %02d:%02d:%02d.%03d"
	sTime = sTime % (tCur.year, tCur.month, tCur.day, tCur.hour, tCur.minute, tCur.second, tCur.microsecond/1000)
	return sTime

#日志文件
class CLogFileMgr:
	__metaclass__ = CSingleton

	def __init__(self):
		self.m_Init = False
		self.m_LogPath = ""
		self.m_LogDict = {}


	def __del__(self):
		for fHandle in self.m_LogDict.itervalues():
			if not fHandle:
				continue
			fHandle.flush()
			fHandle.close()


	def InitPath(self, sPath):
		self.m_LogPath = sPath
		self.m_Init = True


	def Write(self, sName, sMsg):
		if not self.m_Init:
			return
		if not sName in self.m_LogDict:
			sPath = os.path.join(self.m_LogPath, sName)
			self.m_LogDict[sName] = open(sPath, "w")
		fHandle = self.m_LogDict[sName]
		sMsg = "%s %s\n" % (GetTimeString(), sMsg)
		fHandle.write(sMsg)
		fHandle.flush()


#=====================================================================
#对外接口

#初始化主进程日志
def InitLog(dConfig):
	#模块日志的路径
	sPath = dConfig.get("path", "./")
	if not os.path.exists(sPath):
		os.makedirs(sPath)
	CLogFileMgr().InitPath(sPath)

	sFile = os.path.join(sPath, dConfig.get("file", "Log.txt"))
	sLevel = dConfig.get("level", "warn")
	if sLevel == "debug":
		iLevel = logging.DEBUG
	if sLevel == "warning":
		iLevel = logging.WARNING
	elif sLevel == "error":
		iLevel = logging.ERROR
	elif sLevel == "critical":
		iLevel = logging.CRITICAL
	else:
		iLevel = logging.INFO
	sFormat = dConfig.get("format", "%(asctime)s %(levelname)s %(message)s")
	logging.basicConfig(filename=sFile, level=iLevel, filemode="w", format=sFormat)


def Info(sMsg, *args):
	if args:
		sMsg = sMsg % args
	logging.getLogger().info(sMsg)
	print "[Info]", sMsg


def Debug(sMsg, *args):
	if args:
		sMsg = sMsg % args
	logging.getLogger().debug(sMsg)
	print "[Debug]", sMsg


def Error(sMsg, *args):
	if args:
		sMsg = sMsg % args
	logging.getLogger().error(sMsg)
	print "[Error]", sMsg


def Fatal(sMsg, *args):
	if args:
		sMsg = sMsg % args
	logging.getLogger().critical(sMsg)
	print "[Fatal]", sMsg


#模块日志
def LogFile(sFile, sMsg, *args):
	if args:
		sMsg = sMsg % args
	CLogFileMgr().Write(sFile, sMsg)


__all__ = ["InitLog", "Info", "Debug", "Error", "Fatal", "LogFile"]
