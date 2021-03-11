

from urllib import request
import re

headers={
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
}

import argparse
parser = argparse.ArgumentParser(description="从斗破小说网下载小说")
group = parser.add_mutually_exclusive_group()
group.add_argument("-url", "--catalog_url", type=str, default='',help="download novel,need give the url")
#group.add_argument("-s", "--search", type=str, default='',help="search novel from 52bgg,give keywords")
#group.add_argument("-a", "--search_download", type=str, default='',help="from 52bgg,give keywords")
parser.add_argument("-t", "--thread_num", type=int, default=50,choices=[50,100,200,400],help="thread number")
args = parser.parse_args()


chapters = []
allContents={}
def  FromCatalogPage(catalog_url):
    '''
    input : catalog url
    return: name, writer, last update section, introduction, links
    '''
    req = request.Request(url=catalog_url, headers=headers, method='GET')
    response = request.urlopen(req)
    if response.status == 200 :
        html = response.read().decode('utf-8')
        liList = re.findall('<li>.*</li>',  html)
        nameR = re.search('<h1>([^<>=]*?)</h1>', html)
        for li in liList:
            g = re.search('href="([^>"]*)"[\s]*title="([^>"]*)"', li)
            if g != None:
                chapter_url = "http://www.doupoxs.com"+g.group(1)
                chapter_title = g.group(2)
                aChapter = {'chapter_title':chapter_title, 'chapter_url':chapter_url}
                chapters.append(aChapter)
    else:
        print("catalog url request error")
    if nameR.group(1)!=None:
        name = nameR.group(1)
    else:
        name = "unknown"
    return name

import random
import threading
import time
lock = threading.RLock()
def GetAChapterContent(chapters, chapter_index):
    index = chapter_index
    content = ''
    retry_max = 5
    retry = 0
    while retry < retry_max :   
        try:
            req = request.Request(url=chapters[index]['chapter_url'], headers=headers, method='GET')
            response = request.urlopen(req)
            break
        except :
            print("get %dth chapter failure, retrying %d times" % (chapter_index, retry+1))
            time.sleep(int(random.random()*10))
            retry = retry+1
    if retry >= retry_max :
        content = content +'this chapter download failure'
        return index, content
    if response.status == 200 :
        html = response.read().decode('utf-8')
        plist = re.findall('<p>([^<>]*?)</p>',  html)
        for p in plist:
            content = content +'\n'+p
    lock.acquire()
    allContents.update({str(index):content})
    lock.release()
    return None


def GetChapterContent(title, chapters, thread_num_max):
    chapters_num = len(chapters)
    thread_num = thread_num_max
    chapters_leave_num = chapters_num
    chapters_done_index = 0
    threads=[]
    novel_name=title
    fp=open('download/'+novel_name+'.txt','wb+')
    while chapters_done_index < chapters_num:
        if chapters_num - chapters_done_index <  thread_num_max:
            thread_num = chapters_num - chapters_done_index
        print("Downloading chapter from %4d to %d " % (chapters_done_index+1,chapters_done_index+thread_num))
        for i in range(thread_num):
            thread = threading.Thread(target=GetAChapterContent, args=(chapters, chapters_done_index+i))
            threads.append(thread)
        for i in range(thread_num):
            threads[i].start()
        for i in range(thread_num):
            threads[i].join()
        threads.clear() 
        for i in range(chapters_done_index,chapters_done_index+thread_num,1):
            name=chapters[i]['chapter_title']
            text=allContents[str(i)]
            fp.write((name+'\n').encode('UTF-8'))
            fp.write((text+'\n\n').encode('UTF-8'))
        allContents.clear()
        chapters_done_index=chapters_done_index+thread_num
    fp.close()
    print("Download finished, Just enjoy it")
    return None


if __name__ == '__main__':
    title=FromCatalogPage(args.catalog_url)
    print("\n  DOWNLOAD %s START     " % title)
    GetChapterContent(title, chapters,20)
