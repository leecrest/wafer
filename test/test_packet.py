# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/28 0:06
@brief  : 测试网络协议打包与解包
"""


import wafer

wafer.InitNetProto("proto_conf.json", "proto_type.json")

data = {
	"Name" : "user_name",
    "Pass" : "user_pass",
	"role" : [
		{
			"ID" : 1001,
			"Name" : "role_1001",
			"item" : [
			    {"ID":2001, "Name":"item_2001", "param":[3001,3002]},
		        {"ID":2002, "Name":"item_2002", "param":[3101,3102]},
		    ]
		},
	    {
			"ID" : 1002,
			"Name" : "role_1002",
			"item" : [
			    {"ID":2101, "Name":"item_2101", "param":[3201,]},
		    ]
		}
	]
}

sBuff = wafer.PackNet(1, "c2s_login", data)
sNew = wafer.UnpackNet(1, sBuff)
print sNew
print data
print data == sNew[2]

