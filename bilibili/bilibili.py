# -*-coding:utf-8 -*-
# Website: http://cuijiahua.com
# Author: Jack Cui
# Date: 2018.6.9

import requests, json, re, sys, os, urllib, argparse, time
from urllib.request import urlretrieve
from contextlib import closing
from urllib import parse
import xml2ass

class BiliBili:
	def __init__(self, dirname, keyword):
		self.dn_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Referer': 'https://search.bilibili.com/all?keyword=%s' % parse.quote(keyword)}

		self.search_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept': 'application/json, text/plain, */*'}

		self.video_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}

		self.danmu_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-CN,zh;q=0.9'}

		self.sess = requests.Session()

		self.dir = dirname

	def video_downloader(self, video_url, video_name):
		"""
		视频下载
		Parameters:
			video_url: 带水印的视频地址
			video_name: 视频名
		Returns:
			无
		"""
		size = 0
		with closing(self.sess.get(video_url, headers=self.dn_headers, stream=True, verify=False)) as response:
			chunk_size = 1024
			content_size = int(response.headers['content-length'])
			if response.status_code == 200:
				sys.stdout.write('  [文件大小]:%0.2f MB\n' % (content_size / chunk_size / 1024))
				video_name = os.path.join(self.dir, video_name)
				with open(video_name, 'wb') as file:
					for data in response.iter_content(chunk_size = chunk_size):
						file.write(data)
						size += len(data)
						file.flush()

						sys.stdout.write('  [下载进度]:%.2f%%' % float(size / content_size * 100) + '\r')
						# sys.stdout.flush()
						if size / content_size == 1:
							print('\n')
			else:
				print('链接异常')

	def search_video(self, search_url):
		"""
		搜索接口
		Parameters:
			search_url: 带水印的视频地址
		Returns:
			titles：视频名列表
			arcurls: 视频播放地址列表
		"""
		req = self.sess.get(url=search_url, headers=self.search_headers, verify=False)
		html = json.loads(req.text)
		videos = html["data"]['result']
		titles = []
		arcurls = []
		for video in videos:
			titles.append(video['title'].replace('<em class="keyword">','').replace('</em>',''))
			arcurls.append(video['arcurl'])
		return titles, arcurls

	def get_download_url(self, arcurl):
		"""
		获取视频下载地址
		Parameters:
			arcurl: 视频播放地址
			oid：弹幕地址参数
		Returns:
			download_url：视频下载地址
		"""
		req = self.sess.get(url=arcurl, headers=self.video_headers, verify=False)
		pattern = '.__playinfo__=(.*)</script><script>window.__INITIAL_STATE__='
		try:
			infos = re.findall(pattern, req.text)[0]
		except:
			return '',''
		html = json.loads(infos)
		durl = html['durl']
		download_url = []
		for i in range(len(durl)):
			download_url.append(durl[i]['url'])
		url = durl[0]['url']
		if 'mirrork' in url:
			oid = url.split('/')[6]
		else:
			id_ = url.split('/')[7]
			if len(id_) >= 10:
				id_ = url.split('/')[6]
			oid = id_
		return download_url, oid


	def download_xml(self, danmu_url, danmu_name):
		"""
		获取视频XML原生弹幕
		Parameters:
			danmu_url: 弹幕地址
			danmu_name：弹幕xml文件保存名
		Returns:
			无
		"""
		with closing(self.sess.get(danmu_url, headers=self.danmu_header, stream=True, verify=False)) as response:  
			if response.status_code == 200:
				with open(danmu_name, 'wb') as file:
					for data in response.iter_content():
						file.write(data)
						file.flush()
			else:
				print('链接异常')

	def get_danmu(self, oid, filename):
		"""
		下载弹幕
		Parameters:
			oid: 弹幕oid
			filename: 弹幕保存前缀名
		Returns:
			无
		"""
		danmu_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid={}'.format(oid)
		danmu_name = os.path.join(self.dir, filename + '.xml')
		danmu_ass = os.path.join(self.dir, filename + '.ass')
		self.download_xml(danmu_url, danmu_name)
		time.sleep(0.5)
		xml2ass.Danmaku2ASS(danmu_name, danmu_ass, 1280, 720)
		# os.remove(danmu_name)

	def search_videos(self, keyword, pages):
		"""
		搜索视频
		Parameters:
			keyword: 搜索关键字
			pages：下载页数
		Returns:
			无
		"""
		if self.dir not in os.listdir():
			os.mkdir(self.dir)
		for page in range(1, pages+1):
			search_url = 'https://api.bilibili.com/x/web-interface/search/type?jsonp=jsonp&search_type=video&keyword={}&page={}'.format(keyword, page)
			titles, arcurls = self.search_video(search_url)
			for index, arcurl in enumerate(arcurls):
				title = titles[index]
				for c in u'´☆❤◦\/:*?"<>|':
					title = title.replace(c, '')
				if title + '.flv' not in os.listdir(self.dir):
					download_url, oid = self.get_download_url(arcurl)
					movies = []
					for i in range(len(download_url)):
						if download_url[i] != '' and oid != '':
							fname = title + '_' + str(i+1) + '.flv'
							movies.append(fname)
							print('第[ %d ]页:视频[ %s ]下载中:' % (page, fname))
							self.video_downloader(download_url[i], fname)
							print('视频下载完成!')
					if len(movies) > 1:
						filelist_fname = os.path.join(self.dir, 'filelist.txt')
						with open(filelist_fname, 'w') as f:
							for flv in movies:
								f.write("file " + flv)
								f.write('\n')
						try:
							os.system('cd %s & ffmpeg -f concat -safe 0 -i %s -c copy %s' % (self.dir, 'filelist.txt', title + '.flv'))
						except:
							print('请安装FFmpeg,并配置环境变量 http://ffmpeg.org/')
						os.remove(filelist_fname)
						for movie in movies:
							os.remove(os.path.join(self.dir, movie))
						print('视频合并完成！')
					self.get_danmu(oid, title)
					print('弹幕下载完成!')

if __name__ == '__main__':
	if len(sys.argv) == 1:
		sys.argv.append('--help')

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dir', required=True, help=_('download path'))
	parser.add_argument('-k', '--keyword', required=True, help=_('search content'))
	parser.add_argument('-p', '--pages', required=True, help=_('the number of pages for downloading'), type=int, default=1)
	
	args = parser.parse_args()
	B = BiliBili(args.dir,args.keyword)
	B.search_videos(args.keyword, args.pages)

	print('全部下载完成!')
