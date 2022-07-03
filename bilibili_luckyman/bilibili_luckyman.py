# -*- coding:utf-8 -*-
import requests
import json
import re
import random
import time

def get_dynamic_id(url):
    dynamic_id = re.findall(r'\d+', url)
    return dynamic_id

def get_data(detail_url, params):
    req = requests.get(url = detail_url, params = params)
    req_text = json.loads(req.text)
    data = req_text['data']
    offset = data['offset']
    items = data['items']
    return offset, items

def get_uses(dynamic_id):
    detail_url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/detail/forward"
    params = {'id': dynamic_id}

    offset, items = get_data(detail_url, params)

    all_user_name = []
    all_user_text = []
    all_user_mid = []

    while offset != "":
        for item in items:
            name = item['user']['name']
            all_user_name.append(name)
            mid = item['user']['mid']
            all_user_mid.append(mid)
            text = item['desc']['text']
            all_user_text.append(text)

        params = {
            'id': dynamic_id,
            'offset': offset
        }
        offset, items = get_data(detail_url, params)

    return all_user_name, all_user_mid, all_user_text

def get_lucky_man(num, lucky_num):

    tmp = [i for i in range(0, num)]
    random.shuffle(tmp)
    top30_shuffle_id = tmp[:lucky_num]
    return top30_shuffle_id

def get_local_time():
    localtime = "[" + str(time.strftime('%H:%M:%S',time.localtime(time.time()))) + "]"
    return localtime

if __name__ == "__main__":
    print ("+----------------------------------------+")
    print ("      |动态转发抽奖助手 by Jack Cui|")
    print ("+----------------------------------------+")
    # 动态链接，修改为你自己的动态
    url = "https://t.bilibili.com/675922191916728342"
    print (get_local_time() + " 正在获取转发数据中......")

    awards = [
        "动手深度学习",
        "机器学习公式详解",
        "Easy RL 强化学习教程",
        "数学之美",
        "浪潮之巅 第四版",
        "C Primer Plus（第6版）中文版"
    ] * 5

    # 设置随机数种子，保证随机数固定，这里种子数设为转发数+评论数+点赞数
    random.seed(1462 + 213 + 399)
    random.shuffle(awards)

    dynamic_id = get_dynamic_id(url)
    all_user_name, all_user_mid, all_user_text = get_uses(dynamic_id)

    top30_shuffle_id = get_lucky_man(len(all_user_name), 30)
    print (get_local_time() + " 中奖用户信息：\n")
    for idx, id_ in enumerate(top30_shuffle_id):
        print("用户名：{}".format(all_user_name[id_]))
        print("用户主页：{}".format("https://space.bilibili.com/" + str(all_user_mid[id_])))
        print("转发内容：{}".format(all_user_text[id_]))
        print("获得奖品：{}".format(awards[idx]))
        print("*" * 50)
