#coding=utf-8
"""
@author : leecrest
@time   : 14-4-1 下午10:11
@brief  : MySQL
"""

from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor
import wafer.utils.log as log
import MySQLdb


class CDBPool:

	def __init__(self):
		self.m_Pool = None
		self.m_bInited = False

	def __del__(self):
		self.UnInit()


	def Init(self, dConfig):
		"""
		初始化数据连接池
		@param dConfig:数据库配置
		@return:
		"""
		if self.m_bInited:
			raise Exception("DBPool has inited!")

		self.m_Pool = PooledDB(
			MySQLdb,
			5,
			host=dConfig.get("host", "127.0.0.1"),
		    port=dConfig.get("port", 3306),
			user=dConfig.get("user", "root"),
			passwd=dConfig["password"],
			db=dConfig["db"],
			charset=dConfig.get("charset", "latin1"))
		self.m_bInited = True
		log.Info(u"连接数据库成功")
		return True


	def UnInit(self):
		if not self.m_bInited:
			return
		if self.m_Pool:
			self.m_Pool.close()
		self.m_bInited = False


	def GetConnection(self):
		if not self.m_bInited:
			return None
		return self.m_Pool.connection()


	def ExecSQL(self, sql):
		"""
		执行一段数据库修改的sql语句，插入、修改、删除等
		"""
		if (not sql) or (not self.m_bInited):
			return
		conn = self.GetConnection()
		if not conn:
			return
		try:
			cursor = conn.cursor(cursorclass=DictCursor)
			cursor.execute(sql)
			conn.commit()
			log.Debug("ExecSQL:%s"%sql)
		except Exception as ex:
			log.Error("ExecSQL(%s),error:%s" % (sql, ex.args))
		finally:
			cursor.close()
			conn.close()


	def QuerySQL(self, sql):
		"""
		执行一段查询sql语句
		"""
		if (not sql) or (not self.m_bInited):
			return None
		conn = self.GetConnection()
		ret = []
		if not conn:
			return None
		try:
			cursor = conn.cursor(cursorclass=DictCursor)
			cursor.execute(sql)
			ret = cursor.fetchall()
			log.Debug("QuerySQL:%s"%sql)
		except Exception as ex:
			log.Error("QuerySQL(%s),error:%s" % (sql, ex.args))
		finally:
			cursor.close()
			conn.close()
		return ret



__all__ = ["CDBPool"]
