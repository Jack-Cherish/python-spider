#-*- coding:UTF-8 -*-
import sys
import pymysql
import requests
import json
import re
from bs4 import BeautifulSoup

"""
类说明:获取财务数据

Author:
	Jack Cui
Blog:
	http://blog.csdn.net/c406495762
Zhihu:
	https://www.zhihu.com/people/Jack--Cui/
Modify:
	2017-08-31
"""
class FinancialData():

	def __init__(self):
		#服务器域名
		self.server = 'http://quotes.money.163.com/'
		self.cwnb = 'http://quotes.money.163.com/hkstock/cwsj_'
		#主要财务指标
		self.cwzb_dict = {'EPS':'基本每股收益','EPS_DILUTED':'摊薄每股收益','GROSS_MARGIN':'毛利率',
		'CAPITAL_ADEQUACY':'资本充足率','LOANS_DEPOSITS':'贷款回报率','ROTA':'总资产收益率',
		'ROEQUITY':'净资产收益率','CURRENT_RATIO':'流动比率','QUICK_RATIO':'速动比率',
		'ROLOANS':'存贷比','INVENTORY_TURNOVER':'存货周转率','GENERAL_ADMIN_RATIO':'管理费用比率',
		'TOTAL_ASSET2TURNOVER':'资产周转率','FINCOSTS_GROSSPROFIT':'财务费用比率','TURNOVER_CASH':'销售现金比率','YEAREND_DATE':'报表日期'}
		#利润表
		self.lrb_dict = {'TURNOVER':'总营收','OPER_PROFIT':'经营利润','PBT':'除税前利润',
		'NET_PROF':'净利润','EPS':'每股基本盈利','DPS':'每股派息',
		'INCOME_INTEREST':'利息收益','INCOME_NETTRADING':'交易收益','INCOME_NETFEE':'费用收益','YEAREND_DATE':'报表日期'}
		#资产负债表
		self.fzb_dict = {
			'FIX_ASS':'固定资产','CURR_ASS':'流动资产','CURR_LIAB':'流动负债',
			'INVENTORY':'存款','CASH':'现金及银行存结','OTHER_ASS':'其他资产',
			'TOTAL_ASS':'总资产','TOTAL_LIAB':'总负债','EQUITY':'股东权益',
			'CASH_SHORTTERMFUND':'库存现金及短期资金','DEPOSITS_FROM_CUSTOMER':'客户存款',
			'FINANCIALASSET_SALE':'可供出售之证券','LOAN_TO_BANK':'银行同业存款及贷款',
			'DERIVATIVES_LIABILITIES':'金融负债','DERIVATIVES_ASSET':'金融资产','YEAREND_DATE':'报表日期'}
		#现金流表
		self.llb_dict = {
			'CF_NCF_OPERACT':'经营活动产生的现金流','CF_INT_REC':'已收利息','CF_INT_PAID':'已付利息',
			'CF_INT_REC':'已收股息','CF_DIV_PAID':'已派股息','CF_INV':'投资活动产生现金流',
			'CF_FIN_ACT':'融资活动产生现金流','CF_BEG':'期初现金及现金等价物','CF_CHANGE_CSH':'现金及现金等价物净增加额',
			'CF_END':'期末现金及现金等价物','CF_EXCH':'汇率变动影响','YEAREND_DATE':'报表日期'}
		#总表
		self.table_dict = {'cwzb':self.cwzb_dict,'lrb':self.lrb_dict,'fzb':self.fzb_dict,'llb':self.llb_dict}
		#请求头
		self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.8',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'}
	
	"""
	函数说明:获取股票页面信息

	Author:
		Jack Cui
	Parameters:
	    url - 股票财务数据界面地址
	Returns:
	    name - 股票名
	    table_name_list - 财务报表名称
	    table_date_list - 财务报表年限
	    url_list - 财务报表查询连接
	Blog:
		http://blog.csdn.net/c406495762
	Zhihu:
		https://www.zhihu.com/people/Jack--Cui/
	Modify:
		2017-08-31
	"""
	def get_informations(self, url):
		req = requests.get(url = url, headers = self.headers)
		req.encoding = 'utf-8'
		html = req.text
		page_bf = BeautifulSoup(html, 'lxml')
		#股票名称，股票代码
		name = page_bf.find_all('span', class_ = 'name')[0].string
		# code = page_bf.find_all('span', class_ = 'code')[0].string
		# code = re.findall('\d+',code)[0]

		#存储各个表名的列表
		table_name_list = []
		table_date_list = []
		each_date_list = []
		url_list = []
		#表名和表时间
		table_name = page_bf.find_all('div', class_ = 'titlebar3')
		for each_table_name in table_name:
			#表名
			table_name_list.append(each_table_name.span.string)
			#表时间
			for each_table_date in each_table_name.div.find_all('select', id = re.compile('.+1$')):
				url_list.append(re.findall('(\w+)1',each_table_date.get('id'))[0])
				for each_date in each_table_date.find_all('option'):
					each_date_list.append(each_date.string)
				table_date_list.append(each_date_list)
				each_date_list = []
		return name,table_name_list,table_date_list,url_list

	"""
	函数说明:财务报表入库

	Author:
		Jack Cui
	Parameters:
	    name - 股票名
	    table_name_list - 财务报表名称
	    table_date_list - 财务报表年限
	    url_list - 财务报表查询连接
	Returns:
		无
	Blog:
		http://blog.csdn.net/c406495762
	Zhihu:
		https://www.zhihu.com/people/Jack--Cui/
	Modify:
		2017-08-31
	"""
	def insert_tables(self, name, table_name_list,table_date_list, url_list):
		#打开数据库连接:host-连接主机地址,port-端口号,user-用户名,passwd-用户密码,db-数据库名,charset-编码
		conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='yourpasswd',db='financialdata',charset='utf8')
		#使用cursor()方法获取操作游标
		cursor = conn.cursor()  
		#插入信息
		for i in range(len(table_name_list)):
			sys.stdout.write('    [正在下载       ]    %s' % table_name_list[i] + '\r')
			#获取数据地址
			url = self.server + 'hk/service/cwsj_service.php?symbol={}&start={}&end={}&type={}&unit=yuan'.format(code,table_date_list[i][-1],table_date_list[i][0],url_list[i])
			req_table = requests.get(url = url, headers = self.headers)
			table = req_table.json()
			nums = len(table)
			value_dict = {}
			for num in range(nums):
				sys.stdout.write('    [正在下载 %.2f%%]   ' % (((num+1) / nums)*100) + '\r')
				sys.stdout.flush()
				value_dict['股票名'] = name
				value_dict['股票代码'] = code
				for key, value in table[i].items():
					if key in self.table_dict[url_list[i]]:
						value_dict[self.table_dict[url_list[i]][key]] = value

				sql1 = """
				INSERT INTO %s (`股票名`,`股票代码`,`报表日期`) VALUES ('%s','%s','%s')""" % (url_list[i],value_dict['股票名'],value_dict['股票代码'],value_dict['报表日期'])
				try:
					cursor.execute(sql1)
					# 执行sql语句
					conn.commit()
				except:
					# 发生错误时回滚
					conn.rollback()

				for key, value in value_dict.items():
					if key not in ['股票名','股票代码','报表日期']:
						sql2 = """
						UPDATE %s SET %s='%s' WHERE `股票名`='%s' AND `报表日期`='%s'""" % (url_list[i],key,value,value_dict['股票名'],value_dict['报表日期'])
						try:
							cursor.execute(sql2)
							# 执行sql语句
							conn.commit()
						except:
							# 发生错误时回滚
							conn.rollback()
				value_dict = {}
			print('    [下载完成 ')

		# 关闭数据库连接
		cursor.close()  
		conn.close()

if __name__ == '__main__':
	print('*' * 100)
	print('\t\t\t\t\t财务数据下载助手\n')
	print('作者:Jack-Cui\n')
	print('About Me:\n')
	print('  知乎:https://www.zhihu.com/people/Jack--Cui')
	print('  Blog:http://blog.csdn.net/c406495762')
	print('  Gihub:https://github.com/Jack-Cherish\n')
	print('*' * 100)
	fd = FinancialData()
	#上市股票地址
	code = input('请输入股票代码:')

	name,table_name_list,table_date_list,url_list = fd.get_informations(fd.cwnb + code + '.html')
	print('\n  %s:(%s)财务数据下载中！\n' % (name,code))
	fd.insert_tables(name,table_name_list,table_date_list,url_list)
	print('\n  %s:(%s)财务数据下载完成！' % (name,code))