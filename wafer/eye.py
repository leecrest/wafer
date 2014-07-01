# coding=utf-8
"""
@author : leecrest
@time   : 2014/7/1 20:37
@brief  : 监控系统
"""

import wafer
import wafer.rpc as rpc


class CEyeClient:
	"""
	监控客户端，收集本地服务器的硬件数据，服务器自定义数据等
	"""
	def __init__(self, sName, dConfig):
		sRpcName = dConfig["name"]
		tAddress = (dConfig["host"], dConfig["port"])
		self.m_RpcNode = rpc.CreateRpcClient(sName, sRpcName, tAddress)
		self.m_RpcNode.SetLocals({
			"eye_sys_info" : self.GetSystemInfo,
		})


	def GetSystemInfo(self):
		return



class CEyeServer:

	def __init__(self, sName, dConfig):
		sRpcName = dConfig["name"]
		self.m_RpcNode = rpc.CreateRpcServer(sRpcName, dConfig["port"])


	def GetSystemInfo(self):
		for sName in self.m_RpcNode.GetClientList():
			self.m_RpcNode.CallClient(sName, "eye_sys_info")

