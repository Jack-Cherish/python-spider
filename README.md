# Python Spider

* 贵有恒，何必三更起五更睡；最无益，只怕一日暴十寒。
* Python3爬虫实战：实战源码+博客讲解
* [个人网站](http://cuijiahua.com "悬停显示")
* [CSDN博客](http://blog.csdn.net/c406495762 "悬停显示")
* [CSDN爬虫专栏](http://blog.csdn.net/column/details/15321.html "悬停显示")<br>
* 学习交流群【328127489】<a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=e70f3fcff3761450fda9b43eadc1910dac308a962ef9e3e87941cd2c681c4bb4"><img border="0" src="https://github.com/Jack-Cherish/Pictures/blob/master/qqgroup.png" alt="Coder" title="Coder"></a><br>
* 分享技术，乐享生活：Jack Cui公众号每周五推送“程序员欢乐送”系列资讯类文章，欢迎您的关注！
<div align="center"><img border="0" src="https://ww2.sinaimg.cn/large/0072Lfvtly1fxuhd2t2jqj309k09kglk.jpg" alt="Coder" title="gongzhonghao" with="200" height="200"></div>

## 声明

* 代码、教程均为Jack Cui本人原创，且仅限于学习交流，请勿用于任何商业用途！

### 文章首发声明

* 文章在自己的个人网站首发，其他平台文章均属转发，如想获得最新更新进展，欢迎关注我的个人网站：http://cuijiahua.com/

## 目录

* [爬虫小工具](#爬虫小工具)
    * [文件下载小助手](https://github.com/Jack-Cherish/python-spider/blob/master/downloader.py "悬停显示")
* [爬虫实战](#爬虫实战)
    * [笔趣看小说下载](https://github.com/Jack-Cherish/python-spider/blob/master/biqukan.py "悬停显示")
    * [VIP视频下载](https://github.com/Jack-Cherish/python-spider/tree/master/video_downloader "悬停显示")
    * [百度文库文章下载_rev1](https://github.com/Jack-Cherish/python-spider/blob/master/baiduwenku.py "悬停显示")
    * [百度文库文章下载_rev2](https://github.com/Jack-Cherish/python-spider/blob/master/baiduwenku_pro_1.py "悬停显示")
    * [《帅啊》网帅哥图片下载](https://github.com/Jack-Cherish/python-spider/blob/master/shuaia.py "悬停显示")
    * [构建代理IP池](https://github.com/Jack-Cherish/python-spider/blob/master/daili.py "悬停显示")
    * [《火影忍者》漫画下载](https://github.com/Jack-Cherish/python-spider/tree/master/cartoon "悬停显示")
    * [财务报表下载小助手](https://github.com/Jack-Cherish/python-spider/blob/master/financical.py "悬停显示")
    * [一小时入门网络爬虫](https://github.com/Jack-Cherish/python-spider/tree/master/one_hour_spider "悬停显示")
    * [抖音App视频下载_rev1](https://github.com/Jack-Cherish/python-spider/blob/master/douyin.py "悬停显示")
    * [抖音App视频下载_rev2](https://github.com/Jack-Cherish/python-spider/blob/master/douyin_pro.py "悬停显示")
    * [抖音App视频下载_rev3](https://github.com/Jack-Cherish/python-spider/tree/master/douyin "悬停显示")
    * [GEETEST验证码破解](https://github.com/Jack-Cherish/python-spider/blob/master/geetest.py "悬停显示")
    * [12306抢票小助手](https://github.com/Jack-Cherish/python-spider/blob/master/12306.py "悬停显示")
    * [百万英雄答题辅助系统](https://github.com/Jack-Cherish/python-spider/tree/master/baiwan "悬停显示")   
    * [网易云音乐批量下载](https://github.com/Jack-Cherish/python-spider/tree/master/Netease "悬停显示")
    * [B站视频和弹幕批量下载](https://github.com/Jack-Cherish/python-spider/tree/master/bilibili "悬停显示")
    * [京东商品晒单图下载](https://github.com/Jack-Cherish/python-spider/tree/master/dingdong "悬停显示")
    * [正方教务管理系统爬虫](https://github.com/Jack-Cherish/python-spider/tree/master/zhengfang_system_spider "悬停显示")
* [其它](#其它)

## 爬虫小工具

* downloader.py:文件下载小助手

	一个可以用于下载图片、视频、文件的小工具，有下载进度显示功能。稍加修改即可添加到自己的爬虫中。
	
	动态示意图：
	
	![image](https://raw.githubusercontent.com/Jack-Cherish/Pictures/master/9.gif)

## 爬虫实战
 
 * biqukan.py:《笔趣看》盗版小说网站，爬取小说工具

	第三方依赖库安装：

		pip3 install beautifulsoup4

	使用方法：

		python biqukan.py

 * video_downloader：爱奇艺等主流视频网站的VIP视频破解助手(暂只支持PC和手机在线观看VIP视频！)

	感谢Python3二维码生成器作者：https://github.com/sylnsfar/qrcode
	
	编译好的软件下载连接：https://pan.baidu.com/s/1bqSTNJL 密码:p8bs
	
	解压密码：`cuijiahua.com`
	
	无需Python3环境，在Windows下，解压即用！[软件使用方法](http://blog.csdn.net/c406495762/article/details/71334633 "悬停显示")
	
	源码可查看`video_downloader`，运行源码需要搭建Python3环境，并安装相应第三方依赖库：
	
	在`video_downloader`文件夹下，安装第三方依赖库：

		pip3 install -r requirements.txt

	使用方法：
	
		python movie_downloader.py

	运行环境：
	
		Windows, Python3
		
		Linux, Python3
		
		Mac, Python3

 * baiduwenku.py: 百度文库word文章爬取
	
	原理说明：http://blog.csdn.net/c406495762/article/details/72331737
	
	代码不完善，没有进行打包，不具通用性，纯属娱乐，以后有时间会完善。
	
 * shuaia.py: 爬取《帅啊》网，帅哥图片

	《帅啊》网URL：http://www.shuaia.net/index.html

	原理说明：http://blog.csdn.net/c406495762/article/details/72597755
	
	第三方依赖库安装：
	
		pip3 install requests beautifulsoup4
		
 * daili.py: 构建代理IP池

	原理说明：http://blog.csdn.net/c406495762/article/details/72793480
	
	
 * carton: 使用Scrapy爬取《火影忍者》漫画

	代码可以爬取整个《火影忍者》漫画所有章节的内容，保存到本地。更改地址，可以爬取其他漫画。保存地址可以在settings.py中修改。
	
	动漫网站：http://comic.kukudm.com/
	
	原理说明：http://blog.csdn.net/c406495762/article/details/72858983
	
 * hero.py: 《王者荣耀》推荐出装查询小助手

	网页爬取已经会了，想过爬取手机APP里的内容吗？
	
	原理说明：http://blog.csdn.net/c406495762/article/details/76850843
	
 * financical.py: 财务报表下载小助手

	爬取的数据存入数据库会吗？《跟股神巴菲特学习炒股之财务报表入库(MySQL)》也许能给你一些思路。
	
	原理说明：http://blog.csdn.net/c406495762/article/details/77801899
	
	动态示意图：
	
	![image](https://raw.githubusercontent.com/Jack-Cherish/Pictures/master/10.gif)
	
 * one_hour_spider:一小时入门Python3网络爬虫。

	原理说明:
	
	 * 知乎：https://zhuanlan.zhihu.com/p/29809609
	 * CSDN：http://blog.csdn.net/c406495762/article/details/78123502
	
	本次实战内容有：
	
	 * 网络小说下载(静态网站)-biqukan
	 * 优美壁纸下载(动态网站)-unsplash
	 * 爱奇艺VIP视频下载
	 
 * douyin.py:抖音App视频下载
 
	抖音App的视频下载，就是普通的App爬取。

	原理说明:
	
	 * 个人网站：http://cuijiahua.com/blog/2018/03/spider-5.html
	
 * douyin_pro:抖音App视频下载（升级版）
 
	抖音App的视频下载，添加视频解析网站，支持无水印视频下载，使用第三方平台解析。

	原理说明:
	
	 * 个人网站：http://cuijiahua.com/blog/2018/03/spider-5.html
	 
 * douyin:抖音App视频下载（升级版2）
 
	抖音App的视频下载，添加视频解析网站，支持无水印视频下载，通过url解析，无需第三方平台。
	
	原理说明:
	
	 * 个人网站：http://cuijiahua.com/blog/2018/03/spider-5.html
	 
	动态示意图：
	
	![image](https://github.com/Jack-Cherish/Pictures/blob/master/14.gif)
	
 * geetest.py:GEETEST验证码破解
 
 	爬虫最大的敌人之一是什么？没错，验证码！Geetest作为提供验证码服务的行家，市场占有率还是蛮高的。遇到Geetest提供的滑动验证码怎么破？授人予鱼不如授人予渔，接下来就为大家呈现本教程的精彩内容。
 
 	原理说明:
	
	 * 个人网站：http://www.cuijiahua.com/blog/2017/11/spider_2_geetest.html
	 
	动态示意图：
	
	![image](https://github.com/Jack-Cherish/Pictures/blob/master/spider_2_1.gif)
	
 * 12306.py:用Python抢火车票简单代码
 
	可以自己慢慢丰富，蛮简单，有爬虫基础很好操作，没有原理说明。
	
 * baiwan:百万英雄辅助答题
 
	效果图：
	
	![image](https://github.com/Jack-Cherish/Pictures/blob/master/11.gif)
	
	原理说明：
	
	* 个人网站：http://cuijiahua.com/blog/2018/01/spider_3.html
	
  	功能介绍：
	
	服务器端，使用Python（baiwan.py）通过抓包获得的接口获取答题数据，解析之后通过百度知道搜索接口匹配答案，将最终匹配的结果写入文件（file.txt)。
	
	手机抓包不会的朋友，可以看下我的早期[手机APP抓包教程](http://blog.csdn.net/c406495762/article/details/76850843 "悬停显示")。
	
	Node.js（app.js）每隔1s读取一次file.txt文件，并将读取结果通过socket.io推送给客户端（index.html）。
	
	亲测答题延时在3s左右。
	
	声明：没做过后端和前端，花了一天时间，现学现卖弄好的，javascript也是现看现用，百度的程序，调试调试而已。可能有很多用法比较low的地方，用法不对，请勿见怪，有大牛感兴趣，可以自行完善。

 * Netease:根据歌单下载网易云音乐
 	
	效果图：
	
	![image](https://github.com/Jack-Cherish/Pictures/blob/master/13.gif)
	
	原理说明：
	
	暂无
	
	功能介绍：
	
	根据music_list.txt文件里的歌单的信息下载网易云音乐，将自己喜欢的音乐进行批量下载。

 * bilibili：B站视频和弹幕批量下载
 	
	原理说明：
	
	暂无
	
	使用说明：
	
        python bilibili.py -d 猫 -k 猫 -p 10

        三个参数：
        -d	保存视频的文件夹名
        -k	B站搜索的关键字
        -p	下载搜索结果前多少页
	
 * jingdong：京东商品晒单图下载
 
 	效果图：
	
	![image](https://github.com/Jack-Cherish/Pictures/blob/master/jd.gif)
 	
	原理说明：
	
	暂无
	
	使用说明：
	
        python jd.py -k 芒果
	
         三个参数：
        -d	保存图片的路径，默认为fd.py文件所在文件夹
        -k	搜索关键词
        -n  	下载商品的晒单图个数，即n个商店的晒单图

 * zhengfang_system_spider：对正方教务管理系统个人课表，学生成绩，绩点等简单爬取
 
 	效果图：
	
	![image](/zhengfang_system_spider/screenshot/zf.png)
 	
	原理说明：
	
	暂无
	
	使用说明：
	
        cd zhengfang_system_spider
        pip install -r requirements.txt
        python spider.py

## 其它

 * 欢迎 Pull requests，感谢贡献。
