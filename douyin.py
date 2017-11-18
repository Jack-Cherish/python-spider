# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from contextlib import closing
import requests, json, time, re, os, sys, types

class DouYin(object):
	def __init__(self):
		"""
		抖音App视频下载
		"""
		#SSL认证
		pass

	def get_video_urls(self, nickname):
		"""
		获得视频播放地址
		Parameters:
			nickname：查询的用户名
		Returns:
			video_names: 视频名字列表
			video_urls: 视频链接列表
			aweme_count: 视频数量
		"""
		video_names = []
		video_urls = []

		search_url = 'https://api.amemv.com/aweme/v1/discover/search/?cursor=0&keyword=%s&count=10&type=1&retry_type=no_retry&iid=17900846586&device_id=34692364855&ac=wifi&channel=xiaomi&aid=1128&app_name=aweme&version_code=162&version_name=1.6.2&device_platform=android&ssmix=a&device_type=MI+5&device_brand=Xiaomi&os_api=24&os_version=7.0&uuid=861945034132187&openudid=dc451556fc0eeadb&manifest_version_code=162&resolution=1080*1920&dpi=480&update_version_code=1622' % (nickname)
		req = requests.get(url = search_url, verify = False)
		html = json.loads(req.text)

		for each in html['user_list']:
			if each['user_info']['nickname'] == nickname:
				aweme_count = each['user_info']['aweme_count']
				user_id = each['user_info']['uid']
		print(user_id)
		user_url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&max_cursor=0&count=%s' % (user_id, aweme_count)
		req = requests.get(url = user_url, verify = False)
		html = json.loads(req.text)
		for each in html['aweme_list']:
			share_desc = each['share_info']['share_desc']
			if '抖音-原创音乐短视频社区' == share_desc:
				print(each)
				video_names.append(each['cha_list'][0]['cha_name'] + '.mp4')
			else:
				video_names.append(share_desc + '.mp4')
			video_urls.append(each['share_info']['share_url'])
		return video_names, video_urls, aweme_count

	def get_download_url(self, video_url):
		"""
		获得视频播放地址
		Parameters:
			video_url：视频播放地址
		Returns:
			download_url: 视频下载地址
		"""
		req = requests.get(url = video_url, verify = False)
		bf = BeautifulSoup(req.text, 'lxml')
		script = bf.find_all('script')[-1]
		video_url_js = re.findall('var data = \[(.+)\];', str(script))[0]
		video_html = json.loads(video_url_js)
		download_url = video_html['video']['play_addr']['url_list'][0]
		return download_url

	def video_downloader(self, video_url, video_name):
		"""
		视频下载
		Parameters:
			None
		Returns:
			None
		"""
		size = 0
		with closing(requests.get(video_url, stream=True, verify = False)) as response:
			chunk_size = 1024
			content_size = int(response.headers['content-length']) 
			if response.status_code == 200:
				print('  [文件大小]:%0.2f MB' % (content_size / chunk_size / 1024))

				with open(video_name, "wb") as file:  
					for data in response.iter_content(chunk_size = chunk_size):
						file.write(data)
						size += len(data)
						file.flush()

					sys.stdout.write('    [下载进度]:%.2f%%' % float(size / content_size * 100))
					sys.stdout.flush()


	def run(self, nickname):
		"""
		运行函数
		Parameters:
			None
		Returns:
			None
		"""
		self.hello()
		video_names, video_urls, aweme_count = self.get_video_urls(nickname)
		if nickname not in os.listdir():
			os.mkdir(nickname)
		print('视频下载中:\n')
		for num in range(aweme_count):
			print('  ' + video_names[num])
			video_url = self.get_download_url(video_urls[num])
			if '\\' in video_names[num]:
				video_name = video_names[num].replace('\\', '')
			elif '/' in video_names[num]:
				video_name = video_names[num].replace('/', '')
			else:
				video_name = video_names[num]
			self.video_downloader(video_url, os.path.join(nickname.strip(), video_name))
			print('')

	def hello(self):
		"""
		打印欢迎界面
		Parameters:
			None
		Returns:
			None
		"""
		print('*' * 100)
		print('\t\t\t\t抖音App视频下载小助手')
		print('*' * 100)

if __name__ == '__main__':
	douyin = DouYin()
	nickname = r'徐浪浪and芒果琳'
	douyin.run(nickname)
