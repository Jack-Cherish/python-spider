#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = 'ZYSzys'

import requests
import re
import os
import sys
import urllib
import getpass
from lxml import etree
from PIL import Image
from imp import reload
from bs4 import BeautifulSoup


class Who:
    def __init__(self, user, pswd):
        self.user = user
        self.pswd = pswd


class Tool:
    rma = re.compile('<a href=.*?>|</a>')
    rmtb = re.compile('<br />|</br>|<br>')
    rmtr = re.compile('<td>|</td>|<tr>|</tr>|<tr class="alt">|<tr class="datelisthead">')
    rmtime1 = re.compile('<td align="Center" width="7%">.*?</td>')
    rmtime2 = re.compile('<td class="noprint" align="Center".*?>.*?</td>')

    def replace(self, x):
        x = re.sub(self.rma, '   ', x)
        x = re.sub(self.rmtb, '---', x)
        x = re.sub(self.rmtr, '  ', x)
        x = re.sub(self.rmtime1, '\n', x)
        x = re.sub(self.rmtime2, '', x)
        return x.strip()


def Getgrade(response):
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find(id="Datagrid1").findAll("tr")
    Grades = []
    keys = []
    tds = trs[0].findAll("td")
    tds = tds[:2] + tds[3:5] + tds[6:9]
    for td in tds:
        keys.append(td.string)
    for tr in trs[1:]:
        tds = tr.findAll("td")
        tds = tds[:2] + tds[3:5] + tds[6:9]
        values = []
        for td in tds:
            values.append(td.string)
        one = dict((key, value) for key, value in zip(keys, values))
        Grades.append(one)
    return Grades


def Getgradetestresults(trs):
    results = []
    k = []
    for td in trs[0].xpath('.//td/text()'):
        k.append(td)
    trs = trs[1:]
    for tr in trs:
        tds = tr.xpath('.//td/text()')
        v = []
        for td in tds:
            v.append(td)
        one = dict((i, j) for i, j in zip(k, v))
        results.append(one)
    return results


class University:
    def __init__(self, student, baseurl):
        reload(sys)
        self.student = student
        self.baseurl = baseurl
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

    def Login(self):
        url = self.baseurl+'/default2.aspx'
        res = self.session.get(url)
        cont = res.content
        selector = etree.HTML(cont)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
        imgurl = self.baseurl + '/CheckCode.aspx'
        imgres = self.session.get(imgurl, stream=True)
        img = imgres.content
        with open('code.jpg', 'wb') as f:
            f.write(img)
        jpg = Image.open('{}/code.jpg'.format(os.getcwd()))
        jpg.show()
        jpg.close
        code = input('输入验证码：')
        RadioButtonList1 = u"学生"
        data = {
            "__VIEWSTATE": __VIEWSTATE,
            "txtUserName": self.student.user,
            "TextBox1": self.student.pswd,
            "TextBox2": self.student.pswd,
            "txtSecretCode": code,
            "RadioButtonList1": RadioButtonList1,
            "Button1": "",
            "lbLanguage": ""
        }
        loginres = self.session.post(url, data=data)
        logcont = loginres.text
        pattern = re.compile(
            '<form name="Form1".*?action=(.*?) id="Form1">', re.S)
        res = re.findall(pattern, logcont)
        try:
            if res[0][17:29] == self.student.user:
                print('Login succeed!')
        except:
            print('Login failed! Maybe Wrong password ! ! !')
            return
        pattern = re.compile('<span id="xhxm">(.*?)</span>')
        xhxm = re.findall(pattern, logcont)
        name = xhxm[0].replace('同学', '')
        self.student.urlname = urllib.parse.quote_plus(str(name))
        return True

    def GetClass(self):
        self.session.headers['Referer'] = self.baseurl + \
            '/xs_main.aspx?xh=' + self.student.user
        kburl = self.baseurl + '/xskbcx.aspx?xh='+self.student.user + \
            '&xm='+self.student.urlname+'&gnmkdm=N121603'
        kbresponse = self.session.get(kburl)
        kbcont = kbresponse.text
        pattern = re.compile('<td.*?align="Center".*?>(.*?)</td>', re.S)
        contents = re.findall(pattern, kbcont)
        tool = Tool()
        f = open(os.getcwd()+'/zhengfang.txt', 'w')
        f.write(u'本学期课表:'+'\n')
        cnt = 1
        l = [u'周一', u'周二', u'周三', u'周四', u'周五', u'周六', u'周日']
        for day in l:
            for i in contents:
                if u'星期' in i:
                    continue
                elif u'第' in i:
                    if day in i:
                        con = tool.replace(i)
                        f.write(str(cnt)+':\t'+con+'\n')
                        cnt += 1
                else:
                    continue
            f.write('\n')
        f.close()
        print('Download class succeed!')

    def GetGrade(self):
        self.session.headers['Referer'] = self.baseurl + \
            '/xs_main.aspx?xh=' + self.student.user
        gradeurl = self.baseurl + '/xscjcx.aspx?xh='+self.student.user + \
            '&xm='+self.student.urlname+'&gnmkdm=N121605'
        graderesponse = self.session.get(gradeurl)
        gradecont = graderesponse.content
        soup = BeautifulSoup(gradecont, 'lxml')
        __VIEWSTATE = soup.findAll(name="input")[2]["value"]
        self.session.headers['Referer'] = gradeurl
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": __VIEWSTATE,
            "hidLanguage": "",
            "ddlXN": "",
            "ddlXQ": "",
            "ddl_kcxz": "",
            "btn_zcj": u'历年成绩'
        }
        grares = self.session.post(gradeurl, data=data)
        grades = Getgrade(grares)
        totup = 0
        totdown = 0
        f = open(os.getcwd()+'/zhengfang.txt', 'a+')
        f.write('\n\n\n'+u'历年成绩:'+'\n')
        for i in grades[0]:
            f.write('%-13s\t' % i)
        f.write('\n')
        for each in grades:
            for one in each:
                f.write('%-15s\t' % each[one])
            f.write('\n')
            totup = totup + float(each[u'绩点']) * float(each[u'学分'])
            totdown = totdown + float(each[u'学分'])
        f.write('\n'+u'平均绩点: '+'%.2f\t\t\t' % (totup / totdown) +
                u'总学分绩点: '+'%.2f\t\t\t' % totup + u'总学分: '+'%.2f\n' % totdown)
        f.close()
        print('Download grade succeed!')

    def GradeTestResults(self):
        self.session.headers['Referer'] = self.baseurl + \
            '/xs_main.aspx?xh=' + self.student.user
        gtrurl = self.baseurl + '/xsdjkscx.aspx?xh='+self.student.user + \
            '&xm='+self.student.urlname+'&gnmkdm=N121606'
        gtrresponse = self.session.get(gtrurl)
        gtrcontent = gtrresponse.text
        gtrhtml = etree.HTML(gtrcontent)
        trs = gtrhtml.xpath('//table[@class="datelist"]/tr')
        f = open(os.getcwd()+'/zhengfang.txt', 'a+')
        f.write('\n\n\n'+u'等级考试成绩:'+'\n')
        results = Getgradetestresults(trs)
        for one in results[0]:
            f.write('%-10s\t' % one)
        f.write('\n')
        for each in results:
            for one in each:
                f.write('%-10s\t' % each[one])
            f.write('\n')
        f.close()
        print('Download grade test results succeed!')


if __name__ == "__main__":
    url = input("学校教务网站(如http://115.236.84.162)：")
    user = input("学号：")
    pswd = getpass.getpass("密码：")
    who = Who(user, pswd)
    univ = University(who, url)
    if univ.Login():
        univ.GetClass()
        univ.GetGrade()
        univ.GradeTestResults()
