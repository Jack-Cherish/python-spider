# -*- coding:utf-8 -*-
from tkinter.filedialog import askdirectory
from MyQR.myqr import run
from urllib import request, parse
from bs4 import BeautifulSoup

import tkinter.messagebox as msgbox
import tkinter as tk
import webbrowser
import re
import json
import os
import types
import requests
import time


"""
类说明:爱奇艺、优酷等实现在线观看以及视频下载的类

Parameters:
	width - tkinter主界面宽
	height - tkinter主界面高

Returns:
	无

Modify:
	2017-05-09
"""
class APP:
	def __init__(self, width = 500, height = 300):
		self.w = width
		self.h = height
		self.title = ' VIP视频破解助手'
		self.root = tk.Tk(className=self.title)
		self.url = tk.StringVar()
		self.v = tk.IntVar()
		self.v.set(1)


		#Frame空间
		frame_1 = tk.Frame(self.root)
		frame_2 = tk.Frame(self.root)
		frame_3 = tk.Frame(self.root)
		
		#Menu菜单
		menu = tk.Menu(self.root)
		self.root.config(menu = menu)
		filemenu = tk.Menu(menu,tearoff=0)
		moviemenu = tk.Menu(menu,tearoff = 0)
		menu.add_cascade(label = '菜单', menu = filemenu)
		menu.add_cascade(label = '友情链接', menu = moviemenu)
		filemenu.add_command(label = '使用说明',command = lambda :webbrowser.open('http://blog.csdn.net/c406495762/article/details/71334633'))
		filemenu.add_command(label = '关于作者',command = lambda :webbrowser.open('http://blog.csdn.net/c406495762'))
		filemenu.add_command(label = '退出',command = self.root.quit)

		#各个网站链接
		moviemenu.add_command(label = '网易公开课',command = lambda :webbrowser.open('http://open.163.com/'))
		moviemenu.add_command(label = '腾讯视频',command = lambda :webbrowser.open('http://v.qq.com/'))
		moviemenu.add_command(label = '搜狐视频',command = lambda :webbrowser.open('http://tv.sohu.com/'))
		moviemenu.add_command(label = '芒果TV',command = lambda :webbrowser.open('http://www.mgtv.com/'))
		moviemenu.add_command(label = '爱奇艺',command = lambda :webbrowser.open('http://www.iqiyi.com/'))
		moviemenu.add_command(label = 'PPTV',command = lambda :webbrowser.open('http://www.bilibili.com/'))
		moviemenu.add_command(label = '优酷',command = lambda :webbrowser.open('http://www.youku.com/'))
		moviemenu.add_command(label = '乐视',command = lambda :webbrowser.open('http://www.le.com/'))
		moviemenu.add_command(label = '土豆',command = lambda :webbrowser.open('http://www.tudou.com/'))
		moviemenu.add_command(label = 'A站',command = lambda :webbrowser.open('http://www.acfun.tv/'))
		moviemenu.add_command(label = 'B站',command = lambda :webbrowser.open('http://www.bilibili.com/'))

		#控件内容设置
		group = tk.Label(frame_1,text = '请选择一个视频播放通道：', padx = 10, pady = 10)
		tb1 = tk.Radiobutton(frame_1,text = '通道一', variable = self.v, value = 1, width = 10, height = 3)
		tb2 = tk.Radiobutton(frame_1,text = '通道二', variable = self.v, value = 2, width = 10, height = 3)
		label1 = tk.Label(frame_2, text = "请输入视频链接：")
		entry = tk.Entry(frame_2, textvariable = self.url, highlightcolor = 'Fuchsia', highlightthickness = 1,width = 35)
		label2 = tk.Label(frame_2, text = " ")
		play = tk.Button(frame_2, text = "播放", font = ('楷体',12), fg = 'Purple', width = 2, height = 1, command = self.video_play)
		label3 = tk.Label(frame_2, text = " ")
		# download = tk.Button(frame_2, text = "下载", font = ('楷体',12), fg = 'Purple', width = 2, height = 1, command = self.download_wmxz)
		QR_Code = tk.Button(frame_3, text = "手机观看", font = ('楷体',12), fg = 'Purple', width = 10, height = 2, command = self.QR_Code)
		label_explain = tk.Label(frame_3, fg = 'red', font = ('楷体',12), text = '\n注意：支持大部分主流视频网站的视频播放！\n此软件仅用于交流学习，请勿用于任何商业用途！')
		label_warning = tk.Label(frame_3, fg = 'blue', font = ('楷体',12),text = '\n建议：将Chrome内核浏览器设置为默认浏览器\n作者:Jack_Cui')



		#控件布局
		frame_1.pack()
		frame_2.pack()
		frame_3.pack()
		group.grid(row = 0, column = 0)
		tb1.grid(row = 0, column = 1)
		tb2.grid(row = 0, column = 2)
		label1.grid(row = 0, column = 0)
		entry.grid(row = 0, column = 1)
		label2.grid(row = 0, column = 2)
		play.grid(row = 0, column = 3,ipadx = 10, ipady = 10)
		label3.grid(row = 0, column = 4)
		# download.grid(row = 0, column = 5,ipadx = 10, ipady = 10)
		QR_Code.grid(row = 0, column = 0)
		label_explain.grid(row = 1, column = 0)
		label_warning.grid(row = 2, column = 0)

	"""
	函数说明:jsonp解析

	Parameters:
		_jsonp - jsonp字符串

	Returns:
		_json - json格式数据

	Modify:
		2017-05-11
	"""
	def loads_jsonp(self, _jsonp):
		try:
			_json = json.loads(re.match(".*?({.*}).*",_jsonp,re.S).group(1))
			return _json
		except:
			raise ValueError('Invalid Input')

	"""
	函数说明:视频播放

	Parameters:
		self

	Returns:
		无

	Modify:
		2017-05-09
	"""
	def video_play(self):
		#视频解析网站地址
		port_1 = 'http://www.wmxz.wang/video.php?url='
		port_2 = 'http://www.vipjiexi.com/tong.php?url='

		#正则表达是判定是否为合法链接
		if re.match(r'^https?:/{2}\w.+$', self.url.get()):
			if self.v.get() == 1:
				#视频链接获取
				ip = self.url.get()
				#视频链接加密
				ip = parse.quote_plus(ip)
				#浏览器打开
				webbrowser.open(port_1 + self.url.get())
			elif self.v.get() == 2:
				#链接获取
				ip = self.url.get()
				#链接加密
				ip = parse.quote_plus(ip)

				#获取time、key、url
				get_url = 'http://www.vipjiexi.com/x2/tong.php?url=%s' % ip 
				# get_url_head = {
				# 	'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
				# 	'Referer':'http://www.vipjiexi.com/',
				# }
				# get_url_req = request.Request(url = get_url, headers = get_url_head)
				# get_url_response = request.urlopen(get_url_req)
				# get_url_html = get_url_response.read().decode('utf-8')
				# bf = BeautifulSoup(get_url_html, 'lxml')
				# a = str(bf.find_all('script'))
				# pattern = re.compile('"api.php", {"time":"(\d+)", "key": "(.+)", "url": "(.+)","type"', re.IGNORECASE)
				# string = pattern.findall(a)
				# now_time = string[0][0]
				# now_key = string[0][1]
				# now_url = string[0][2] 

				# #请求播放,获取Success = 1
				# get_movie_url = 'http://www.vipjiexi.com/x2/api.php'
				# get_movie_data = {
				# 	'key':'%s' % now_key,
				# 	'time':'%s' % now_time,
				# 	'type':'',
				# 	'url':'%s' % now_url
				# }
				# get_movie_head = {
				# 	'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
				# 	'Referer':'http://www.vipjiexi.com/x2/tong.php?',
				# 	'url':'%s' % ip,
				# }
				# get_movie_req = request.Request(url = get_movie_url, headers = get_movie_head)
				# get_movie_data = parse.urlencode(get_movie_data).encode('utf-8')
				# get_movie_response = request.urlopen(get_movie_req, get_movie_data)
				#请求之后立刻打开
				webbrowser.open(get_url)

		else:
			msgbox.showerror(title='错误',message='视频链接地址无效，请重新输入！')

	"""
	函数说明:视频下载，通过无名小站抓包(已经无法使用)

	Parameters:
		self

	Returns:
		无

	Modify:
		2017-06-15
	"""
	def download_wmxz(self):	
		if re.match(r'^https?:/{2}\w.+$', self.url.get()):
			#视频链接获取
			ip = self.url.get()
			#视频链接加密
			ip = parse.quote_plus(ip)

			#获取保存视频的url
			get_url = 'http://www.sfsft.com/index.php?url=%s' % ip 
			head = {
				'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
				'Referer':'http://www.sfsft.com/index.php?url=%s' % ip
			}
			get_url_req = request.Request(url = get_url, headers = head)
			get_url_response = request.urlopen(get_url_req)
			get_url_html = get_url_response.read().decode('utf-8')
			bf = BeautifulSoup(get_url_html, 'lxml')
			a = str(bf.find_all('script'))
			pattern = re.compile("url : '(.+)',", re.IGNORECASE)
			url = pattern.findall(a)[0]

			#获取视频地址
			get_movie_url = 'http://www.sfsft.com/api.php'
			get_movie_data = {
				'up':'0',
				'url':'%s' % url,
			}
			get_movie_req = request.Request(url = get_movie_url, headers = head)
			get_movie_data = parse.urlencode(get_movie_data).encode('utf-8')
			get_movie_response = request.urlopen(get_movie_req, get_movie_data)
			get_movie_html = get_movie_response.read().decode('utf-8')
			get_movie_data = json.loads(get_movie_html)
			webbrowser.open(get_movie_data['url'])
		else:
			msgbox.showerror(title='错误',message='视频链接地址无效，请重新输入！')


	"""
	函数说明:生成二维码,手机观看

	Parameters:
		self

	Returns:
		无

	Modify:
		2017-05-12
	"""
	def QR_Code(self):	
		if re.match(r'^https?:/{2}\w.+$', self.url.get()):
			#视频链接获取
			ip = self.url.get()
			#视频链接加密
			ip = parse.quote_plus(ip)

			url = 'http://www.wmxz.wang/video.php?url=%s' % ip
			words = url
			images_pwd = os.getcwd() + '\Images\\'
			png_path = images_pwd + 'bg.png'
			qr_name = 'qrcode.png'
			qr_path = images_pwd + 'qrcode.png'

			run(words = words, picture = png_path, save_name = qr_name, save_dir = images_pwd)

			top = tk.Toplevel(self.root)
			img = tk.PhotoImage(file = qr_path)
			text_label = tk.Label(top, fg = 'red', font = ('楷体',15), text = "手机浏览器扫描二维码，在线观看视频！")
			img_label = tk.Label(top, image = img)
			text_label.pack()
			img_label.pack()
			top.mainloop()

		else:
			msgbox.showerror(title='错误',message='视频链接地址无效，请重新输入！')

	"""
	函数说明:tkinter窗口居中

	Parameters:
		self

	Returns:
		无

	Modify:
		2017-05-09
	"""
	def center(self):
		ws = self.root.winfo_screenwidth()
		hs = self.root.winfo_screenheight()
		x = int( (ws/2) - (self.w/2) )
		y = int( (hs/2) - (self.h/2) )
		self.root.geometry('{}x{}+{}+{}'.format(self.w, self.h, x, y))

	"""
	函数说明:loop等待用户事件

	Parameters:
		self

	Returns:
		无

	Modify:
		2017-05-09
	"""
	def loop(self):
		self.root.resizable(False, False)	#禁止修改窗口大小
		self.center()						#窗口居中
		self.root.mainloop()

if __name__ == '__main__':
	app = APP()			#实例化APP对象
	app.loop()			#loop等待用户事件




