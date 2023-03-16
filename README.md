# Hawkeye
Hawkeye鹰眼web监测｜[重保小助手]｜网站违规检测｜暗链检测｜重要页面持续监控

<a href="https://github.com/heikanet/Hawkeye"><img alt="Release" src="https://img.shields.io/badge/python-3.x+-9cf"></a>
<a href="https://github.com/heikanet/Hawkeye"><img alt="Release" src="https://img.shields.io/badge/Hawkeye-2.0-ff69b4"></a>
<a href="https://github.com/heikanet/Hawkeye"><img alt="Release" src="https://img.shields.io/badge/LICENSE-GPL-important"></a>
![GitHub Repo stars](https://img.shields.io/github/stars/heikanet/Hawkeye?color=success)
![GitHub forks](https://img.shields.io/github/forks/heikanet/Hawkeye)
![GitHub all release](https://img.shields.io/github/downloads/heikanet/Hawkeye/total?color=blueviolet)  

## 使用指南
```
optional arguments:
  -h, --help  show this help message and exit
  -monitor    对关键页面进行监控
  --time 60   监控时间间隔，默认60秒
  --range 0   忽略x个字符内的变化，默认0个
  -check      对目标网站进行爬虫并检测违规信息
  --deep 5    爬虫的深度，默认5
  --work 5    爬虫的线程，默认1
  --ua baidu  user-agent，可选(pc,baidu,google,360,bing,sm,sogou)，默认使用百度蜘蛛
```

## 安装&使用
```
# 安装依赖包
pip install -r requirements.txt

# 下载和安装依赖的浏览器
playwright install --force chromium
playwright install --force chrome

# run
python3 Hawkeye.py -h
```
# log
- 2022-10-16
>  某次特殊行动值守期间的小需求，项目诞生。

- 2023-03-16
> 感谢[@moshe](https://github.com/moshe)反馈的一些小bug，已修复
> 简单重构了一下，违规检测改成异步+多线程模式


## 其他介绍
https://mp.weixin.qq.com/s/ppAoFj-fMb78tJIc7Ggz4A
