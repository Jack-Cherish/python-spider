# ZhengFang_System_Spider
对正方教务管理系统的个人课表，个人学生成绩，绩点等简单爬取

## 依赖环境
python 3.6
### python库
http请求：requests，urllib  
数据提取：re，lxml，bs4  
存储相关：os，sys  
验证码处理：PIL  

## 下载安装
在终端输入如下命令：
```bash
git clone git@github.com:Jack-Cherish/python-spider.git
```

## 使用方法

### 安装依赖包
```bash
pip install -r requirements.txt
```

### 运行
在当前目录下输入：
```
cd zhengfang_system_spider
python spider.py
```
运行爬虫，按提示输入学校教务网，学号，密码，输入验证码  

![运行时](/zhengfang_system_spider/screenshot/spider.png)

稍等几秒钟，当前ZhengFang_System_Spider文件夹下就会生成zhengfang.txt  
个人课表，成绩绩点均已保存到该文本文件中

![结果](/zhengfang_system_spider/screenshot/zf.png)
