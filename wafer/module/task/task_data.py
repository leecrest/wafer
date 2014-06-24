#coding=utf-8
"""
@author : leecrest
@time   : 14-6-16 上午7:58
@brief  : 任务配置文件示例
"""

#自动生成开始
TASK_DATA = {
	1001 : {
		"Name"      : "测试任务",
	    "Main"      : 100,
	    "Pre"       : 0,
	    "Next"      : 1002,
	    "AcceptNPC" : 9001,
	    "SubmitNPC" : 9002,
	    "Type"      : 1,
	    "Level"     : 1,
	    "Brief"     : "和9002对话",
	    "Detail"    : "从9001接取任务，和9002对话完成任务",
	    "Track"     : "和9002对话",
	    "FixedParam": {"自动领取":True,},
	    "Condition" : (("等级",">",1),("职业","=","战士")),
	    "TimeLimit" : 0,
	    "Chat"      : {
		    "领取" : "我是领取对白",
	        "提交" : "我是提交对白",
	    },
	    "Active"    : (("摆怪",201,100,200,9002),),
	    "Target"    : (),
	    "Reward"    : (("奖励任务经验",100),)
	},
}
#自动生成结束


def GetTaskConfig(iTaskID):
	return TASK_DATA[iTaskID]
