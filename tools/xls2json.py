# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/18 8:09
@brief  : 从Excel文件中导出数值表，保存成json文件

Excel文件格式如下：
1、第一列是索引列，一般指ID
2、第一行是表头，从英文表头起算

"""

import os
import json
import xlrd

EXPORT_EXT = ".json"


def Export(sConfigFile):
	f = open(sConfigFile, "r")
	dConfig = json.load(f)
	f.close()

	sRoot = dConfig.get("root", "./")
	sOut = dConfig.get("out", "./")

	print "Export path:", sRoot
	dFile = dConfig["file"]
	for sFile, dSheet in dFile.iteritems():
		sFull = os.path.join(sRoot, sFile)
		print "Begin export ..", sFull
		if not os.path.exists(sFull) or not os.path.isfile(sFull):
			print "file %s is err" % sFull
			continue
		oFile = OpenExcel(sFull)
		if not oFile:
			continue
		if not os.path.exists(sOut):
			os.makedirs(sOut)
		for sSheet, dCfg in dSheet.iteritems():
			print "\t export [%s]" % sSheet,
			iLeft   = dCfg.get("left", 0)
			iRight  = dCfg.get("right", 0)
			iTop    = dCfg.get("top", 0)
			iBottom = dCfg.get("bottom", 0)
			if (iLeft < 0 or iRight < 0 or iTop < 0 or iBottom < 0 or
				    (iRight > 0 and iLeft > iRight) or
				    (iBottom > 0 and iTop > iBottom)):
				print "Config(%s %s) error" % (sFile, sSheet)
				continue
			oSheet = oFile.sheet_by_name(sSheet)
			if not oSheet:
				continue
			sOutSheet = os.path.join(sOut, dCfg.get("name",sSheet)+EXPORT_EXT)
			if ExportSheet(sOutSheet, oSheet, iLeft, iRight, iTop, iBottom):
				print " ... ok"
			else:
				print " ... fail"
				return




def OpenExcel(sFile):
	try:
		data = xlrd.open_workbook(sFile)
		return data
	except Exception, e:
		print str(e)


def ExportSheet(sOutFile, oSheet, iLeft, iRight, iTop, iBottom):
	if (iLeft >= oSheet.ncols or iRight > oSheet.ncols or
		iTop >= oSheet.nrows or iBottom > oSheet.nrows):
		return False
	if iRight == 0:
		iRight = oSheet.ncols
	if iBottom == 0:
		iBottom = oSheet.nrows
	#表头
	sHeadList = oSheet.row_values(iTop)

	data = {}
	for iRow in xrange(iTop+1, iBottom):
		sIndex = oSheet.cell(iRow, iLeft).value
		try:
			idx = int(sIndex)
		except Exception, e:
			idx = sIndex
		data[idx] = {}
		for iCol in xrange(iLeft+1, iRight):
			sValue = oSheet.cell(iRow, iCol).value
			data[idx][sHeadList[iCol]] = sValue

	json.dump(data, open(sOutFile, "wb"))
	return True






if __name__ == "__main__":
	Export("xls2json.json")

