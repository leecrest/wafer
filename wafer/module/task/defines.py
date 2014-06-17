# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/11 19:18
@brief  : 任务系统定义
"""

#任务状态
TASK_STATUS_TODO	= 1 #可接取
TASK_STATUS_ACCEPT	= 2 #已接取，但是条件不满足，未激活
TASK_STATUS_DOING	= 3 #进行中
TASK_STATUS_FINISH	= 4 #完成


#任务系
TASK_SERIES_NORMAL	= 1 #普通任务
TASK_SERIES_STORY	= 2 #剧情任务
TASK_SERIES_RING	= 3 #环任务


#任务类型
TASK_TYPE_MAIN		= 1 #主线
TASK_TYPE_SUB		= 2 #支线
TASK_TYPE_DAY		= 3 #日常


