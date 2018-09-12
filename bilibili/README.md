## 功能

下载B站视频和弹幕，将xml原生弹幕转换为ass弹幕文件，支持plotplayer等播放器的弹幕播放。

## 作者

* Website: [http://cuijiahua.com](http://cuijiahua.com "悬停显示")
* Author: Jack Cui
* Date: 2018.6.12

## 更新

* 2018.09.12：添加FFmpeg分段视频合并

## 使用说明

FFmpeg下载，并配置环境变量。http://ffmpeg.org/

	python bilibili.py -d 猫 -k 猫 -p 10

	三个参数：
	-d	保存视频的文件夹名
	-k	B站搜索的关键字
	-p	下载搜索结果前多少页
