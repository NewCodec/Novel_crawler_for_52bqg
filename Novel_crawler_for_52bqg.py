#coding:utf-8

import requests
from bs4 import BeautifulSoup
import os
import re
import time
import urllib.parse
import argparse

parser = argparse.ArgumentParser(description="从笔趣网下载小说")
group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--download", action="store_true",help="download novel,need give the url")
group.add_argument("-s", "--search", action="store_true",help="search novel from 52bgg")
group.add_argument("-a", "--search_download", action="store_true")
parser.add_argument("-u", "--url", type = str , default='',help="the url you want to download")
args = parser.parse_args()
headers={
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cookie": "jieqiVisitId=article_articleviews%3D126948; Hm_lvt_cec763d47d2d30d431932e526b7f1218=1585894807; Hm_lpvt_cec763d47d2d30d431932e526b7f1218=1585894807; __gads=ID=22f0cfc6317b1562:T=1585894807:S=ALNI_Mb9AmlzE8sE2AP38xxYmmSCw-sobQ",
"Host": "www.52bqg.com",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
}

#first_page_url= 'https://www.52bqg.com/book_113099/'
#txt_section = '48628280.html'
def FindFirstSectionAndSectionNum(first_page):
    response=requests.get(first_page,headers=headers)
    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text,"html.parser")
    first_section_s =soup.select('#list dl dd a')[0]
    first_section=first_page+first_section_s["href"]
    Num_s = soup.select('#list dl dd')
    novel_name = soup.select('.box_con #maininfo h1')[0].text
    return (novel_name,first_section,len(Num_s))

def ReadOneSection(txt_section):
    response=requests.get(txt_section,headers=headers)
    response.encoding = 'gbk'
    #print(response.text)
    soup=BeautifulSoup(response.text,"html.parser")
    section_name=soup.select('#wrapper .content_read #box_con .bookname h1')
    if len(section_name)==0:
        print("s_link")
    else:
        section_name=section_name[0]
    section_text=soup.select('#wrapper .content_read #box_con #content')[0]
    next_section=soup.select('#wrapper .content_read #box_con .bottem a' )[3]
    for ss in section_text.select("script"):                #删除无用项
        ss.decompose()

    section_text=re.sub( '\s+', '\r\n\t', section_text.text).strip('\r\n')
    return (str(section_name.text),section_text,next_section["href"])

def DownLoadNovel(first_page_url):
    novel_name,first_section_url,section_num=FindFirstSectionAndSectionNum(first_page_url)
    print("开始下载小说《"+novel_name+"》...")
    print("小说链接为："+first_page_url)

    fp = open(novel_name+'.txt',"ab+")

    download_section=first_section_url
    last_section_url=''
    while last_section_url != first_page_url:
        name,text,download_section = ReadOneSection(download_section)
        last_section_url = download_section
        fp.write(('\r' + str(name) + '\r\n').encode('UTF-8'))
        fp.write((text).encode('UTF-8'))
        print(name+"\t下载完成")
    fp.close()
    print("小说下载完成，请享受阅读")

searchStr="绝世"
search_res_table=[]
history_file_name = 'history_file'
def NovelSearch(searchStr):
    searchStr = searchStr.encode('gb2312')
    searchStr_url = urllib.parse.quote(searchStr)
    #print(searchStr_url)
    search_url = 'https://www.52bqg.com/modules/article/search.php?searchkey='+searchStr_url
    
    response = requests.get(search_url,headers=headers)
    response.encoding = 'gbk'
    soup=BeautifulSoup(response.text,"html.parser")
    Search_res_active = soup.select('.main #centerl #content #main .novelslistss li')
    Search_res_active_len = len(Search_res_active)
    Search_res_page=soup.find_all('a', attrs={"class":"last"})
    
    if Search_res_active_len==0 or 0==len(Search_res_page):
        Search_res_one = soup.select('head link')

        if len(Search_res_one)!=0 :
            one = Search_res_one[0]['href']
            if len(one)>27 or one[0:26] == "https://www.52bqg.com/book_":
                novel_name= soup.select('body .box_con #maininfo #info h1')[0].text
                novel_writer=soup.select('body .box_con #maininfo #info p a')[0].text
                novel_link = one
                print("只有一本符合")
                save_his = "num:1"+";"+"name:"+novel_name+";"+"writer:"+novel_writer \
                    +";"+"link:"+novel_link+";"+"\t\n"
                print("1 【 无类别 】\t"+novel_name+'\t'+'作者：'+novel_writer)
                hf=open(history_file_name,'wb+')
                hf.write(save_his.encode('utf-8'))
                hf.close()
            else:
                print("href error")
        else:
            print("no result")
        return
    Search_res_page_num=int(Search_res_page[0].text)
    for pages in range(Search_res_page_num):
        if 0==pages :
            response_pages = response
            soup_pages = soup
            Search_res_active_pages=Search_res_active
            Search_res_active_len_pages=Search_res_active_len
        else:
            response_pages = requests.get(search_url+"&page="+str(pages+1),headers=headers)
            response_pages.encoding = 'gbk'
            soup_pages=BeautifulSoup(response.text,"html.parser")
            Search_res_active_pages = soup.select('.main #centerl #content #main .novelslistss li')
            Search_res_active_len_pages = len(Search_res_active)

        for i in range(Search_res_active_len_pages):
            Span_i=Search_res_active_pages[i].find_all('span')
            novel_class = Span_i[0].text
            novel_name = Span_i[1].a.text
            novel_link = Span_i[1].a['href']
            novel_writer=Span_i[3].text
            search_res_table.append((novel_class,novel_name,novel_link,novel_writer))
    hf=open(history_file_name,'wb+')
    if len(search_res_table) >20 :
        print("搜索结果太多，只显示一部分，跟多结果，请查阅文件")
    for i in range(len(search_res_table)):
        novel_class,novel_name,novel_link,novel_writer=search_res_table[i]
        save_his = "num:"+str(i+1)+";"+"name:"+novel_name+";"+"writer:"+novel_writer \
                    +";"+"link:"+novel_link+";"+"\t\n"
        hf.write(save_his.encode('utf-8'))
        if i<20 :
            show_mesg = str(i+1)+"【"+ novel_class+"】"+"\t"+ novel_name+"\t" +novel_writer
            print(show_mesg)
    hf.close()

def ReadLinkFromHistory(history_file_name,his_num):
    if not os.path.isfile(history_file_name):
        print("没有搜索记录")
        exit(1)
    with open(history_file_name,"r",encoding='UTF-8') as hf:
        reg=re.compile("num:(?P<num>[^\s]+);name:(?P<name>[^\s]+);writer:(?P<writer>[^\s]+);link:(?P<link>[^\s]+);")
        for line in hf.readlines():
            line_re=reg.match(line)
            line_dic=line_re.groupdict()
            if int(his_num)==int(line_dic['num']):
                print("选择下载《"+line_dic['name']+">,作者："+ line_dic['name'])
                return line_dic['link']
        print("无此小说")
        return ''
    

if args.search :
    print("您选择了搜索")
    search_key=input("请您输出搜索关键词(宁可少，不可错)：")
    NovelSearch(search_key)
    print("搜索完成，您可以在搜索结果保存在："+history_file_name)
elif args.search_download:
    print("您选择了搜索和下载")
    search_key=input("请您输出搜索关键词(宁可少，不可错)：")
    NovelSearch(search_key)
    download_num=input("搜索完成，请您选择你要下载的序号:")
    if not download_num.isdigit():
        print("您输入的序号不是数字，退出")
        exit(1)
    s_link=ReadLinkFromHistory(history_file_name,download_num)
    DownLoadNovel(s_link)

elif args.download:
    print("您选择了下载")
    if args.url=='':
        print("您没有输入下载地址")
        d_link=input("请您输入小说首页地址：")
    else:
        d_link=args.url
    print(d_link)
    if len(d_link)<27 or d_link[0:27] != r"https://www.52bqg.com/book_":
        print("您输入了错误的网址，退出")
        exit(1)
    DownLoadNovel(d_link)
else:
    print("您什么也没有选择，退出")
    exit(1)