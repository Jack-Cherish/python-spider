# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy import Selector
from cartoon.items import ComicItem

class ComicSpider(scrapy.Spider):
	name = 'comic'

	def __init__(self):
		#图片链接server域名
		self.server_img = 'http://n.1whour.com/'
		#章节链接server域名
		self.server_link = 'http://comic.kukudm.com'
		self.allowed_domains = ['comic.kukudm.com']
		self.start_urls = ['http://comic.kukudm.com/comiclist/3/']
		#匹配图片地址的正则表达式
		self.pattern_img = re.compile(r'\+"(.+)\'><span')

	#从start_requests发送请求
	def start_requests(self):
		yield scrapy.Request(url = self.start_urls[0], callback = self.parse1)

	#解析response,获得章节图片链接地址
	def parse1(self, response):
		hxs = Selector(response)
		items = []
		#章节链接地址
		urls = hxs.xpath('//dd/a[1]/@href').extract()
		#章节名
		dir_names = hxs.xpath('//dd/a[1]/text()').extract()
		#保存章节链接和章节名
		for index in range(len(urls)):
			item = ComicItem()
			item['link_url'] = self.server_link + urls[index]
			item['dir_name'] = dir_names[index]
			items.append(item)

		#根据每个章节的链接，发送Request请求，并传递item参数
		for item in items:
			yield scrapy.Request(url = item['link_url'], meta = {'item':item}, callback = self.parse2)
		
	#解析获得章节第一页的页码数和图片链接	
	def parse2(self, response):
		#接收传递的item
		item = response.meta['item']
		#获取章节的第一页的链接
		item['link_url'] = response.url
		hxs = Selector(response)
		#获取章节的第一页的图片链接
		pre_img_url = hxs.xpath('//script/text()').extract()
		#注意这里返回的图片地址,应该为列表,否则会报错
		img_url = [self.server_img + re.findall(self.pattern_img, pre_img_url[0])[0]]
		#将获取的章节的第一页的图片链接保存到img_url中
		item['img_url'] = img_url
		#返回item，交给item pipeline下载图片
		yield item
		#获取章节的页数
		page_num = hxs.xpath('//td[@valign="top"]/text()').re(u'共(\d+)页')[0]
		#根据页数，整理出本章节其他页码的链接
		pre_link = item['link_url'][:-5]
		for each_link in range(2, int(page_num) + 1):
			new_link = pre_link + str(each_link) + '.htm'
			#根据本章节其他页码的链接发送Request请求，用于解析其他页码的图片链接，并传递item
			yield scrapy.Request(url = new_link, meta = {'item':item}, callback = self.parse3)

	#解析获得本章节其他页面的图片链接
	def parse3(self, response):
		#接收传递的item
		item = response.meta['item']
		#获取该页面的链接
		item['link_url'] = response.url
		hxs = Selector(response)
		pre_img_url = hxs.xpath('//script/text()').extract()
		#注意这里返回的图片地址,应该为列表,否则会报错
		img_url = [self.server_img + re.findall(self.pattern_img, pre_img_url[0])[0]]
		#将获取的图片链接保存到img_url中
		item['img_url'] = img_url
		#返回item，交给item pipeline下载图片
		yield item
		