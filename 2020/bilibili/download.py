# -*-coding:utf-8 -*-
# Website: https://cuijiahua.com
# Author: Jack Cui
# Date: 2020.07.22
import requests
import json
import re
import json
import math
import xml2ass
import time
from contextlib import closing

from bs4 import BeautifulSoup

import os
from win32com.client import Dispatch

def addTasktoXunlei(down_url):
    flag = False
    o = Dispatch('ThunderAgent.Agent64.1')
    try:
        o.AddTask(down_url, "", "", "", "", -1, 0, 5)
        o.CommitTasks()
        flag = True
    except Exception:
        print(Exception.message)
        print(" AddTask is fail!")
    return flag

def get_download_url(arcurl):
    # 微信搜索 JackCui-AI 关注公众号，后台回复「B 站」获取视频解析地址
    jiexi_url = 'xxx'
    payload = {'url': arcurl}
    jiexi_req = requests.get(jiexi_url, params=payload)
    jiexi_bf = BeautifulSoup(jiexi_req.text)
    jiexi_dn_url = jiexi_bf.iframe.get('src')
    dn_req = requests.get(jiexi_dn_url)
    dn_bf = BeautifulSoup(dn_req.text)
    video_script = dn_bf.find('script',src = None)
    DPlayer = str(video_script.string)
    download_url = re.findall('\'(http[s]?:(?:[a-zA-Z]|[0-9]|[$-_@.&~+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\'', DPlayer)[0]
    download_url = download_url.replace('\\', '')
    return download_url

space_url = 'https://space.bilibili.com/280793434'
search_url = 'https://api.bilibili.com/x/space/arc/search'
mid = space_url.split('/')[-1]
sess = requests.Session()
search_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'application/json, text/plain, */*'}

# 获取视频个数
ps = 1
pn = 1
search_params = {'mid': mid,
                 'ps': ps,
                 'tid': 0,
                 'pn': pn}
req = sess.get(url=search_url, headers=search_headers, params=search_params, verify=False)
info = json.loads(req.text)
video_count = info['data']['page']['count']

ps = 10
page = math.ceil(video_count/ps)
videos_list = []
for pn in range(1, page+1):
    search_params = {'mid': mid,
                     'ps': ps,
                     'tid': 0,
                     'pn': pn}
    req = sess.get(url=search_url, headers=search_headers, params=search_params, verify=False)
    info = json.loads(req.text)
    vlist = info['data']['list']['vlist']
    for video in vlist:
        title = video['title']
        bvid = video['bvid']
        vurl = 'https://www.bilibili.com/video/' + bvid
        videos_list.append([title, vurl])
print('共 %d 个视频' % len(videos_list))
all_video = {}
# 下载前 10 个视频
for video in videos_list[:10]:
    download_url = get_download_url(video[1])
    print(video[0] + ':' + download_url)
    # 记录视频名字
    xunlei_video_name = download_url.split('?')[0].split('/')[-1]
    filename = video[0]
    for c in u'´☆<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="❤" src="https://s.w.org/images/core/emoji/11.2.0/svg/2764.svg">◦\/:*?"<>| ':
        filename = filename.replace(c, '')
    save_video_name = filename + '.mp4'
    all_video[xunlei_video_name] = save_video_name

    addTasktoXunlei(download_url)
    # 弹幕下载
    danmu_name = filename + '.xml'
    danmu_ass = filename + '.ass'
    oid = download_url.split('/')[6]
    danmu_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid={}'.format(oid)
    danmu_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9'}
    with closing(sess.get(danmu_url, headers=danmu_header, stream=True, verify=False)) as response:  
        if response.status_code == 200:
            with open(danmu_name, 'wb') as file:
                for data in response.iter_content():
                    file.write(data)
                    file.flush()
        else:
            print('链接异常')
    time.sleep(0.5)
    xml2ass.Danmaku2ASS(danmu_name, danmu_ass, 1280, 720)
# 视频重命名
for key, item in all_video.items():
    while key not in os.listdir('./'):
        time.sleep(1)
    os.rename(key, item)
