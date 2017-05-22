# -*- coding:UTF-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import requests
import os
import time

if __name__ == '__main__':
	list_url = []
	for num in range(1,3):
		if num == 1:
			url = 'http://www.shuaia.net/index.html'
		else:
			url = 'http://www.shuaia.net/index_%d.html' % num
		headers = {
				"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
		}
		req = requests.get(url = url,headers = headers)
		req.encoding = 'utf-8'
		html = req.text
		bf = BeautifulSoup(html, 'lxml')
		targets_url = bf.find_all(class_='item-img')
		
		for each in targets_url:
			list_url.append(each.img.get('alt') + '=' + each.get('href'))

	print('连接采集完成')

	for each_img in list_url:
		img_info = each_img.split('=')
		target_url = img_info[1]
		filename = img_info[0] + '.jpg'
		print('下载：' + filename)
		headers = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
		}
		img_req = requests.get(url = target_url,headers = headers)
		img_req.encoding = 'utf-8'
		img_html = img_req.text
		img_bf_1 = BeautifulSoup(img_html, 'lxml')
		img_url = img_bf_1.find_all('div', class_='wr-single-content-list')
		img_bf_2 = BeautifulSoup(str(img_url), 'lxml')
		img_url = 'http://www.shuaia.net' + img_bf_2.div.img.get('src')
		if 'images' not in os.listdir():
			os.makedirs('images')
		urlretrieve(url = img_url,filename = 'images/' + filename)
		time.sleep(1)

	print('下载完成！')