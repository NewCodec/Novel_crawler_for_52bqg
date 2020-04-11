# coding=utf-8


from bs4 import BeautifulSoup
import requests
import re
# 定义一个类，可以下载所有的小说
# 传入的参数：
#1. headers [Host different]
#2. slink[是一个方法，输入【关键词】，输出【输出符合关键词的结果主页地址列表】] 
#3. getLink[方法： 输入【主页面链接】，输出【小说的名字，各个章节的链接列表】]
#4. getSection --方法：输入【页面链接】，输出【章节名字，章节内容】



class palibery(object):
	def __init__(self):
		self.Header={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "zh-CN,zh;q=0.9",
		"Cache-Control": "max-age=0",
		"Cookie": "UM_distinctid=17167f8192d10-03ccd313d809b7-5313f6f-144000-17167f8192ea71; CNZZDATA1278275441=175857863-1586586857-null%7C1586586857; Hm_lvt_3a0ea2f51f8d9b11a51868e48314bf4d=1586587245; Hm_lpvt_3a0ea2f51f8d9b11a51868e48314bf4d=1586587245; CNZZDATA1275936910=26680182-1586585743-null%7C1586585743",
		"Host": "www.paliberg.com",
		"Upgrade-Insecure-Requests":"1",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
		self.nlistlink=[]		
		
	def slink(self, searchStr):
		print("slink Have not be completed")
		return None
	
	def getLink(self, main_page):
		print("开始解析下载链接[%s]..." % main_page)
		try:
			res=requests.get(main_page,headers=self.Header)
		except:
			print("网页获取失败："+main_page)
			exit(1)
		print("小说首页链接获取成功[%s]..." % main_page)
		res.encoding = 'utf-8'
		soup = BeautifulSoup(res.text,"html.parser")
		link_cell_set = soup.find_all('dd')
		#get the numbers of the section
		try:
			last_page_link = link_cell_set[0].find_all('a')[0].get('href')
			last_page_link = 'http://'+self.Header['Host']+last_page_link
			#print(last_page_link)
		except:
			print("获取总章节数失败")
			exit(1)
		cont = 1
		page = main_page+str(cont)+'.html'
		while  page != last_page_link:
			#print(page)
			self.nlistlink.append(page)
			cont +=1
			page = main_page+str(cont)+'.html'
		self.nlistlink.append(page)
		
		try:
			novel_name = soup.select('#wrapper .box_con #maininfo #info h1')[0].text
			novel_desc = soup.select('#wrapper .box_con #maininfo #intro p')[0].text
		except:
			print('获取小说名失败')
			novel_name = 'null'
			novel_desc = 'null'
		print("链接获取结束[%s]..." % main_page)
		return novel_name,self.nlistlink
		
	def getSection(self,page_link):
		page_name = '无'
		page_text = '章节内容获取失败'
		res=requests.get(page_link,headers=self.Header,timeout=10)
		res.encoding = 'utf-8'
    	#print(response.text)
		soup=BeautifulSoup(res.text,"html.parser")
		try:
			page_name=soup.select('#wrapper .content_read .box_con .bookname h1')[0].text
			#print(page_name)
			section_text=soup.select('#wrapper .content_read .box_con #content')[0]
			for ss in section_text.select("script"):                #删除无用项
				ss.decompose()

			section_text=re.sub( '\s+', '\r\n\t', section_text.text).strip('\r\n')
			page_text=section_text
		except:
			print("章节内容获取失败")
		return page_name,page_text
'''
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
		return name,linklist = 
'''			
			
if __name__=='__main__':
	a = palibery()
#	name,listt = a.getLink('http://www.paliberg.com/cbook_1/')
	print(a.getSection('http://www.paliberg.com/cbook_1/2.html'))