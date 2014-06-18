#coding=utf-8
"""
@author : leecrest
@time   : 14-6-16 下午10:29
@brief  : 配置管理中心
"""
from wafer.utils import CSingleton
import marshal
import os
import json


RES_TYPE_PATH   = 1 #资源采用目录模式
RES_TYPE_PAK    = 2 #资源采用.pak包的模式


class CConfigCenter:
	__metaclass__ = CSingleton


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
		iType       = dConfig.get("type", RES_TYPE_PATH)
		bCrypt      = dConfig.get("crypt", False)
		sPath       = dConfig.get("path", "./")
		if iType == RES_TYPE_PATH:
			if not os.path.exists(sPath) or not os.path.isdir(sPath):
				raise "[CC] path(%s) not existed" % sPath
			self.m_Type     = iType
			self.m_Crypt    = bCrypt
			self.m_Path     = sPath
			self.m_IncludeExt = dConfig.get("include_ext", ".dat").split(",")
			self.m_ExcludeExt = dConfig.get("exclude_ext", "").split(",")
			self.m_IncludeDir = dConfig.get("include_dir", "").split(",")
			self.m_ExcludeDir = dConfig.get("exclude_dir", "").split(",")
			self.LoadConfigByPath(self.m_Data, self.m_Path)
		elif iType == RES_TYPE_PAK:
			if not os.path.exists(sPath) or not os.path.isfile(sPath):
				raise "[CC] file(%s) not existed" % sPath
			self.m_Type     = iType
			self.m_Crypt    = bCrypt
			self.m_Path     = sPath
			self.m_IncludeExt = dConfig.get("include_ext", ".dat").split(",")
			self.m_ExcludeExt = dConfig.get("exclude_ext", "").split(",")
			self.m_IncludeDir = dConfig.get("include_dir", "").split(",")
			self.m_ExcludeDir = dConfig.get("exclude_dir", "").split(",")
			self.LoadConfigByPak()
		else:
			raise "[CC]Error ResType(%d)" % self.m_ResType


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


	def LoadConfigByPath(self, dData, sRoot):
		"""
		加载指定目录下的资源文件到内存中
		@dData，dict，资源的存储地址
		@sRoot，string，当前需要访问的目录
		"""
		dData = {}
		for sPath in os.listdir(sRoot):
			sFull = os.path.join(sRoot, sPath)
			sName, sExt = os.path.splitext(sPath)
			if os.path.isfile(sFull) and self.ValidFile(sExt):
				dData[sName] = self.LoadFile(sFull)
			elif os.path.isdir(sFull) and self.ValidDir(sName):
				dData[sName] = {}
				self.LoadConfigByPath(dData[sName], sFull)


	def LoadConfigByPak(self):
		"""
		加载指定的数据包文件
		"""
		self.m_Data = {}
		#等待添加




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
		@sKey，string，多重目录可以用.分割
		示例：Query("task.global") 查询task/global.json的内容
		"""
		sKeyList = sKey.split(".")
		dData = self.m_Data
		for k in sKeyList:
			dData = dData.get(k, None)
			if not dData:
				break
		return dData


