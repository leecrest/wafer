#coding=utf-8
"""
@author : leecrest
@time   : 14-1-29 上午11:02
@brief  : 单个服务器的启动程序
"""


import wafer.server
import sys
import os
import traceback
import json


if os.name != "nt" and os.name != "posix":
	#对系统的类型的判断，如果不是NT系统的话使用epoll
	from twisted.internet import epollreactor
	epollreactor.install()


if __name__ == "__main__":
	try:
		args = sys.argv
		#args = ["python" "Name" "config.json"]
		if len(args) <= 3:
			raise u"启动参数有误"
		app = wafer.server.CreateApp(args[1], args[2])
		app.Start()
	except Exception, e:
		print "="*20, "Error", "="*20
		print e
		print traceback.format_exc()
