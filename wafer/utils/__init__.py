#coding=utf-8
"""
@author : leecrest
@time   : 14-1-14 上午12:01
@brief  : 通用函数集合
"""
import copy


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



def CopyList(iList):
	return iList[:]


def CopyTuple(iTuple):
	return iTuple[:]


def CopyDict(iDict):
	return copy.copy(iDict)



import log
