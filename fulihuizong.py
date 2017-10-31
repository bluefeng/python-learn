# coding:utf-8
import re
import json
import sys
import os
import threading
import time
from urllib import parse
from urllib import request
import traceback

homeLayer = "http://fuliba.net/category/fulihuizong"


class ThreadTask(threading.Thread):

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        saveOneUrl(self.url)


class MyError(Exception):
    def __init__(self, arg):
        self.arg = arg

def getHtml(url):
    #url = parse.quote(url, safe='/:?=')
    try:
        page = request.urlopen(url)
        html = page.read().decode('utf-8')
        return html
    except KeyboardInterrupt:  # CTRL+C 退出程序
        raise
    except:
        # traceback.print_exc()
        #raise MyError('The URL you requested could not be found')
        print('The URL you requested could not be found')
        return False

def getPageUrl(page):
    if page == 1 :
        return homeLayer
    else:
        return homeLayer + '/page/' + str(page)

def saveOneUrl(url):
    html = getHtml(url)
    if html :
        reg = r'<title>2017福利汇总(.+?) \| 福利吧</title>'
        pattern = re.compile(reg)
        names = re.findall(pattern, html)
        if names :
            name = names[0]
        else:
            name = r'第不知道多少期'
        print('start download' + name)
        name = re.sub(r'[\\/:*?"<>|]', '', name)
        path = './fulidownload/' + name + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        reg = r'<article (.+?)</article>'
        pattern = re.compile(reg, re.S)
        canUseInfos = re.findall(pattern, html)

        if not canUseInfos:
            print(url + ' download failed')
            return
        canUseInfo = canUseInfos[0]
        reg = r'<img src="(https*://.*?\.(jpg|gif|png))"'
        pattern = re.compile(reg)
        imglist = re.findall(pattern, canUseInfo)
        #imglist = list(set(imglist))

        i = 1
        if imglist :
            for imgurls in imglist:
                Name = name + '_' + str(i)
                imgurl = imgurls[0]
                Postfix = imgurls[1]

                target = path + '%s.%s' % (Name,Postfix)
                i += 1
                if os.path.exists(target):
                    continue

                print("Downloading %s \n" % target)
                try:
                    request.urlretrieve(imgurl, target)
                except KeyboardInterrupt:  # CTRL+C 退出程序
                    raise
                except:
                    print('The image is lost.')
        else:
            print(url + ' no image')
            return
    else :
        print(url + ' download failed')

def saveOnePage(page):
    print('check page: %d ......' % page)
    html = getHtml(getPageUrl(page))
    if html :
        reg = r'<a class="thumb" rel="external" href="(https*://.*?)">'
        pattern = re.compile(reg)
        urls = re.findall(pattern, html)
        if urls :
            return urls
        else:
            print('no one url')
    else:
        print('no the page')


def saveAllPage():
    html = getHtml(getPageUrl(1))
    if html :
        reg = r"<a href='https*://fuliba\.net/category/fulihuizong/page/(\d*)' class='extend' title='跳转到最后一页'>"
        pattern = re.compile(reg)
        index = re.findall(pattern, html)
        if index :
            try :
                lastPage = int(index[0])
            except:
                print('can not found lastPage number')
            print('check all page start number %d......' % lastPage)
            urls = []
            for page in range(1, lastPage + 1):
                temp = saveOnePage(page)
                if temp:
                    for url in temp:
                        urls.append(url)
            return urls
        else:
            print('can not found lastPage number')
        
    else:
        print('no one page')

def isWantAgain(string):
    choose = input(string + "again？[Y/N]:")
    if choose == 'N' :
        sys.exit()
    else:
        return False



if __name__ == '__main__':
    print('''
        ---------------------------------
           Welcome to Fuliba Fulihuizong Download!
        ---------------------------------
        ''')

    while True :
        try:
            page = input('Input page(eg. 1, no will all）: ')
            if page != '':
                try : 
                    page = int(page)
                except:
                    if isWantAgain('input error!!!') :
                        continue
            urls = []
            if page == '' :
                urls = saveAllPage()
            else:
                urls = saveOnePage(page)

            print(len(urls))
            nowtime = time.time()
            #单线程  影响大的是网速  没必要 多线程
            # for urlId in range(len(urls)):
            #     saveOneUrl(urls[urlId])
                
            #多线程

            tasks = []
            for urlId in range(len(urls)):
                task = ThreadTask(urls[urlId])
                tasks.append(task)
                #print('-'*16,'\nThis is thread %s\n' % len(tasks),'-'*16)

            for task in tasks:
                task.setDaemon(True)
                task.start()
                #print(time.ctime(),'thread %s start' % task)
            # for task in tasks:
            #     task.join()
            while 1:
                for task in tasks:
                    if task.is_alive():
                        continue
                    else:
                        tasks.remove(task)
                        #print(time.ctime(),'thread %s is finished' % task)
                if len(tasks) == 0:
                    break

            print(time.time() - nowtime)
            sys.exit()
        except KeyboardInterrupt:  # CTRL+C 退出程序
            print("你已经使用CTRL+C结束了程序。")
            sys.exit()
        except MyError as e:
            print(e.arg)
        except:
            #traceback.print_exc()
            sys.exit()





