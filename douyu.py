# -*- coding: UTF-8 -*-
import time, sys, pymysql
from danmu import DanMuClient

def pp(msg):
	print(msg.encode(sys.stdin.encoding, 'ignore').decode(sys.stdin.encoding))

@dmc.danmu
def danmu_fn(msg):
	uid = msg['uid']
	name = msg['NickName']
	text = msg['Content']
	print(text)
	sql = """
	INSERT INTO danmu (`用户ID`,`用户昵称`,`弹幕内容`) VALUES ('%s','%s','%s')""" % (uid, name, text)
	try:
		cursor.execute(sql)
		# 执行sql语句
		conn.commit()
	except:
		# 发生错误时回滚
		conn.rollback()
	

if __name__ == '__main__':
	dmc = DanMuClient('https://www.douyu.com/70537')
	if not dmc.isValid(): 
		print('Url not valid')
	#打开数据库连接:host-连接主机地址,port-端口号,user-用户名,passwd-用户密码,db-数据库名,charset-编码
	conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='meditation',db='douyu',charset='utf8')
	#使用cursor()方法获取操作游标
	cursor = conn.cursor()  

	dmc.start(blockThread = True)

	# 关闭数据库连接
	cursor.close()  
	conn.close()


# pp('[%s] %s' % (msg['NickName'], msg['Content']))
# result = nlp.tag(msg['Content'])
# pp(msg['Content'])
# print(result[0]['word'])

# @dmc.gift
# def gift_fn(msg):
#     pp('[%s] sent a gift!' % msg['NickName'])

# @dmc.other
# def other_fn(msg):
#     pp('Other message received')

