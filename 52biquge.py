

import requests
from bs4 import BeautifulSoup
import re

headers={
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
}

import argparse

helpwords='Download novel from https://www.52biquge.com, you can reading README for the details of usage'

parser = argparse.ArgumentParser(description=helpwords)
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
    print('Start analys chapter link: %s' % catalog_url)
    current_url = catalog_url
    do_next_page = True
    chapter_num_start = 0
    chapter_num_end = 0
    while(do_next_page):
        chapter_num_start = chapter_num_end
        req = requests.get(url=current_url, headers=headers)
        if req.status_code== 200 :
            soup = BeautifulSoup(req.text, 'lxml')
            #print(type(soup))
            nameSet = soup.select('body > div.container > div.row.row-detail > div > div > div.info > div.top > h1')
            name = nameSet[0].text
            liList = soup.select('body > div.container > div.row.row-section > div > div:nth-child(4) > ul > li>a')
            next_page_tag =  soup.select('body > div.container > div.row.row-section > div > div.listpage > span.right> a')
            for li in liList:
                charter_herf = li['href']
                chapter_url = "https://www.52biquge.com"+charter_herf
                chapter_title = li.text
                #print('%s:%s' % (chapter_url,chapter_title))
                aChapter = {'chapter_title':chapter_title, 'chapter_url':chapter_url}
                chapters.append(aChapter)
                chapter_num_end=chapter_num_end+1
            if 'href' in next_page_tag[0].attrs:
                current_url = "https://www.52biquge.com"+next_page_tag[0]['href']
            else:
                do_next_page = False
            print('chapter %4d - %4d analyse done! ' %(chapter_num_start+1, chapter_num_end) )
        else:
            print("page %s error(%d):" %(current_url, req.status_code))
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
            req = requests.get(url=chapters[index]['chapter_url'], headers=headers)
            #req = requests.get(url='https://www.52biquge.com/biquge/8/8480/3600511.html', headers=headers)
            soup = BeautifulSoup(req.text, 'lxml')
            break
        except :
            print("get %dth chapter failure, retrying %d times" % (chapter_index, retry+1))
            time.sleep(int(random.random()*10))
            retry = retry+1
    if retry >= retry_max :
        content = content +'this chapter download failure'
        print("Have tried %d times, get %dth chapter still failure,error:%d" % (retry_max, chapter_index, req.status_code))
        return index, content
    if req.status_code == 200 :
        contants_tag = soup.select('#content')
        for p in contants_tag:
            #print(p.contents)
            for st in p.contents[2:len(p.contents)-2]:
                #fliter <br/>
                if st.string != None and  st.string != '\n' and st.string !='\u3000\u3000':
                    #print(st.string,end='')
                    content=content+st.string+'\n'
    content=content.replace('\u3000', '')
    #print(content)
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
    if args.catalog_url == '' :
        print('please input a url')
        exit(1)
    title=FromCatalogPage(args.catalog_url)
    print("\n  DOWNLOAD %s START     " % title)
    GetChapterContent(title, chapters,args.thread_num)
    #GetAChapterContent(chapters,1)

