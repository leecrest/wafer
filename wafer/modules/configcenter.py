# coding=utf-8
"""
@author : leecrest
@time   : 2014/7/5 14:47
@brief  : 配置管理
"""

"""
模块功能如下：
1、每个服务器，将所有数值文件集中到一个目录下，或者打包成pak
2、服务器启动时，将由本模块进行数据加载
3、每个数值文件，将变成本模块的一个数值节点
4、
"""

import wafer.log as log
import os
import json


RES_TYPE_PATH   = 1 #资源采用目录模式
RES_TYPE_PAK    = 2 #资源采用.pak包的模式


class CConfigCenter:

	def __init__(self):
		self.m_Type     = RES_TYPE_PATH #资源类型
		self.m_Crypt    = False         #是否加密
		self.m_Path     = ""            #资源路径
		self.m_Data     = {}            #资源数据根目录
		self.m_Init     = False
		self.m_IncludeExt   = []        #包含扩展名列表
		self.m_ExcludeExt   = []        #排除扩展名列表
		self.m_IncludeDir   = []        #包含目录列表
		self.m_ExcludeDir   = []        #排除目录列表


	def InitConfig(self, dConfig):
		"""
		初始化配置管理中心，务必在配置管理中心实例化后优先调用
		@dConfig，dict，配置字典
		"""
		if self.m_Init:
			raise "CC.InitConfig should be called first"
		self.m_Type       = dConfig.get("type", RES_TYPE_PATH)
		self.m_Path       = dConfig.get("path", "./")
		if self.m_Type == RES_TYPE_PATH:
			if not os.path.exists(self.m_Path) or not os.path.isdir(self.m_Path):
				raise "[CC] path(%s) not existed" % self.m_Path
		elif self.m_Type == RES_TYPE_PAK:
			if not os.path.exists(self.m_Path) or not os.path.isfile(self.m_Path):
				raise "[CC] file(%s) not existed" % self.m_Path
		else:
			raise "[CC]Error ResType(%d)" % self.m_Type

		self.m_Crypt      = dConfig.get("crypt", False)
		self.m_IncludeExt = dConfig.get("include_ext", ".json").split(",")
		sValue = dConfig.get("exclude_ext", "")
		if sValue:
			self.m_ExcludeExt = sValue.split(",")
		sValue = dConfig.get("include_dir", "")
		if sValue:
			self.m_IncludeDir = sValue.split(",")
		sValue = dConfig.get("exclude_dir", "")
		if sValue:
			self.m_ExcludeDir = sValue.split(",")

		if self.m_Type == RES_TYPE_PATH:
			self.m_Data = self.LoadConfigByPath(self.m_Path)
		elif self.m_Type == RES_TYPE_PAK:
			self.m_Data = self.LoadConfigByPak()

		self.m_Init = True
		log.Info("[CC] init success!")


	def ValidFile(self, sExt):
		"""判断sExt的扩展名是否有效"""
		if sExt in self.m_ExcludeExt:
			return False
		return sExt in self.m_IncludeExt


	def ValidDir(self, sDir):
		"""判断sDir的目录名是否有效"""
		if sDir in self.m_ExcludeDir:
			return False
		if not self.m_IncludeDir:
			return True
		return sDir in self.m_IncludeDir


	def LoadConfigByPath(self, sRoot):
		"""
		加载指定目录下的资源文件到内存中
		@dData，dict，资源的存储地址
		@sRoot，string，当前需要访问的目录
		"""
		dData = {}
		for sPath in os.listdir(sRoot):
			sFull = os.path.join(sRoot, sPath)
			if os.path.isfile(sFull):
				sName, sExt = os.path.splitext(sPath)
				if not self.ValidFile(sExt):
					continue
				dData[sName] = self.LoadFile(sFull)
				log.Info("[CC] load : %s -> %s" % (sName, sFull))
			elif os.path.isdir(sFull) and self.ValidDir(sPath):
				dData[sPath] = self.LoadConfigByPath(sFull)
		return dData


	def LoadConfigByPak(self):
		"""
		加载指定的数据包文件
		"""
		dData = {}
		#等待添加
		return dData



	def LoadFile(self, sPath):
		"""
		加载指定的资源文件
		@sPath，string，资源文件的路径
		"""
		if not self.m_Crypt:
			return json.load(open(sPath, "r"))
		#等待添加


	def Query(self, sKey):
		"""
		查询键值
		:param sKey:配置文件名称
		:return:
		"""
		if not self.m_Init:
			return
		return self.m_Data.get(sKey, None)


if not "g_ConfigCenter" in globals():
	g_ConfigCenter = CConfigCenter()


def InitConfig(dConfig):
	g_ConfigCenter.InitConfig(dConfig)


def GetConfig(sKey):
	return g_ConfigCenter.Query(sKey)


__all__ = ["InitConfig", "GetConfig"]
