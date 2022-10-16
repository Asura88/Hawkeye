# Hawkeye
Hawkeye鹰眼web监测｜[重保小助手]页面违规检测与重要页面持续监控

```
optional arguments:
  -h, --help  show this help message and exit
  -monitor    对关键页面进行监控
  --time 60   监控时间间隔，默认60秒
  -check      对目标网站进行爬虫并检测违规信息
  --deep 5    爬虫的深度，默认5
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

## 其他介绍
https://mp.weixin.qq.com/s/ppAoFj-fMb78tJIc7Ggz4A
