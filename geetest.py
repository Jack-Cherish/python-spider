# -*-coding:utf-8 -*-
import random
import re
import time
# 图片转换
import base64
from urllib.request import urlretrieve

from bs4 import BeautifulSoup

import PIL.Image as image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def save_base64img(data_str, save_name):
    """
    将 base64 数据转化为图片保存到指定位置
    :param data_str: base64 数据，不包含类型
    :param save_name: 保存的全路径
    """
    img_data = base64.b64decode(data_str)
    file = open(save_name, 'wb')
    file.write(img_data)
    file.close()


def get_base64_by_canvas(driver, class_name, contain_type):
    """
    将 canvas 标签内容转换为 base64 数据
    :param driver: webdriver 对象
    :param class_name: canvas 标签的类名
    :param contain_type: 返回的数据是否包含类型
    :return: base64 数据
    """
    # 防止图片未加载完就下载一张空图
    bg_img = ''
    while len(bg_img) < 5000:
        getImgJS = 'return document.getElementsByClassName("' + class_name + '")[0].toDataURL("image/png");'
        bg_img = driver.execute_script(getImgJS)
        time.sleep(0.5)
    # print(bg_img)
    if contain_type:
        return bg_img
    else:
        return bg_img[bg_img.find(',') + 1:]


def save_bg(driver, bg_path="bg.png", bg_class="geetest_canvas_bg geetest_absolute"):
    """
    保存包含缺口的背景图
    :param driver: webdriver 对象
    :param bg_path: 保存路径
    :param bg_class: 背景图的 class 属性
    :return: 保存路径
    """
    bg_img_data = get_base64_by_canvas(driver, bg_class, False)
    save_base64img(bg_img_data, bg_path)
    return bg_path


def save_full_bg(driver, full_bg_path="fbg.png", full_bg_class="geetest_canvas_fullbg geetest_fade geetest_absolute"):
    """
    保存完整的的背景图
    :param driver: webdriver 对象
    :param full_bg_path: 保存路径
    :param full_bg_class: 完整背景图的 class 属性
    :return: 保存路径
    """
    bg_img_data = get_base64_by_canvas(driver, full_bg_class, False)
    save_base64img(bg_img_data, full_bg_path)
    return full_bg_path

class Crack():
	def __init__(self,keyword):
		self.url = '*'
		self.browser = webdriver.Chrome('D:\\chromedriver.exe')
		self.wait = WebDriverWait(self.browser, 100)
		self.keyword = keyword
		self.BORDER = 6

	def open(self):
		"""
		打开浏览器,并输入查询内容
		"""
		self.browser.get(self.url)
		keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'keyword_qycx')))
		bowton = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn')))
		keyword.send_keys(self.keyword)
		bowton.click()

	def get_images(self, bg_filename = 'bg.jpg', fullbg_filename = 'fullbg.jpg'):
		"""
		获取验证码图片
		:return: 图片的location信息
		"""
		bg = []
		fullgb = []
		while bg == [] and fullgb == []:
			bf = BeautifulSoup(self.browser.page_source, 'lxml')
			bg = bf.find_all('div', class_ = 'gt_cut_bg_slice')
			fullgb = bf.find_all('div', class_ = 'gt_cut_fullbg_slice')
		bg_url = re.findall('url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
		fullgb_url = re.findall('url\(\"(.*)\"\);', fullgb[0].get('style'))[0].replace('webp', 'jpg')
		bg_location_list = []
		fullbg_location_list = []
		for each_bg in bg:
			location = {}
			location['x'] = int(re.findall('background-position: (.*)px (.*)px;',each_bg.get('style'))[0][0])
			location['y'] = int(re.findall('background-position: (.*)px (.*)px;',each_bg.get('style'))[0][1])
			bg_location_list.append(location)
		for each_fullgb in fullgb:
			location = {}
			location['x'] = int(re.findall('background-position: (.*)px (.*)px;',each_fullgb.get('style'))[0][0])
			location['y'] = int(re.findall('background-position: (.*)px (.*)px;',each_fullgb.get('style'))[0][1])
			fullbg_location_list.append(location)

		urlretrieve(url = bg_url, filename = bg_filename)
		print('缺口图片下载完成')
		urlretrieve(url = fullgb_url, filename = fullbg_filename)
		print('背景图片下载完成')
		return bg_location_list, fullbg_location_list

	def get_merge_image(self, filename, location_list):
		"""
		根据位置对图片进行合并还原
		:filename:图片
		:location_list:图片位置
		"""
		im = image.open(filename)
		new_im = image.new('RGB', (260,116))
		im_list_upper=[]
		im_list_down=[]

		for location in location_list:
			if location['y'] == -58:
				im_list_upper.append(im.crop((abs(location['x']),58,abs(location['x']) + 10, 166)))
			if location['y'] == 0:
				im_list_down.append(im.crop((abs(location['x']),0,abs(location['x']) + 10, 58)))

		new_im = image.new('RGB', (260,116))

		x_offset = 0
		for im in im_list_upper:
			new_im.paste(im, (x_offset,0))
			x_offset += im.size[0]

		x_offset = 0
		for im in im_list_down:
			new_im.paste(im, (x_offset,58))
			x_offset += im.size[0]

		new_im.save(filename)

		return new_im

	def get_merge_image(self, filename, location_list):
		"""
		根据位置对图片进行合并还原
		:filename:图片
		:location_list:图片位置
		"""
		im = image.open(filename)
		new_im = image.new('RGB', (260,116))
		im_list_upper=[]
		im_list_down=[]

		for location in location_list:
			if location['y']==-58:
				im_list_upper.append(im.crop((abs(location['x']),58,abs(location['x'])+10,166)))
			if location['y']==0:
				im_list_down.append(im.crop((abs(location['x']),0,abs(location['x'])+10,58)))

		new_im = image.new('RGB', (260,116))

		x_offset = 0
		for im in im_list_upper:
			new_im.paste(im, (x_offset,0))
			x_offset += im.size[0]

		x_offset = 0
		for im in im_list_down:
			new_im.paste(im, (x_offset,58))
			x_offset += im.size[0]

		new_im.save(filename)

		return new_im

	def is_pixel_equal(self, img1, img2, x, y):
		"""
		判断两个像素是否相同
		:param image1: 图片1
		:param image2: 图片2
		:param x: 位置x
		:param y: 位置y
		:return: 像素是否相同
		"""
		# 取两个图片的像素点
		pix1 = img1.load()[x, y]
		pix2 = img2.load()[x, y]
		threshold = 60
		if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] < threshold)):
			return True
		else:
			return False

	def get_gap(self, img1, img2):
		"""
		获取缺口偏移量
		:param img1: 不带缺口图片
		:param img2: 带缺口图片
		:return:
		"""
		left = 43
		for i in range(left, img1.size[0]):
			for j in range(img1.size[1]):
				if not self.is_pixel_equal(img1, img2, i, j):
					left = i
					return left
		return left	

	def get_track(self, distance):
		"""
		根据偏移量获取移动轨迹
		:param distance: 偏移量
		:return: 移动轨迹
		"""
		# 移动轨迹
		track = []
		# 当前位移
		current = 0
		# 减速阈值
		mid = distance * 4 / 5
		# 计算间隔
		t = 0.2
		# 初速度
		v = 0
        
		while current < distance:
			if current < mid:
				# 加速度为正2
				a = 2
			else:	
				# 加速度为负3
				a = -3
			# 初速度v0
			v0 = v
			# 当前速度v = v0 + at
			v = v0 + a * t
			# 移动距离x = v0t + 1/2 * a * t^2
			move = v0 * t + 1 / 2 * a * t * t
			# 当前位移
			current += move
			# 加入轨迹
			track.append(round(move))
		return track

	def get_slider(self):
		"""
		获取滑块
		:return: 滑块对象
		"""
		while True:
			try:
				slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
				break
			except:
				time.sleep(0.5)
		return slider

	def move_to_gap(self, slider, track):
		"""
		拖动滑块到缺口处
		:param slider: 滑块
		:param track: 轨迹
		:return:
		"""
		ActionChains(self.browser).click_and_hold(slider).perform()
		while track:
			x = random.choice(track)
			ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
			track.remove(x)
		time.sleep(0.5)
		ActionChains(self.browser).release().perform()

	def crack(self):
		# 打开浏览器
		self.open()

		# 保存的图片名字
		bg_filename = 'bg.jpg'
		fullbg_filename = 'fullbg.jpg'

		# 获取图片
		bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)

		# 根据位置对图片进行合并还原
		# 方法1
		# bg_img = self.get_merge_image(bg_filename, bg_location_list)
		# fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)
		# 方法2
		bg_img = save_bg(self.browser)
		full_bg_img = save_full_bg(self.browser)

		# 获取缺口位置
		# 方法1
		# gap = self.get_gap(fullbg_img, bg_img)
		# 方法2
		gap = self.get_gap(image.open(full_bg_img), image.open(bg_img))
		print('缺口位置', gap)

		track = self.get_track(gap-self.BORDER)
		print('滑动滑块')
		print(track)

		# # 点按呼出缺口
		# slider = self.get_slider()
		# # 拖动滑块到缺口处
		# self.move_to_gap(slider, track)

if __name__ == '__main__':
	print('开始验证')
	crack = Crack(u'中国移动')
	crack.crack()
	print('验证成功')
