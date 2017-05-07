#-*-coding:utf-8-*-
import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter.filedialog import askdirectory
import webbrowser
import re
import json
from bs4 import BeautifulSoup
from urllib import request, parse

class APP:
	def __init__(self, width = 420, height = 250):
		self.w = width
		self.h = height
		self.title = ' VIP视频破解助手'
		self.root = tk.Tk(className=self.title)
		self.url = tk.StringVar()
		self.v = tk.IntVar()
		self.v.set(1)
		

		frame_1 = tk.Frame(self.root)
		frame_2 = tk.Frame(self.root)

		menu = tk.Menu(self.root)
		self.root.config(menu = menu)
		filemenu = tk.Menu(menu,tearoff=0)
		menu.add_cascade(label = '菜单', menu = filemenu)
		filemenu.add_command(label = '视频下载',command = self.download_wmxz)
		filemenu.add_command(label = '使用说明',command = lambda :webbrowser.open('http://blog.csdn.net/c406495762/article/details/71334633'))
		filemenu.add_command(label = '关于作者',command = lambda :webbrowser.open('http://blog.csdn.net/c406495762'))
		filemenu.add_command(label = '退出',command = self.root.quit)

		moviemenu = tk.Menu(menu,tearoff = 0)
		menu.add_cascade(label = '友情链接', menu = moviemenu)
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
	
		group = tk.Label(frame_1,text = '请选择一个视频播放通道：', padx = 10, pady = 10)
		tb1 = tk.Radiobutton(frame_1,text = '通道一', variable = self.v, value = 1, width = 14, height = 3)
		tb2 = tk.Radiobutton(frame_1,text = '通道二', variable = self.v, value = 2, width = 14, height = 3)
		label1 = tk.Label(frame_1, text = "请输入视频链接：")
		entry = tk.Entry(frame_1, textvariable = self.url, highlightcolor = 'blue', highlightthickness = 2)
		label2 = tk.Label(frame_1, text = "\n")
		play = tk.Button(frame_1, text = "播放", fg = 'red', width = 2, height = 1, command = self.confirm)
		label_explain = tk.Label(frame_2, fg = 'red', font = ('楷体',10), text = '\n注意：支持大部分主流视频网站的视频播放,\n暂只支持爱奇艺和优酷的视频下载。\n若播放失败请刷新浏览器或选择其他通道进行观看！')
		label_warning = tk.Label(frame_2, fg = 'blue', font = ('楷体',12),text = '\n建议：将Chrome内核浏览器设置为默认浏览器\n作者:Jack_Cui')

		frame_1.pack()
		frame_2.pack()

		group.grid(row = 0, column = 0)
		tb1.grid(row = 0, column = 1)
		tb2.grid(row = 0, column = 2)
		label1.grid(row = 1, column = 0)
		entry.grid(row = 1, column = 1)
		play.grid(row = 1, column = 2,ipadx = 5, ipady = 5)
		label_explain.grid(row = 4, column = 0)
		label_warning.grid(row = 5, column = 0)


	def confirm(self):
		port_1 = 'http://www.wmxz.wang/video.php?url='
		port_2 = 'http://www.vipjiexi.com/tong.php?url='
		#正则表达是判定是否为合法链接
		if re.match(r'^https?:/{2}\w.+$', self.url.get()):
			if self.v.get() == 1:
				webbrowser.open(port_1 + self.url.get())
			elif self.v.get() == 2:
				webbrowser.open(port_2 + self.url.get())
		else:
			msgbox.showerror(title='错误',message='视频链接地址无效，请重新输入！')

	def download_wmxz(self):	
		if re.match(r'^https?:/{2}\w.+$', self.url.get()):
			ip = self.url.get()
			get_url = 'http://www.sfsft.com/index.php?url=%s' % ip 
			
			get_movie_url = 'http://www.sfsft.com/api.php'
			
			head = {
				'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
				'Referer':'http://www.sfsft.com/index.php?url=%s' % ip
			}

			get_url_req = request.Request(url = get_url, headers = head)
			# data = parse.urlencode(data).encode('utf-8')
			get_url_response = request.urlopen(get_url_req)
			get_url_html = get_url_response.read().decode('utf-8')
			bf = BeautifulSoup(get_url_html, 'lxml')
			
			# print(bf.body.script.next_sibling.string)
			a = str(bf.find_all('script'))

			pattern = re.compile("url : '(.+)',", re.IGNORECASE)
			url = pattern.findall(a)[0]

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
	# def download_vipjiexi(self):
	# 	ip = 'http://www.iqiyi.com/v_19rrb7mkgo.html?fc=8b62d5327a54411b#vfrm=19-9-0-1'
	# 	get_url = 'http://www.vipjiexi.com/x2/tong.php?url=%s' % ip 
	# 	head = {
	# 		'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
	# 		'Referer':'http://www.vipjiexi.com/x2/tong.php?url=%s' % ip,
	# 	}
	# 	get_url_req = request.Request(url = get_url, headers = head)
	# 	get_url_response = request.urlopen(get_url_req)
	# 	get_url_html = get_url_response.read().decode('utf-8')
	# 	bf = BeautifulSoup(get_url_html, 'lxml')
	# 	a = str(bf.find_all('script'))
	# 	print(a)
	# 	pattern = re.compile('"api.php", {"time":"(\d+)", "key": "(.+)", "url"', re.IGNORECASE)
	# 	now_time = pattern.findall(a)[0][0]
	# 	now_key = pattern.findall(a)[0][1]

	# 	get_movie_url = 'http://www.vipjiexi.com/x2/api.php'
	# 	get_movie_data = {
	# 		'key':'%s' % now_key,
	# 		'time':'%s' % now_time,
	# 		'url':'http%3A%2F%2Fwww.iqiyi.com%2Fv_19rrb7mkgo.html%3Ffc%3D8b62d5327a54411b'
	# 	}
	# 	get_movie_req = request.Request(url = get_movie_url, headers = head)
	# 	get_movie_data = parse.urlencode(get_movie_data).encode('utf-8')
	# 	get_movie_response = request.urlopen(get_movie_req, get_movie_data)
	# 	get_movie_html = get_movie_response.read().decode('utf-8')
	# 	get_movie_data = json.loads(get_movie_html)
	# 	print(get_movie_data)

	def center(self):
		ws = self.root.winfo_screenwidth()
		hs = self.root.winfo_screenheight()
		x = int( (ws/2) - (self.w/2) )
		y = int( (hs/2) - (self.h/2) )
		self.root.geometry('{}x{}+{}+{}'.format(self.w, self.h, x, y))

	def loop(self):
		self.root.resizable(False, False)	#禁止修改窗口大小
		self.center()						#窗口居中
		self.root.mainloop()

if __name__ == '__main__':
	app = APP()
	app.loop()




