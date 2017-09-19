# -*- coding:UTF-8 -*-
import requests, json, time, sys
from contextlib import closing

class get_photos(object):

	def __init__(self):
		self.photos_id = []
		self.download_server = 'https://unsplash.com/photos/xxx/download?force=trues'
		self.target = 'http://unsplash.com/napi/feeds/home'
		self.headers = {'authorization':'Client-ID c94869b36aa272dd62dfaeefed769d4115fb3189a9d1ec88ed457207747be626'}

	"""
	函数说明:获取图片ID
	Parameters:
		无
	Returns:
		无
	Modify:
		2017-09-13
	"""	
	def get_ids(self):
		req = requests.get(url=self.target, headers=self.headers, verify=False)
		html = json.loads(req.text)
		next_page = html['next_page']
		for each in html['photos']:
			self.photos_id.append(each['id'])
		time.sleep(1)
		for i in range(5):
			req = requests.get(url=next_page, headers=self.headers, verify=False)
			html = json.loads(req.text)
			next_page = html['next_page']
			for each in html['photos']:
				self.photos_id.append(each['id'])
			time.sleep(1)


	"""
	函数说明:图片下载
	Parameters:
		无
	Returns:
		无
	Modify:
		2017-09-13
	"""	
	def download(self, photo_id, filename):
		headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
		target = self.download_server.replace('xxx', photo_id)
		with closing(requests.get(url=target, stream=True, verify = False, headers = self.headers)) as r:
			with open('%d.jpg' % filename, 'ab+') as f:
				for chunk in r.iter_content(chunk_size = 1024):
					if chunk:
						f.write(chunk)
						f.flush()

if __name__ == '__main__':
	gp = get_photos()
	print('获取图片连接中:')
	gp.get_ids()
	print('图片下载中:')
	for i in range(len(gp.photos_id)):
		print('  正在下载第%d张图片' % (i+1))
		gp.download(gp.photos_id[i], (i+1))