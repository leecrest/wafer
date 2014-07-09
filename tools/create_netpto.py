# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/27 18:34
@brief  : 协议生成
"""

import sys
import os
import json

PTO_EXT = ".pto"    #协议文件的扩展名
TYPE_EXT = ".type"  #类型文件的扩展名


def ScanPath(root, sExtName):
	if not os.path.exists(root) or not os.path.isdir(root):
		return
	data = {}
	for item in os.listdir(root):
		sFull = os.path.join(root, item)
		if os.path.isdir(sFull):
			dSub = ScanPath(sFull, sExtName)
			if dSub:
				data.update(dSub)
		elif os.path.isfile(sFull):
			sName, sExt = os.path.splitext(item)
			sExt = sExt.lower()
			if sExt != sExtName:
				continue
			f = open(sFull, "r")
			sData = f.read()
			f.close()
			data[sName] = eval(sData)
			print "load", sFull, "... ok"
	return data


def CreatePto(root, sOut, iMin, iMax):
	data = ScanPath(root, PTO_EXT)
	if not data:
		return
	if iMax > iMin and len(data) > iMax - iMin:
		print u"协议文件数量已经超出了定制的协议长度"
		return
	iIndex = iMin
	dName2ID = {}
	dPtoDict = {}
	for sName, pto in data.iteritems():
		dName2ID[sName] = iIndex
		dPtoDict[iIndex] = {"name":sName, "args":data[sName]}
		iIndex += 1
	if not dName2ID:
		return
	json.dump({"Name2ID":dName2ID, "PtoCfg":dPtoDict}, open(sOut, "w"))


def CreateType(root, sOut):
	data = ScanPath(root, TYPE_EXT)
	if not data:
		return
	json.dump(data, open(sOut, "w"))


if __name__ == "__main__":
	sRoot = sys.argv[1]
	iMin = int(sys.argv[2], 16)
	iMax = int(sys.argv[3], 16)
	os.chdir(sRoot)
	os.popen("rd /s /q protocol/proto_conf.json")
	os.popen("rd /s /q protocol/proto_type.json")
	CreatePto("protocol/", "protocol/proto_conf.json", iMin, iMax)
	CreateType("protocol/", "protocol/proto_type.json")