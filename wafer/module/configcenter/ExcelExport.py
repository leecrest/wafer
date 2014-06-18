# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/18 8:09
@brief  : 从Excel文件中导出数值表，以json格式存储到.dat文件中
"""

import os
import json
import xlrd



def Export(sConfigFile):
	f = open(sConfigFile, "r")
	dConfig = json.load(f)
	f.close()

	sRoot = dConfig.get("root", "./")
	print "Export path", sRoot
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
		for sSheet, dCfg in dSheet.iteritems():
			print "\texport", sSheet
			iLeft   = dCfg.get("left", 0)
			iRight  = dCfg.get("right", 0)
			iTop    = dCfg.get("top", 0)
			iBottom = dCfg.get("bottom", 0)
			if (iLeft < 0 or iRight < 0 or iTop < 0 or iBottom < 0 or
				iLeft > iRight or iBottom > iTop):
				print "Config(%s %s) error" % (sFile, sSheet)
				continue
			oSheet = oFile.sheet_by_name(sSheet)
			if not oSheet:
				continue
			ExportSheet(oSheet, iLeft, iRight, iTop, iBottom)




def OpenExcel(sFile):
	try:
		data = xlrd.open_workbook(sFile)
		return data
	except Exception, e:
		print str(e)


def ExportSheet(oSheet, iLeft, iRight, iTop, iBottom):
	print oSheet.row_values(1)
	print oSheet.col_values(1)




if __name__ == "__main__":
	Export("export.json")

