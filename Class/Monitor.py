# python3
import time
import pytz
import datetime
from Class import Util


class Monitor:
    def __init__(self):
        self.url_list = []  # 监控的url列表
        self.url_length_dict = {}  # url对应的标题和长度字典
        self.u = Util.Util()

    # 初始化-重要页面标题和长度
    def __getIndex(self, ua):
        for url in self.url_list:
            res = self.u.getPage(url, ua)
            if res[2] == '无法访问':
                length = 0
                title = res[1]
            else:
                length = len(res[2])
                title = res[1]
            self.url_length_dict[url] = (length, title)

    # 重要页面监控
    def __monitor(self, str_range, ua):
        for url in self.url_list:
            data = self.u.getPage(url, ua)
            url = data[0]
            title = data[1]
            content = data[2]
            now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
            if title == '无法访问' and content == '无法访问':
                res = '[{}]{}|{}|无法访问'.format(now, url, title)
                print('[{}]{}|{}|{}'.format(self.u.color(now, 'gray'), self.u.color(url, 'blue'), self.u.color(title, 'gray'), self.u.color('无法访问', 'yellow')))
            else:
                length_change_tmp = len(content) - self.url_length_dict[url][0]
                length_change = length_change_tmp if length_change_tmp >= 0 else -length_change_tmp
                if length_change <= str_range:
                    if title == self.url_length_dict[url][1]:
                        res = '[{}]{}|{}|页面正常'.format(now, url, title)
                        print('[{}]{}|{}|{}'.format(self.u.color(now, 'gray'), self.u.color(url, 'blue'), self.u.color(title, 'gray'), self.u.color('页面正常', 'green')))
                    else:
                        res = '[{}]{}|{}|标题发生变化：{}'.format(now, url, title, self.url_length_dict[url][1])
                        print('[{}]{}|{}|{}：{}'.format(self.u.color(now, 'gray'), self.u.color(url, 'blue'), self.u.color(title, 'gray'), self.u.color('标题发生变化', 'red'), self.u.color(self.url_length_dict[url][1], 'red')))
                else:
                    res = '[{}]{}|{}|长度发生变化：{}'.format(now, url, title, length_change).encode('utf-8', 'ignore').decode()
                    print('[{}]{}|{}|{}：{}'.format(self.u.color(now, 'gray'), self.u.color(url, 'blue'), self.u.color(title, 'gray'), self.u.color('长度发生变化', 'red'), self.u.color(self.url_length_dict[url][0] - len(content), 'red')))
            with open('重要页面监控日志_{}.txt'.format(str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y_%m_%d'))), 'a') as f:
                f.write(res + '\n')

    def run(self, url_list, str_range, ua, delay):
        self.url_list = url_list
        self.__getIndex(ua)
        while True:
            self.__monitor(str_range, ua)
            now = str(datetime.datetime.now(pytz.timezone('PRC')).strftime('%Y-%m-%d %H:%M:%S'))
            print(f'[{self.u.color(now, "gray")}]本轮结束，下一轮将在{self.u.color(delay, "green")}秒后继续')
            time.sleep(delay)
