#coding=utf-8
"""
@author : leecrest
@time   : 14-1-29 上午10:40
@brief  : 服务器组的启动器，执行此文件将会按序启动所有服务器
"""

#主进程为Master，其余服务器在子进程中启动


import json
import subprocess
import traceback
import wafer


if __name__ == "__main__":
	try:
		sConfigFile = "config/server.json"
		dConfig = json.load(open(sConfigFile, "r"))

		#启动子进程
		for sName in dConfig.iterkeys():
			if sName == "master":
				continue
			cmd = "python %s %s %s" % ("launch.py", sName, sConfigFile)
			subprocess.Popen(cmd)
		#启动主服务器
		app = wafer.CreateServer("master", dConfig["master"])
		app.Start()
	except Exception, e:
		print "="*20, "Error", "="*20
		print e
		print traceback.format_exc()
