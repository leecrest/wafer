#coding=utf-8
"""
@author : leecrest
@time   : 14-1-14 上午12:01
@brief  : 通用函数集合
"""
import sys
import copy
import random


class CFunctor:
	"""
	对回调函数的一次包装
	"""

	def __init__(self, fn, *args):
		self._fn = fn
		self._args = args


	def __call__(self, *args):
		return self._fn(*(self._args + args))



class CSingleton(type):
	"""
	单件模式，通过原型继承实现
	示例如下：

	class CBase:
		__metaclass__ = CSingleton

		def Show(self):
			print "Show"

	CBase().Show()
	"""

	def __init__(cls, name, bases, dic):
		super(CSingleton, cls).__init__(name, bases, dic)
		cls.instance = None

	def __call__(cls, *args, **kwargs):
		if cls.instance is None:
			cls.instance = super(CSingleton, cls).__call__(*args, **kwargs)
		return cls.instance


#加载、重新加载
def Reload(sRoot, sFile):
	"""
	热更新某个代码文件
	:param sRoot: 服务器主路径，根目录名称
	:param sFile: 需要更新的文件路径，相对服务器根目录的绝对路径
	:return:
	"""
	if not sFile:
		return
	if sFile.endswith(".__init__"):
		sFile = sFile[:-9]
	sModName = "%s/%s" % (sRoot, sFile)
	if sModName in sys.modules:
		mod = reload(sFile)
	else:
		mod = __import__(sFile)
	sList = sFile.split(".")
	for sItem in sList[1:]:
		mod = getattr(mod, sItem)
	return mod


def CopyList(iList):
	return iList[:]


def CopyTuple(iTuple):
	return iTuple[:]


def CopyDict(iDict):
	return copy.copy(iDict)


def RandomList(iList):
	if not iList:
		return
	iPos = random.randint(0, len(iList)-1)
	return iList[iPos]



