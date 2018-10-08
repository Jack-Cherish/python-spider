# -*- coding:UTF-8 -*-
from urllib import request
from bs4 import BeautifulSoup
import collections
import re
import os
import time
import sys
import types

"""
类说明:下载《笔趣看》网小说: url:https://www.biqukan.com/

Parameters:
	target - 《笔趣看》网指定的小说目录地址(string)

Returns:
	无

Modify:
	2017-05-06
"""
class download(object):
	def __init__(self, target):
		self.__target_url = target
		self.__head = {'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',}

	"""
	函数说明:获取下载链接

	Parameters:
		无

	Returns:
		novel_name + '.txt' - 保存的小说名(string)
		numbers - 章节数(int)
		download_dict - 保存章节名称和下载链接的字典(dict)

	Modify:
		2017-05-06
	"""
	def get_download_url(self):
		charter = re.compile(u'[第弟](.+)章', re.IGNORECASE)
		target_req = request.Request(url = self.__target_url, headers = self.__head)
		target_response = request.urlopen(target_req)
		target_html = target_response.read().decode('gbk','ignore')
		listmain_soup = BeautifulSoup(target_html,'lxml')
		chapters = listmain_soup.find_all('div',class_ = 'listmain')
		download_soup = BeautifulSoup(str(chapters), 'lxml')
		novel_name = str(download_soup.dl.dt).split("》")[0][5:]
		flag_name = "《" + novel_name + "》" + "正文卷"
		numbers = (len(download_soup.dl.contents) - 1) / 2 - 8
		download_dict = collections.OrderedDict()
		begin_flag = False
		numbers = 1
		for child in download_soup.dl.children:
			if child != '\n':
				if child.string == u"%s" % flag_name:
					begin_flag = True
				if begin_flag == True and child.a != None:
					download_url = "https://www.biqukan.com" + child.a.get('href')
					download_name = child.string
					names = str(download_name).split('章')
					name = charter.findall(names[0] + '章')
					if name:
							download_dict['第' + str(numbers) + '章 ' + names[1]] = download_url
							numbers += 1
		return novel_name + '.txt', numbers, download_dict
	
	"""
	函数说明:爬取文章内容

	Parameters:
		url - 下载连接(string)

	Returns:
		soup_text - 章节内容(string)

	Modify:
		2017-05-06
	"""
	def Downloader(self, url):
		download_req = request.Request(url = url, headers = self.__head)
		download_response = request.urlopen(download_req)
		download_html = download_response.read().decode('gbk','ignore')
		soup_texts = BeautifulSoup(download_html, 'lxml')
		texts = soup_texts.find_all(id = 'content', class_ = 'showtxt')
		soup_text = BeautifulSoup(str(texts), 'lxml').div.text.replace('\xa0','')
		return soup_text

	"""
	函数说明:将爬取的文章内容写入文件

	Parameters:
		name - 章节名称(string)
		path - 当前路径下,小说保存名称(string)
		text - 章节内容(string)

	Returns:
		无

	Modify:
		2017-05-06
	"""
	def Writer(self, name, path, text):
		write_flag = True
		with open(path, 'a', encoding='utf-8') as f:
			f.write(name + '\n\n')
			for each in text:
				if each == 'h':
					write_flag = False
				if write_flag == True and each != ' ':
					f.write(each)
				if write_flag == True and each == '\r':
					f.write('\n')			
			f.write('\n\n')

if __name__ == "__main__":
	print("\n\t\t欢迎使用《笔趣看》小说下载小工具\n\n\t\t作者:Jack-Cui\t时间:2017-05-06\n")
	print("*************************************************************************")
	
	#小说地址
	target_url = str(input("请输入小说目录下载地址:\n"))

	#实例化下载类
	d = download(target = target_url)
	name, numbers, url_dict = d.get_download_url()
	if name in os.listdir():
		os.remove(name)
	index = 1

	#下载中
	print("《%s》下载中:" % name[:-4])
	for key, value in url_dict.items():
		d.Writer(key, name, d.Downloader(value))
		sys.stdout.write("已下载:%.3f%%" %  float(index/numbers) + '\r')
		sys.stdout.flush()
		index += 1	

	print("《%s》下载完成！" % name[:-4])

	
