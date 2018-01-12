# -*-coding:utf-8 -*-
import requests
from lxml import etree
from bs4 import BeautifulSoup
import urllib
import time, re, types, os


"""
代码写的匆忙，本来想再重构下，完善好注释再发，但是比较忙，想想算了，所以自行完善吧！写法很不规范，勿见怪。

作者：  Jack Cui
Website:http://cuijiahua.com
注:     本软件仅用于学习交流，请勿用于任何商业用途！
"""

class BaiWan():
	def __init__(self):
		# 百度知道搜索接口
		self.baidu = 'http://zhidao.baidu.com/search?'
		# 百万英雄及接口,每个人的接口都不一样，里面包含的手机信息，因此不公布，请自行抓包，有疑问欢迎留言：http://cuijiahua.com/liuyan.html
		self.api = 'https://api-spe-ttl.ixigua.com/xxxxxxx={}'.format(int(time.time()*1000))

	# 获取答案并解析问题
	def get_question(self):
		to = True
		while to:
			list_dir = os.listdir('./')
			if 'question.txt' not in list_dir:
				fw = open('question.txt', 'w')
				fw.write('百万英雄尚未出题请稍后!')
				fw.close()		
			go = True
			while go:
				req = requests.get(self.api, verify=False)
				req.encoding = 'utf-8'
				html = req.text

				print(html)
				if '*' in html:
					question_start = html.index('*')
					try:
						
						question_end = html.index('？')
					except:
						question_end = html.index('?')
					question = html[question_start:question_end][2:]
					if question != None:
						fr = open('question.txt', 'r')
						text = fr.readline()
						fr.close()
						if text != question:
							print(question)
							go = False
							with open('question.txt', 'w') as f:
								f.write(question)
						else:
							time.sleep(1)
					else:
						to = False
				else:
					to = False

			temp = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9\+\-\*/]', html[question_end+1:])
			b_index = []
			print(temp)

			for index, each in enumerate(temp):
				if each == 'B':
					b_index.append(index)
				elif each == 'P' and (len(temp) - index) <= 3 :
					b_index.append(index)
					break

			if len(b_index) == 4:
				a = ''.join(temp[b_index[0] + 1:b_index[1]])
				b = ''.join(temp[b_index[1] + 1:b_index[2]])
				c = ''.join(temp[b_index[2] + 1:b_index[3]])
				alternative_answers = [a,b,c]

				if '下列' in question:
					question = a + ' ' + b + ' ' + c + ' ' + question.replace('下列', '')
				elif '以下' in question:
					question = a + ' ' + b + ' ' + c + ' ' + question.replace('以下', '')
			else:
				alternative_answers = []
			# 根据问题和备选答案搜索答案
			self.search(question, alternative_answers)
			time.sleep(1)

	def search(self, question, alternative_answers):
		print(question)
		print(alternative_answers)
		infos = {"word":question}
		# 调用百度接口
		url = self.baidu + 'lm=0&rn=10&pn=0&fr=search&ie=gbk&' + urllib.parse.urlencode(infos, encoding='GB2312')
		print(url)
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
		}
		sess = requests.Session()
		req = sess.get(url = url, headers=headers, verify=False)
		req.encoding = 'gbk'
		# print(req.text)
		bf = BeautifulSoup(req.text, 'lxml')
		answers = bf.find_all('dd',class_='dd answer')
		for answer in answers:
			print(answer.text)

		# 推荐答案
		recommend = ''
		if alternative_answers != []:
			best = []
			print('\n')
			for answer in answers:
				# print(answer.text)
				for each_answer in alternative_answers:
					if each_answer in answer.text:
						best.append(each_answer)
						print(each_answer,end=' ')
						# print(answer.text)
						print('\n')
						break
			statistics = {}
			for each in best:
				if each not in statistics.keys():
					statistics[each] = 1
				else:
					statistics[each] += 1
			errors = ['没有', '不是', '不对', '不正确','错误','不包括','不包含','不在','错']
			error_list = list(map(lambda x: x in question, errors))
			print(error_list)
			if sum(error_list) >= 1:
				for each_answer in alternative_answers:
					if each_answer not in statistics.items():
						recommend = each_answer
						print('推荐答案：', recommend)
						break
			elif statistics != {}:
				recommend = sorted(statistics.items(), key=lambda e:e[1], reverse=True)[0][0]
				print('推荐答案：', recommend)

		# 写入文件
		with open('file.txt', 'w') as f:
			f.write('问题：' + question)
			f.write('\n')
			f.write('*' * 50)
			f.write('\n')
			if alternative_answers != []:
				f.write('选项：')
				for i in range(len(alternative_answers)):
					f.write(alternative_answers[i])
					f.write('  ')
			f.write('\n')
			f.write('*' * 50)
			f.write('\n')
			f.write('参考答案：\n')
			for answer in answers:
				f.write(answer.text)
				f.write('\n')
			f.write('*' * 50)
			f.write('\n')
			if recommend != '':
				f.write('最终答案请自行斟酌！\t')
				f.write('推荐答案：' + sorted(statistics.items(), key=lambda e:e[1], reverse=True)[0][0])


if __name__ == '__main__':
	bw = BaiWan()
	bw.get_question()