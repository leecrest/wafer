#coding=utf-8
"""
@author : leecrest
@time   : 14-6-16 下午11:22
@brief  : 
"""

import json
import os
import marshal

a = {
	"1":{"11":{"111":111}}
}

b = ["1", "11", "111"]

d = a
for k in b:
	d = d.get(k, {})
	if not d:
		break
print d
print a
