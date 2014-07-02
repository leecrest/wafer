# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/30 20:31
@brief  : 
"""

import os, sys

#载入测试
#import test_module
#from test_module import *
import test_module as a

#更新前做一些事情
print u"模块内容：", dir(a)

print "="*50
print u"准备更新"
os.system("pause")

x = a.NAME
print x
#===========================================================================
#开始更新
name = "test_module"
old = sys.modules.get(name, None)
if old:
	dOldAttr = {}
	for i in dir(old):
		dOldAttr[i] = getattr(old, i)
	new = reload(old)

	print dOldAttr.keys()
	print dir(new)
else:
	new = __import__(name)


#===========================================================================
print u"更新完成"
print "="*50
print u"开始更新检查"

print u"模块内容：", dir(new)
print a.NAME, a.NAME2
print x