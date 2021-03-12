'''
这是一个从网上直接copy的脚本，执行需要lxml模块。
https://blog.csdn.net/qq_49077418/article/details/108268482

但是它有几个问题
1. 单线程，getContent有sleep下载很慢，
2.一旦某章出错，下载就停止了。
'''
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import time
from pip._vendor.retrying import retry


def getBook(book):
    murl = 'http://www.xbiquge.la/modules/article/waps.php'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    data={'searchkey':book}
    response=requests.post(url=murl,data=data,headers=headers)
    response.encoding = "utf-8"
    code=response.text
    soup=BeautifulSoup(code,'lxml')
    tab=soup.select('.even')
    all=re.findall(r'<td class="even">(.*?)</td>',str(tab))
    if len(all)==0:
        return None
    name=re.findall(r'target="_blank">(.*?)</a>',str(all))
    author=[]
    url=re.findall(r'href="(.*?)"',str(all))
    for i,n in enumerate(all):
        if i%2!=0:
            author.append(n)
    for i in range(len(name)):
        if i == 0:
            print('序号\t书名\t作者\t网址')
        print('['+str(i)+']\t'+name[i]+'\t'+author[i]+'\t'+url[i])
    burl=input("请输入你想获得txt的书的序号：")
    return url[int(burl)]


def getChap(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    response = requests.get(url=url,headers=headers)
    response.encoding = "utf-8"
    code = response.text
    tree=etree.HTML(code)
    nurl = tree.xpath('//div[@id="list"]/dl/dd/a/@href')
    name=str(tree.xpath('//div[@id="info"]/h1/text()')).split("'")[1]
    print(name+"共发现"+str(len(nurl))+"章，即将开始爬取")
    for i in range(len(nurl)):
        turl='http://www.xbiquge.la'+nurl[i]
        getContent(turl,name)
        print("爬取完成，剩余" + str(len(nurl)-i-1)+'章')
@retry
def getContent(url,name):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    response = requests.get(url=url, headers=headers)
    response.encoding='utf-8'
    time.sleep(1)
    code = response.text
    tree = etree.HTML(code)
    chap = tree.xpath('//div[@class="bookname"]/h1/text()')[0]
    content = tree.xpath('//div[@id="content"]/text()')
    with open('./download'+name + '.txt', 'a+', encoding='utf-8') as file:
        print("开始爬取:" + chap)
        file.write(chap + '\n\n')
        for i in content:
            text = str(i)
            text.strip()
            file.write(text)
        file.write("\n\n")
        file.close()

book=input("请输入你要获取的书名或作者(请您少字也别输错字)：")
url=getBook(book)
if url==None:
    print("未找到相关书籍")
else:
    getChap(url)
    print("爬取完毕")
