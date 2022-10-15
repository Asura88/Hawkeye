import re
import time

import pytz
import datetime
import argparse
from queue import Queue
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class Hawkeye:

    def __init__(self):
        self.url_length_dict = {}  # 重要页面标题和长度
        self.spidered_list = []  # 已经作为入口爬过的url，避免重复
        self.result_url_list = []  # 爬取的url
        self.checked_url_list = []  # 本轮已经检测过的url，避免重复
        self.q = Queue(0)  # 创建队列
        try:
            with open('urls.txt', 'r') as f:
                self.url_list = [i for i in f.read().split('\n') if i != '']
            with open('rules.txt', 'r') as f:
                self.rule_list = [i for i in f.read().split('\n') if i != '']
        except:
            print('{}'.format(self.color('[error]请确保urls.txt（目标网站/页面的链接）和rules.txt（规则文件）位于本目录下', 'red')))
            exit()
        self.blacklist1 = ['#', '##', '###', '####', 'None', 'javascript:', 'javascript:void(0)']
        self.blacklist2 = ['.gif', '.ico', '.jpg', '.png', '.bmp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.tif', '.rar', '.zip', '.tar', '.gz']
        self.user_agent = {'pc': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36', 'baidu': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)', 'google': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', '360': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36; 360Spider',
                           'bing': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)', 'sm': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 YisouSpider/5.0 Safari/537.36', 'sogou': 'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'}

    # 简单队列
    def queue(self, MaxDeep):
        for url in self.url_list:
            self.q.put(url)
        for i in range(MaxDeep):
            if not self.q.empty():
                self.spider(self.q.get())
            else:
                break

    # 初始化-重要页面标题和长度
    def init_get_index(self):
        for url in self.url_list:
            res = self.get_page(url)
            if res[2] == '无法访问':
                length = 0
                title = res[1]
            else:
                length = len(res[2])
                title = res[1]
            self.url_length_dict[url] = (length, title)

    # 无头浏览器访问web，支持渲染
    def get_page(self, url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.new_context(user_agent='Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)')
                page = browser.new_page()
                page.goto(url, )
                title = page.title()
                content = page.content()
                browser.close()
            return url, title, content
        except:
            return url, '无法访问', '无法访问'

    # 重要页面监控
    def monitor(self):
        for url in self.url_list:
            data = self.get_page(url)
            url = data[0]
            title = data[1]
            content = data[2]
            now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
            if title == '无法访问' and content == '无法访问':
                res = '[{}]{}|{}|无法访问'.format(now, url, title)
                print('[{}]{}|{}|{}'.format(self.color(now, 'gray'), self.color(url, 'blue'), self.color(title, 'gray'), self.color('无法访问', 'yellow')))
            else:
                if len(content) == self.url_length_dict[url][0]:
                    if title == self.url_length_dict[url][1]:
                        res = '[{}]{}|{}|页面正常'.format(now, url, title)
                        print('[{}]{}|{}|{}'.format(self.color(now, 'gray'), self.color(url, 'blue'), self.color(title, 'gray'), self.color('页面正常', 'green')))
                    else:
                        res = '[{}]{}|{}|标题发生变化：{}'.format(now, url, title, self.url_length_dict[url][1])
                        print('[{}]{}|{}|{}：{}'.format(self.color(now, 'gray'), self.color(url, 'blue'), self.color(title, 'gray'), self.color('标题发生变化', 'red'), self.color(self.url_length_dict[url][1], 'red')))
                else:
                    res = '[{}]{}|{}|长度发生变化：{}'.format(now, url, title, self.url_length_dict[url][0] - len(content))
                    print('[{}]{}|{}|{}：{}'.format(self.color(now, 'gray'), self.color(url, 'blue'), self.color(title, 'gray'), self.color('长度发生变化', 'red'), self.color(self.url_length_dict[url][0] - len(content), 'red')))
            with open('重要页面监控日志_{}.txt'.format(str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y_%m_%d'))), 'a') as f:
                f.write(res + '\n')

    # 暗链、敏感词检测
    def check(self, MaxDeep):
        self.queue(MaxDeep)
        for url in self.result_url_list:
            if url not in self.checked_url_list:
                res = self.re_rule(self.get_page(url))
                if res != '':
                    with open('暗链敏感词命中.txt', 'a') as f:
                        f.write(res + '\n')

    # 特征匹配
    def re_rule(self, data):
        url = data[0]
        content = data[2]
        hit_rule_list = []
        now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
        for rule in self.rule_list:
            if not re.findall(rule, content, re.I | re.S | re.M):
                pass
            else:
                hit_rule_list.append(rule)
        if len(hit_rule_list) != 0:
            res = 'URL:{}\n时间:{}\n命中:{}\n{}'.format(url, now, str(hit_rule_list), '-' * 50)
            print('[{}]{}|{}|{}'.format(self.color(now, 'gray'), self.color('敏感词', 'red'), self.color(url, 'blue'), str(self.color(hit_rule_list, 'yellow'))))
        else:
            res = ''
            print('[{}]{}|{}'.format(self.color(now, 'gray'), self.color(url, 'blue'), self.color('未检出违规', 'green')))
        return res

    # 获取base url
    def get_base_url(self, url):
        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc + '/'
        return base_url

    # 爬虫处理
    def deal_url(self, base_url, tmp_url):
        if tmp_url not in self.blacklist1 and tmp_url[4:] not in self.blacklist2 and tmp_url[5:] not in self.blacklist2:
            if (tmp_url[0:7] == 'http://' or tmp_url[0:8] == 'https://') and base_url in tmp_url and tmp_url not in self.result_url_list:  # 判断是否未本站链接
                self.result_url_list.append(tmp_url)
                if tmp_url not in self.spidered_list:
                    self.q.put(tmp_url)
            elif tmp_url[0:7] != 'http://' and tmp_url[0:8] != 'https://' and len(tmp_url) != 0:
                if tmp_url[0] == '/':
                    if (base_url + tmp_url[1:]) not in self.result_url_list:
                        self.result_url_list.append(base_url + tmp_url[1:])
                    if (base_url + tmp_url[1:]) not in self.spidered_list:
                        self.q.put(base_url + tmp_url[1:])
                else:
                    if (base_url + tmp_url) not in self.result_url_list:
                        self.result_url_list.append(base_url + tmp_url)
                    if (base_url + tmp_url) not in self.spidered_list:
                        self.q.put(base_url + tmp_url)
            else:
                pass

    # 爬虫
    def spider(self, url):
        base_url = self.get_base_url(url)
        data = self.get_page(url)
        res = data[2]
        self.re_rule(data)  # 爬虫返回的页面先做一次检测，减少重复请求
        self.checked_url_list.append(url)
        self.spidered_list.append(url)
        if res != '无法访问':
            soup = BeautifulSoup(res.encode('utf-8'), 'html.parser')
            for href in soup.find_all('a'):
                if href.get('href') is not None:
                    tmp_url = re.sub(r'#.*|\?.*', '', href.get('href'))
                    self.deal_url(base_url, tmp_url)
            for href in soup.find_all('script'):
                if href.get('src') is not None:
                    tmp_url = re.sub(r'#.*|\?.*', '', href.get('src'))
                    self.deal_url(base_url, tmp_url)

    # 花里胡哨，好看
    def color(self, str, m):
        if m == 'red':
            return "\033[1;31m{}\033[0m".format(str)
        elif m == 'green':
            return "\033[1;32m{}\033[0m".format(str)
        elif m == 'yellow':
            return "\033[1;33m{}\033[0m".format(str)
        elif m == 'blue':
            return "\033[1;34m{}\033[0m".format(str)
        elif m == 'gray':
            return "\033[1;37m{}\033[0m".format(str)
        else:
            return ''


# 入口
def run():
    banner = '''\033[1;34m
        
    ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗███████╗██╗   ██╗███████╗
    ██║  ██║██╔══██╗██║    ██║██║ ██╔╝██╔════╝╚██╗ ██╔╝██╔════╝
    ███████║███████║██║ █╗ ██║█████╔╝ █████╗   ╚████╔╝ █████╗  
    ██╔══██║██╔══██║██║███╗██║██╔═██╗ ██╔══╝    ╚██╔╝  ██╔══╝  
    ██║  ██║██║  ██║╚███╔███╔╝██║  ██╗███████╗   ██║   ███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝
                                                  --鹰眼web监测  
                                                
powered by 说书人｜公众号：台下言书|https://github.com/heikanet/Hawkeye\033[0m
    '''
    print(banner)
    main = Hawkeye()
    parser = argparse.ArgumentParser(description='[重保小助手]页面违规检测与重要页面持续监控')
    parser.add_argument("-monitor", action='store_true', help='对关键页面进行监控')
    parser.add_argument("--time", nargs=1, metavar='60', help='监控时间间隔，默认60秒')
    parser.add_argument("-check", action='store_true', help='对目标网站进行爬虫并检测违规信息')
    parser.add_argument("--deep", nargs=1, metavar='5', help='爬虫的深度，默认5')
    parser.add_argument("--ua", nargs=1, metavar='baidu', help='user-agent，可选(pc,baidu,google,360,bing,sm,sogou)，默认使用百度蜘蛛')

    args = parser.parse_args()
    if args.deep:
        MaxDeep = int(args.deep[0])
    else:
        MaxDeep = 5
    if args.time:
        interval = int(args.time[0])
    else:
        interval = 60

    if args.check:
        main.check(MaxDeep)
    elif args.monitor:
        print(main.color('获取所有页面原始信息中...请确保这个时候页面是正常的'.format(interval), 'yellow'))
        main.init_get_index()  # 初始化
        while True:
            main.monitor()
            now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
            print('[{}]{}'.format(main.color(now, 'gray'), main.color('休息{}秒...'.format(interval), 'yellow')))
            time.sleep(interval)
    else:
        print("\033[1;33m[tips] 使用 -h 参数查看使用说明\033[0m")


if __name__ == "__main__":
    run()
