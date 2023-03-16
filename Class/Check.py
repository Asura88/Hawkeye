# python3
import re
import pytz
import datetime
from queue import Queue
from bs4 import BeautifulSoup
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from Class import Util


# 异步
def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class Check:

    def __init__(self):
        self.u = Util.Util()
        self.wait_url_check_queue = Queue(0)  # 等待检查的url队列
        self.wait_rule_check_queue = Queue(0)  # 等待识别的响应队列
        self.wait_check_url = []  # 防重复列表，等待检查的url
        self.spider_flag = False
        self.black_rule_list = ['^javascript:(.+?)$', '^none$', '^/?$', '^#?$', '(.+?)\.gif$', '(.+?)\.ico$', '(.+?)\.jpg$', '(.+?)\.png$', '(.+?)\.bmp$', '(.+?)\.pdf$', '(.+?)\.doc$', '(.+?)\.docx$', '(.+?)\.xls$', '(.+?)\.xlsx$', '(.+?)\.tif$', '(.+?)\.rar$', '(.+?)\.zip$', '(.+?)\.tar$', '(.+?)\.gz$']

    # 爬虫
    def __spider(self, page_res):
        result_list = []
        url = page_res[0]
        content = page_res[2]
        base_url = self.u.getBaseUrl(url)
        if content != '无法访问':
            soup = BeautifulSoup(content.encode('utf-8'), 'html.parser')
            for href in soup.find_all('a'):
                if href.get('href') is not None:
                    tmp_url = re.sub(r'#.*|\?.*', '', href.get('href'))
                    result = self.__dealUrl(base_url, tmp_url)
                    if result is not None:
                        result_list.append(result)
            for href in soup.find_all('script'):
                if href.get('src') is not None:
                    tmp_url = re.sub(r'#.*|\?.*', '', href.get('src'))
                    result = self.__dealUrl(base_url, tmp_url)
                    if result is not None:
                        result_list.append(result)
        return result_list

    # 爬虫处理
    def __dealUrl(self, base_url, tmp_url):
        for black_rule in self.black_rule_list:
            if re.findall(black_rule, tmp_url, re.I):
                return None
        if (tmp_url[0:7] == 'http://' or tmp_url[0:8] == 'https://') and base_url in tmp_url and tmp_url not in self.wait_check_url:  # 完整本站链接
            self.wait_check_url.append(tmp_url)
            return tmp_url
        elif tmp_url[0:7] != 'http://' and tmp_url[0:8] != 'https://' and len(tmp_url) != 0:  # 非完整，uri形式
            if tmp_url[0] == '/':
                self.wait_check_url.append(base_url + tmp_url[1:])
                return base_url + tmp_url[1:]
            else:
                self.wait_check_url.append(base_url + tmp_url)
                return base_url + tmp_url
        else:
            return None

    # 特征匹配
    def __reRule(self, data, rule_list):
        url = data[0]
        content = data[2]
        hit_rule_list = []
        now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
        for rule in rule_list:
            if not re.findall(rule, content, re.I | re.S | re.M):
                pass
            else:
                hit_rule_list.append(rule)
        if len(hit_rule_list) != 0:
            res = 'URL:{}\n时间:{}\n命中:{}\n{}'.format(url, now, str(hit_rule_list), '-' * 50)
            with open('暗链敏感词命中.txt', 'a') as f:
                f.write(res + '\n')
            print('[{}]{}|{}|{}'.format(self.u.color(now, 'gray'), self.u.color('敏感词', 'red'), self.u.color(url, 'blue'), str(self.u.color(hit_rule_list, 'yellow'))))
        else:
            print('[{}]{}|{}'.format(self.u.color(now, 'gray'), self.u.color(url, 'blue'), self.u.color('未检出违规', 'green')))

    @async_call
    def __spiderRun(self, ua, max_work, max_deep, url_list):
        # 加入等待检查的url队列
        for url in url_list:
            self.wait_url_check_queue.put(url)
            self.wait_check_url.append(url)  # 加入防重复列表
        # 一直到等待队列清空为止
        while not self.wait_url_check_queue.empty():
            max_deep -= 1
            url_list = []
            for i in range(self.wait_url_check_queue.qsize()):
                url_list.append(self.wait_url_check_queue.get())
            with ThreadPoolExecutor(max_workers=max_work) as executor:
                futures = [executor.submit(self.u.getPage, url, ua) for url in url_list]
                for future in as_completed(futures):
                    result = future.result()
                    # 响应加入规则识别队列
                    self.wait_rule_check_queue.put(result)
                    # 根据深度进行爬虫
                    if max_deep > 0:
                        wait_url_list = self.__spider(result)
                        if wait_url_list:
                            for wait_url in wait_url_list:
                                self.wait_url_check_queue.put(wait_url)
        # 发送爬虫结束信号
        self.spider_flag = True

    def __reRuleRun(self, rule_list):
        # 直到爬虫结束和队列清空
        while not self.wait_url_check_queue.empty() or not self.spider_flag:
            res_list = []
            for i in range(self.wait_rule_check_queue.qsize()):
                res_list.append(self.wait_rule_check_queue.get())
            for res in res_list:
                self.__reRule(res, rule_list)
        print('[*]检测全部结束')

    def run(self, ua, max_work, max_deep, url_list, rule_list):
        self.__spiderRun(ua, max_work, max_deep, url_list)
        self.__reRuleRun(rule_list)
