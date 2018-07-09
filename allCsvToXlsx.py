from openpyxl import Workbook
import sys
import os

def to_number(s):
	try:
		return int(s)
	except ValueError:
		try:
			return float(s)
		except ValueError:
			pass
	s = s.encode("utf-8")
	return s

def changeOne(path, toPath):
	wb = Workbook()
	sheet = wb.active
	cur = 1
	with open(path, 'rb') as file:
		for line in file.readlines():
			try :
				line = line.decode('utf8')
			except :
				line = line.decode("gbk")
			line = line.strip('\n')
			temp = line.split(',')
			for j in range(len(temp)):
				sheet.cell(row = cur, column = j + 1, value = to_number(temp[j]))
			cur += 1

	wb.save(toPath + ".xlsx")

def getCsvPaths(csvF):
	fl = os.listdir(csvF)
	allpath = []
	for tempP in fl :
		cpath = os.path.join(csvF, tempP)
		if os.path.isdir(cpath) :
			allpath += getCsvPaths(cpath)
		else:
			ftype = os.path.splitext(cpath)[1]
			if ftype == '.csv' or ftype == '.info' :
				allpath.append(cpath)
	return allpath

try :
	fpath = sys.argv[1]
except:
	fpath = "./"
try :
	tPath = sys.argv[2]
except:
	tPath = "./outxlsx/"


allCsv = getCsvPaths(fpath)

for oneCsvPath in allCsv :
	print(oneCsvPath)
	toPath = os.path.splitext(oneCsvPath.replace(fpath, tPath, 1))[0]
	onlyF = os.path.split(toPath)[0]
	if not os.path.exists(onlyF) :
		os.makedirs(onlyF)
	changeOne(oneCsvPath, toPath)
print("success")