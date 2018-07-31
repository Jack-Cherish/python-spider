# -*- coding:utf-8 -*-
import requests
import json
import os
from contextlib import closing

"""
从https://unsplash.com/爬取壁纸代码，使用时我是开启了代理软件
国内网速貌似有些限制，很慢
    2018-07-31
"""

# 本地保存图片根路径（请确保根路径存在）
save_path = 'G:/pythonlearn'
dir_path=save_path+'/'+'unsplash-image'
if not os.path.exists(dir_path):
    os.path.join(save_path, 'unsplash-image')
    os.mkdir(dir_path)
n=10
#n建议从第2页开始，因为第一页的per_page可能是1，不是12
while n>2:
    print('当前爬取第'+str(n)+'次加载图片（本次共12张）')
    url='https://unsplash.com/napi/photos?page='+str(n)+'&per_page=12&order_by=latest'
    req=requests.get(url=url)
    html=json.loads(req.text)
    for each in html:
        downloadurl=each['links']["download"]
        jpgrep=requests.get(url=downloadurl)
        with closing(requests.get(url=downloadurl, stream=True)) as r:
            with open(dir_path+'/'+each['id']+'.jpg', 'ab+') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
    n=n-1