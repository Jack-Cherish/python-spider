# -*- coding:UTF-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
import subprocess as sp
from lxml import etree
import requests
import random
import re

"""
函数说明:获取IP代理
Parameters:
	page - 高匿代理页数,默认获取第一页
Returns:
	proxys_list - 代理列表
Modify:
	2017-05-27
"""
def get_proxys(page = 1):
	#requests的Session可以自动保持cookie,不需要自己维护cookie内容
	S = requests.Session()
	#西祠代理高匿IP地址
	target_url = 'http://www.xicidaili.com/nn/%d' % page
	#完善的headers
	target_headers = {'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Referer':'http://www.xicidaili.com/nn/',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8',
	}
	#get请求
	target_response = S.get(url = target_url, headers = target_headers)
	#utf-8编码
	target_response.encoding = 'utf-8'
	#获取网页信息
	target_html = target_response.text
	#获取id为ip_list的table
	bf1_ip_list = BeautifulSoup(target_html, 'lxml')
	bf2_ip_list = BeautifulSoup(str(bf1_ip_list.find_all(id = 'ip_list')), 'lxml')
	ip_list_info = bf2_ip_list.table.contents
	#存储代理的列表
	proxys_list = []
	#爬取每个代理信息
	for index in range(len(ip_list_info)):
		if index % 2 == 1 and index != 1:
			dom = etree.HTML(str(ip_list_info[index]))
			ip = dom.xpath('//td[2]')
			port = dom.xpath('//td[3]')
			protocol = dom.xpath('//td[6]')
			proxys_list.append(protocol[0].text.lower() + '#' + ip[0].text + '#' + port[0].text)
	#返回代理列表
	return proxys_list

"""
函数说明:检查代理IP的连通性
Parameters:
	ip - 代理的ip地址
	lose_time - 匹配丢包数
	waste_time - 匹配平均时间
Returns:
	average_time - 代理ip平均耗时
Modify:
	2017-05-27
"""
def check_ip(ip, lose_time, waste_time):
	#命令 -n 要发送的回显请求数 -w 等待每次回复的超时时间(毫秒)
	cmd = "ping -n 3 -w 3 %s"
	#执行命令
	p = sp.Popen(cmd % ip, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True) 
	#获得返回结果并解码
	out = p.stdout.read().decode("gbk")
	#丢包数
	lose_time = lose_time.findall(out)
	#当匹配到丢失包信息失败,默认为三次请求全部丢包,丢包数lose赋值为3
	if len(lose_time) == 0:
		lose = 3
	else:
		lose = int(lose_time[0])
	#如果丢包数目大于2个,则认为连接超时,返回平均耗时1000ms
	if lose > 2:
		#返回False
		return 1000
	#如果丢包数目小于等于2个,获取平均耗时的时间
	else:
		#平均时间
		average = waste_time.findall(out)
		#当匹配耗时时间信息失败,默认三次请求严重超时,返回平均好使1000ms
		if len(average) == 0:
			return 1000
		else:
			#
			average_time = int(average[0])
			#返回平均耗时
			return average_time

"""
函数说明:初始化正则表达式
Parameters:
	无
Returns:
	lose_time - 匹配丢包数
	waste_time - 匹配平均时间
Modify:
	2017-05-27
"""
def initpattern():
	#匹配丢包数
	lose_time = re.compile(u"丢失 = (\d+)", re.IGNORECASE)
	#匹配平均时间
	waste_time = re.compile(u"平均 = (\d+)ms", re.IGNORECASE)
	return lose_time, waste_time

if __name__ == '__main__':
	#初始化正则表达式
	lose_time, waste_time = initpattern()
	#获取IP代理
	proxys_list = get_proxys(1)

	#如果平均时间超过200ms重新选取ip
	while True:
		#从100个IP中随机选取一个IP作为代理进行访问
		proxy = random.choice(proxys_list)
		split_proxy = proxy.split('#')
		#获取IP
		ip = split_proxy[1]
		#检查ip
		average_time = check_ip(ip, lose_time, waste_time)
		if average_time > 200:
			#去掉不能使用的IP
			proxys_list.remove(proxy)
			print("ip连接超时, 重新获取中!")
		if average_time < 200:
			break

	#去掉已经使用的IP
	proxys_list.remove(proxy)
	proxy_dict = {split_proxy[0]:split_proxy[1] + ':' + split_proxy[2]}
	print("使用代理:", proxy_dict)
