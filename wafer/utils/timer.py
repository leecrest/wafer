#coding=utf-8
"""
@author : leecrest
@time   : 14-1-12 下午5:06
@brief  : 定时器系统，封装twisted中的定时器函数
"""

from twisted.internet import reactor
from wafer.utils import *

if not "g_TimerCtrl" in globals():
	g_TimerCtrl = {}
	g_TimerID = 10000

#=====================================================================
def NewTimerID():
	global g_TimerID
	g_TimerID += 1
	return g_TimerID


def TimerCallback(iTimerID, sFlag):
	tTimerDict = g_TimerCtrl.get(iTimerID, None)
	if not tTimerDict:
		return
	oTimer = tTimerDict.get(sFlag, None)
	if not oTimer:
		return
	oTimer.Exec()


class CTimerCall:
	def __init__(self, iTimerID, sFlag, cbFunc, iDelay, iInterval=0, iMaxCount=0):
		self.m_TimerID  = iTimerID
		self.m_Flag     = sFlag
		self.m_Func     = cbFunc
		self.m_Delay    = iDelay
		self.m_Interval = iInterval
		self.m_MaxCount = iMaxCount
		self.m_Call     = None
		if iMaxCount > 0:
			self.m_CurCount = 0

	def Active(self):
		self.m_Call = reactor.callLater(self.m_Delay/1000.0, TimerCallback, self.m_TimerID, self.m_Flag)

	def Exec(self):
		self.m_Func()
		if self.m_Interval < 1:
			self.Remove()
			return
		if self.m_MaxCount > 0:
			self.m_CurCount += 1
			if self.m_CurCount >= self.m_MaxCount:
				self.Remove()
				return
		del self.m_Call
		self.m_Call = reactor.callLater(self.m_Interval/1000.0, TimerCallback, self.m_TimerID, self.m_Flag)

	def Remove(self):
		if not self.m_Call.cancelled and not self.m_Call.called:
			self.m_Call.cancel()
			self.m_Call = None
		oTimerDict = g_TimerCtrl.get(self.m_TimerID, {})
		if not oTimerDict:
			return
		if not self.m_Flag in oTimerDict:
			return
		del oTimerDict[self.m_Flag]
		if not oTimerDict:
			del g_TimerCtrl[self.m_TimerID]


#=====================================================================
#对外接口

def SetTimer(iTimerID, sFlag, cbFunc, iDelay=0, iInterval=0, iMaxCount=0):
	"""
	设置定时器，如果此iTimerID的定时器已经存在，就顶替掉
	参数说明：
	@iTimerID   ：定时器编号，如果为0，则由系统分配
	@sFlag      : 定时器标记
	@cbFunc     ：回调函数
	@iDelay     ：延迟时间，单位：ms，指定时间到后定时器才开始执行
	@iInterval  ：执行间隔，单位：ms，定时器的心跳时间
	"""
	if iTimerID <= 0:
		iTimerID = NewTimerID()
	if iDelay < 0:
		iDelay = 0
	if iInterval < 1:
		iInterval = 0
	tTimerDict = g_TimerCtrl.get(iTimerID, {})
	oTimer = tTimerDict.get(sFlag, None)
	if oTimer:
		oTimer.Remove()
	oTimer = CTimerCall(iTimerID, sFlag, cbFunc, iDelay, iInterval, iMaxCount)
	tTimerDict[sFlag] = oTimer
	g_TimerCtrl[iTimerID] = tTimerDict
	oTimer.Active()


def RemoveTimer(*args):
	"""
	删除定时器，
	参数说明：
	@iTimerID   ：定时器ID，如果只有定时器ID，就删除该ID下所有的定时器
	@sFlag      ：定时器标识
	"""
	iTimerID = args[0]
	sFlag = ""
	if len(args) > 1:
		sFlag = args[1]
	if not iTimerID in g_TimerCtrl:
		return
	oTimerDict = CopyDict(g_TimerCtrl[iTimerID])
	if not sFlag:
		for sFlag, oTimer in oTimerDict.iteritems():
			oTimer.Remove()
	elif sFlag in oTimerDict:
		oTimer = oTimerDict[sFlag]
		oTimer.Remove()
		del oTimerDict[sFlag]


