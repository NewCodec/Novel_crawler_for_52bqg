#coding:utf-8

from bs4 import BeautifulSoup
import requests
import re
import threading
import urllib.parse
import argparse
import time
import os
import paliberg as pbg
import clean_novel as cn
parser = argparse.ArgumentParser(description="从笔趣网下载小说")
group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--download", type=str, default='',help="download novel,need give the url")
group.add_argument("-s", "--search", type=str, default='',help="search novel from 52bgg,give keywords")
group.add_argument("-a", "--search_download", type=str, default='',help="from 52bgg,give keywords")
parser.add_argument("-th", "--thh", type=int, default=50,choices=[50,100,200,400],help="from 52bgg,give keywords")
parser.add_argument("-c", "--clean", action = 'store_true',help="from 52bgg,give keywords")
args = parser.parse_args()

# 定义一个类，可以下载所有的小说：
# 传入的参数：
#1. headers [Host different]
#2. slink[是一个方法，输入【关键词】，输出【输出符合关键词的结果主页地址列表】] 
#3. getLink[方法： 输入【主页面链接】，输出【小说的名字，各个章节的链接列表】]
#4. getSection --方法：输入【页面链接】，输出【章节名字，章节内容】


class NovelDownload(object):

		def __init__(self, src, arg):
			self.header = src.Header
			self.slink = src.slink
			self.getLink = src.getLink
			self.getSection = src.getSection
			self.lock = threading.RLock()
			self.args =arg
			self.linklist = []
			self.clean = src.clean
			self.name = ''
		
		def SearchNovel(self, searchStr):
			slinklist = self.slink(searchStr)
			for ll in slinklist:
				self.linklist.append(ll)
			return
		
		#get all the section link save as nlinklist	
		def GetLink(self,main_link):
			print("\n  正在解析链接："+main_link)
			name,nlinklist = self.getLink(main_link)
			print('\n---- 下载 %s ----\n' % name)
			self.name = name
			return name,nlinklist
			
		def GetSection(self,page_link,page_num,page_contens_dic):
			name,text = self.getSection(page_link)
			#print(name+'\t'+str(page_num))
			self.lock.acquire()
			page_contens_dic.update({page_num:(name,text)})
			self.lock.release()
			return (page_num,name,text)
		
		def Download(self,main_link,thread_num):
			name,nlinklist=self.GetLink(main_link)	
			nlistlist_len = len(nlinklist)
			page_contens_dic = {}
			threads = []
			downloading_num = thread_num if thread_num<nlistlist_len else nlistlist_len
			downloaded_num = 0
			need_download_num = nlistlist_len
			with open(name+'.txt',"wb") as filebook:
				while need_download_num > 0:
					threads.clear()
					print('正在下载：%d\t~ %d\t|%d 请稍后...' % (downloaded_num,downloaded_num+downloading_num,nlistlist_len))
					for i in range(downloading_num):
						thread = threading.Thread(target = self.GetSection,args=(nlinklist[downloaded_num+i],downloaded_num+i,page_contens_dic))
						threads.append(thread)
					for i in range(downloading_num):
						threads[i].start()
					for i in range(downloading_num):
						threads[i].join()
					for i in range(downloaded_num,downloaded_num+downloading_num,1):
						page_name,page_text = page_contens_dic.get(i)
						filebook.write(page_name.encode('utf-8'))
						filebook.write(page_text.encode('utf-8'))
					need_download_num -= downloading_num
					downloaded_num += downloading_num
					if need_download_num < downloading_num:
						downloading_num = need_download_num
				
				if need_download_num < thread_num:
					downloading_num = need_download_num
				else:
					downloading_num=thread_num
				
		def do_it(self):
			if self.args.download != '':
				self.Download(self.args.download,self.args.thh)
				if self.args.clean:
					cn.NovelClean(self.name+'.txt',self.clean[0],self.clean[1])	
				print("小说下载完成，请尽情享受阅读吧")
			elif self.args.search !='':
				self.SearchNovel(self.args.search)
			elif self.args.search_download != '':
				self.SearchNovel(self.args.search_download)
				a = input("你选中的序号是：")
				self.Download(self.linklist[int(a)],self.args.th)
				
				
				
				
if __name__=='__main__':
	pb = pbg.palibery()	
	dn = NovelDownload(pb, args)
	dn.do_it()