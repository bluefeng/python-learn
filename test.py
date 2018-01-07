import requests
import re
import os
import sys
from bs4 import BeautifulSoup
url = input("please input url: ")
#url = "http://elearning.chinaacc.com/xcware/video/videoList/videoList.shtm?cwareID=18804&ranNum=0.31865859827346554"
cookies = {}
f=open('cookies.txt','r')#打开所保存的cookies内容文件  
for line in  f.read().split(';'):   #按照字符：进行划分读取  
    #其设置为1就会把字符串拆分成2份  
    name,value=line.strip().split('=',1)  
    cookies[name]=value  #为字典cookies添加内容
html = requests.get(url, cookies = cookies).text

soup = BeautifulSoup(html, "html.parser")
# print(soup.prettify())
result = soup.find_all('a' , re.compile('clearfix pr '))
allMap = {}
for one in result:
	# page = int(one["data-list"].split("#", 1)[0])
	allMap[one["id"]] = one["id"] + " " + one.find_all('span')[0]['title'].replace('\u3000',' ').replace('\t','')
print(allMap)

def rename(path, name):
    fir, sec = name.strip().split('.',1)
    if fir in allMap.keys():
        os.rename(path + name, path + allMap[fir] + '.' + sec)


path = "./"
for f in os.listdir(path):
    if os.path.isdir(path + f):
    	for of in os.listdir(path + f):
            rename(path + f + "/", of)
    else:
        rename(path, f)
input("success")