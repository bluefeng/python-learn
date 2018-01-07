# coding:utf-8
import re
import json
import sys
import os
import time
from urllib import parse
from urllib import request
import traceback
import shutil

def isWantAgain(string):
    choose = input(string + "    again？[Y/N]:")
    if choose == 'N' :
        #sys.exit()
        return True
    else:
        return True

if __name__ == '__main__':
    print('''
        ---------------------------------
           Welcome to Monkey Downloader
        ---------------------------------
        ''')

    while True :
        try:
            m3u8Url = input("please input m3u8 url: ")

            reg = r'(http://.+?)/'
            pattern = re.compile(reg)
            group = re.search(pattern, m3u8Url)
            if group :
                urltitle = group.group(1)
            else:
                print('error input!')
                continue

            reg = r'&videoID=(.+?)&'
            pattern = re.compile(reg)
            group = re.search(pattern, m3u8Url)
            if group :
                viName = group.group(1)
            else:
                print('error input!')
                continue

            path = './temp' + viName + '/'
            if not os.path.exists(path):
                os.makedirs(path)

            for f in os.listdir('./temp' + viName):
                if os.path.isdir(path + f):
                    shutil.rmtree(path + f)
                else:
                    os.remove(path + f)
            if os.path.exists("D:/tools/openResty/html/video/video" + viName + ".key"):
                os.remove("D:/tools/openResty/html/video/video" + viName + ".key")
            try:
                request.urlretrieve(m3u8Url, path + 'index.m3u8')
            except:
                if isWantAgain('error input'):
                    continue
            downList = []
            keyUrl = False
            with open(path + 'index.m3u8','r+') as mf:
                lins = mf.readlines()
                for i in range(len(lins)):
                    if lins[i] == "" :
                        break
                    if not keyUrl :
                        reg = r'#EXT-X-KEY:METHOD=AES-128,URI="(.+?)"'
                        pattern = re.compile(reg)
                        keyUrlG = re.search(pattern, lins[i])
                        if keyUrlG :
                            keyUrl = keyUrlG.group(1)
                            lins[i] = '#EXT-X-KEY:METHOD=AES-128,URI="http://127.0.0.1/luatest?path=D:/tools/openResty/html/video/video' + viName +'.key"\n'

                    reg2 = r'#EXT'
                    pattern = re.compile(reg2)
                    if not re.search(pattern, lins[i]):
                        downUrl = urltitle + lins[i].strip()
                        downList.append(downUrl)
                        lins[i] = "%03d.ts" % len(downList) + '\n'
                mf.seek(0, 0)
                mf.truncate()
                mf.writelines(lins)
                    
            if keyUrl :
                try:
                    key = request.urlopen(keyUrl).read()
                    with open("D:/tools/openResty/html/video/video" + viName + ".key",'wb') as file:
                        file.write(key)
                except:
                    if isWantAgain('keyUrl timeout'):
                        continue
            else:
                if isWantAgain('keyUrl not fount'):
                    continue
            lost = False
            for i in range(len(downList)):
                name = "%03d.ts" % (i + 1)
                try:
                    request.urlretrieve(downList[i], path + name)
                    print('download   ' + name  + '  success!')
                except KeyboardInterrupt:  # CTRL+C 退出程序
                    raise
                except:
                    lost = True
                    print('The %s is lost.' % name)
            os.system('ffmpeg -protocol_whitelist crypto,file,tcp,http -i temp' + viName + '/index.m3u8 -c copy ' + viName + '.mp4')
            if os.path.exists('./temp' + viName):
                shutil.rmtree('./temp' + viName)
            if os.path.exists("D:/tools/openResty/html/video/video" + viName + ".key"):
                os.remove("D:/tools/openResty/html/video/video" + viName + ".key")
            if lost :
                print("failed had lost   " + viName +", next?")
            else:
                print("success   " + viName +", next?")
            continue
            sys.exit()
        except KeyboardInterrupt:  # CTRL+C 退出程序
            print("你已经使用CTRL+C结束了程序。")
            sys.exit()
        except:
            traceback.print_exc()
            sys.exit()





