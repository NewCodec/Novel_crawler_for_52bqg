#coding:utf-8

from bs4 import BeautifulSoup
import requests
import re
import threading
import urllib.parse
import argparse
import time
import os

parser = argparse.ArgumentParser(description="从笔趣网下载小说")
group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--download", type=str, default='',help="download novel,need give the url")
group.add_argument("-s", "--search", type=str, default='',help="search novel from 52bgg,give keywords")
group.add_argument("-a", "--search_download", type=str, default='',help="from 52bgg,give keywords")
group.add_argument("-th", "--thh", type=int, default=100,choices=[50,100,200,400],help="from 52bgg,give keywords")
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

DOWNLOAD_THREAD_MAX = args.thh

Home='https://www.52bqg.com/book_4468/'
LinkFromHome=[]
contents={}
def GetAllLinkFromHome(home):
    print("开始解析下载链接...")
    try:
        res=requests.get(home,headers=headers)
    except:
        print("网页获取失败："+home)
        return
    res.encoding = 'gbk'
    soup = BeautifulSoup(res.text,"html.parser")
    link_cell_set = soup.find_all('dd')
    link_cell_len = len(link_cell_set)
    try:
        novel_name = soup.select('.box_con #maininfo h1')[0].text
    except:
        print("获取小说标题失败")
    for i in range(link_cell_len):
        try:
            link_cell_name=link_cell_set[i].text
            link_cell_link=home+link_cell_set[i].find_all('a')[0]['href']
            LinkFromHome.append((link_cell_name,link_cell_link))
        except:
            pass
        #print("('%s|%d','%s')" % (link_cell_name,i,link_cell_link))
    print("解析链接完成！")
    return novel_name


def ReadOneSection(section_link):
    response=requests.get(section_link,headers=headers)
    response.encoding = 'gbk'
    #print(response.text)
    soup=BeautifulSoup(response.text,"html.parser")
    section_name=soup.select('#wrapper .content_read #box_con .bookname h1')
    if len(section_name)==0:
        print(section_link)
    else:
        section_name=section_name[0]
    section_text=soup.select('#wrapper .content_read #box_con #content')[0]
    for ss in section_text.select("script"):                #删除无用项
        ss.decompose()

    section_text=re.sub( '\s+', '\r\n\t', section_text.text).strip('\r\n')
    return (str(section_name.text),section_text)

lock = threading.RLock()
def threadGetSections(link_list,download_num):
    name,text=('null','内容下载失败')
    retry=5
    
    for i in range(retry):
        try:
            name,text = ReadOneSection(link_list[download_num][1])
            break
        except:
            print("获取第%d章内容失败:第%d次" % (download_num,i+1))
            time.sleep(2)
    
    lock.acquire()
    contents.update({str(download_num):(name,text)})
    lock.release()
    #print("获取第%d章完成,总共%d章" % (download_num,len(link_list)))

def Dowloading(novel_name,link_list,thread_num_max):
    threads=[]
    section_num = len(link_list)
    download_index = 0
    thread_num = thread_num_max
    if thread_num_max>section_num:
        thread_num=section_num
    #print("section_num=%d" % section_num )
    fp=open(novel_name+'.txt','wb+')
    while download_index<section_num:
        if section_num-download_index < thread_num:
            thread_num = section_num-download_index
        print("正在下载: %d ~ %d\t|%d\t请稍后.." % (download_index+1,download_index+1+ thread_num,section_num))
        for i in range(thread_num):
            thread = threading.Thread(target =threadGetSections,args=(link_list,download_index+i))
            threads.append(thread)
        for i in range(thread_num):
            threads[i].start()
        for i in range(thread_num):
            threads[i].join()
        threads.clear()
        for i in range(download_index,download_index+thread_num,1):
            name,text=contents[str(i)]
            fp.write((name+'\t\n').encode('UTF-8'))
            fp.write(text.encode('UTF-8'))
            fp.write(('\n').encode('UTF-8'))
        contents.clear()
        download_index=thread_num+download_index
    fp.close()
    print("下载完成：尽情享受阅读吧")
    print("小说保存在："+os.path.abspath('.')+'\\'+novel_name+'.txt\n')
    return

search_res_table=[]
history_file_name = 'history_file'
def NovelSearch(searchStr):
    rc = 0
    search_res_table.clear()
    print("开始搜索："+searchStr)
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
                #print("只有一本符合")
                save_his = "num:1"+";"+"name:"+novel_name+";"+"writer:"+novel_writer \
                    +";"+"link:"+novel_link+";"+"\t\n"
                print("1 【 无类别 】\t"+novel_name+'\t'+'作者：'+novel_writer)
                hf=open(history_file_name,'wb+')
                hf.write(save_his.encode('utf-8'))
                hf.close()
                search_res_table.append(("无类别",novel_name,novel_link,novel_writer))
                rc = 1
            else:
                print("href error")
        else:
            print("no result")
        return rc
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
    rc = len(search_res_table)
    hf=open(history_file_name,'wb+')
    if rc >20 :
        print("搜索结果共有%d，只显示一部分，跟多结果，请查阅文件" % rc)
    for i in range(len(search_res_table)):
        novel_class,novel_name,novel_link,novel_writer=search_res_table[i]
        save_his = "num:"+str(i+1)+";"+"name:"+novel_name+";"+"writer:"+novel_writer \
                    +";"+"link:"+novel_link+";"+"\t\n"
        hf.write(save_his.encode('utf-8'))
    hf.close()
    print("搜索完成，您可以在搜索结果保存在："+history_file_name)
    return rc

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

#(novel_class,novel_name,novel_link,novel_writer)
# return -1 means no result
# return other numbers means the one have been choosed
def showSearchRes(search_res_table):
    rc = -1
    res_table_len=len(search_res_table)
    show_en = True
    show_once_num = 20
    showing_num = 0
    unshowed_num = res_table_len
    if res_table_len != 0:
            
        print("----------------------")
        print("功能显示：")
        print("1，下一搜索页")
        print("2，选择一个小说")
        print("3，结束搜索：")
        print("----------------------")
        while show_en:
            if unshowed_num < show_once_num:
                show_once_num = unshowed_num
            for i in range(show_once_num):
                print(str(showing_num)+search_res_table[showing_num][0]+'\t'+ \
                        search_res_table[showing_num][1]+'\t'+search_res_table[showing_num][3]+ \
                        '  \t'+search_res_table[showing_num][2])
                showing_num+=1
            unshowed_num=unshowed_num-show_once_num
            if res_table_len == 1:
                rc = 0
                return rc
            choice=input("接下来您要：")
            if not choice.isdigit():
                print("您输入的功能不是数字，退出")
                exit(1)
            choice=int(choice)
            if choice == 1 :
                pass
            elif choice == 2:
                c_num = input("您选择哪个小说(选前面的序号)：")
                if not c_num.isdigit():
                    print("您输入的序号不是数字，退出")
                    exit(1)
                c_num=int(c_num)
                return c_num
            elif choice==3 :
                show_en=False
                print("结束")
                exit(1)
            else:
                print("不支持的功能，结束")
                show_en=False
                return rc
            if unshowed_num <=0:
                print("全部显示完")
                unshowed_num=0
    else:
        print("网站没有符合关键词的小说，请您缩小关键词再试")
    return rc

if args.search != '' :
    print("您选择了搜索:"+args.search)
    search_key=str(args.search)
    Novel_num = NovelSearch(search_key)
    num_c=showSearchRes(search_res_table)
    if -1 == num_c:
        exit(1)
    if Novel_num == 1:
        print('\n只有一本：'+search_res_table[num_c][1]+'\t下载链接'+search_res_table[num_c][2])
    else:
        print('你选择了'+search_res_table[num_c][1]+'\t下载链接'+search_res_table[num_c][2])
    print("您可以通过-d + 链接 的方式直接下载小说")
elif args.search_download != '' :
    print("您选择了搜索[%s]和下载" % args.search_download)
    NovelSearch(args.search_download)
    num_c=showSearchRes(search_res_table)
    if num_c == -1:
        print("获取小说主页失败")
        exit(1)
    Dowloading(GetAllLinkFromHome(Home),LinkFromHome,DOWNLOAD_THREAD_MAX)
elif args.download != '' :
    print("您选择了下载:"+args.download)
    if len(args.download)<27 or args.download[0:27] != r"https://www.52bqg.com/book_":
        print("您输入了错误的网址，退出")
        exit(1)
    Dowloading(GetAllLinkFromHome(args.download),LinkFromHome,DOWNLOAD_THREAD_MAX)
else:
    print("您什么也没有选择，退出")
    exit(1)

#GetAllLinkFromHome(Home)
#Dowloading(GetAllLinkFromHome(Home),LinkFromHome,200)