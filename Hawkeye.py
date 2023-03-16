import argparse
from Class import Check, Util, Monitor


class Hawkeye:
    def __init__(self):
        self.u = Util.Util()
        self.c = Check.Check()
        self.m = Monitor.Monitor()
        banner = f'''\033[1;34m

        ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗███████╗██╗   ██╗███████╗
        ██║  ██║██╔══██╗██║    ██║██║ ██╔╝██╔════╝╚██╗ ██╔╝██╔════╝
        ███████║███████║██║ █╗ ██║█████╔╝ █████╗   ╚████╔╝ █████╗  
        ██╔══██║██╔══██║██║███╗██║██╔═██╗ ██╔══╝    ╚██╔╝  ██╔══╝  
        ██║  ██║██║  ██║╚███╔███╔╝██║  ██╗███████╗   ██║   ███████╗
        ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝
                                                --鹰眼web监测 v2.0

    powered by 说书人｜公众号：台下言书|https://github.com/heikanet/Hawkeye\033[0m
            '''
        print(banner)
        try:
            with open('urls.txt', 'r', encoding='utf-8') as f:
                self.url_list = list(set([i for i in f.read().split('\n') if i != '']))
            with open('rules.txt', 'r', encoding='utf-8') as f:
                self.rule_list = list(set([i for i in f.read().split('\n') if i != '']))
        except:
            print('{}'.format(self.u.color('[error]请确保urls.txt（目标网站/页面的链接）和rules.txt（规则文件）位于本目录下', 'red')))
            exit()

    def run(self):
        parser = argparse.ArgumentParser(description='[重保小助手]页面违规检测与重要页面持续监控')
        parser.add_argument("-monitor", action='store_true', help='对关键页面进行监控')
        parser.add_argument("--time", nargs=1, metavar='60', help='监控时间间隔，默认60秒')
        parser.add_argument("--range", nargs=1, metavar='0', help='忽略x个字符内的变化，默认0个')
        parser.add_argument("-check", action='store_true', help='对目标网站进行爬虫并检测违规信息')
        parser.add_argument("--deep", nargs=1, metavar='5', help='爬虫的深度，默认5')
        parser.add_argument("--work", nargs=1, metavar='5', help='爬虫的线程，默认1')
        parser.add_argument("--ua", nargs=1, metavar='baidu', help='user-agent，可选(pc,baidu,google,360,bing,sm,sogou)，默认使用百度蜘蛛')
        args = parser.parse_args()

        if args.ua:
            ua = args.ua[0]
        elif args.ua in ['pc', 'baidu', 'google', '360', 'bing', 'sm', 'sogou']:
            print(f'{self.u.color("[*] --ua 参数值填写错误，将默认使用baidu", "yellow")}')
            ua = 'baidu'
        else:
            ua = 'baidu'
        if args.check:
            if args.deep:
                if args.deep[0].isdigit():
                    max_deep = int(args.deep[0])
                else:
                    print(f'{self.u.color("[-] --deep 的值应为数字", "yellow")}')
                    return
            else:
                max_deep = 5
            if args.work:
                if args.work[0].isdigit():
                    max_work = int(args.work[0])
                else:
                    print(f'{self.u.color("[-] --work 的值应为数字", "yellow")}')
                    return
            else:
                max_work = 1

            self.c.run(ua, max_work, max_deep, self.url_list, self.rule_list)
        elif args.monitor:
            if args.time:
                if args.time[0].isdigit():
                    delay = int(args.time[0])
                else:
                    print(f'{self.u.color("[-] --time 的值应为数字", "yellow")}')
                    return
            else:
                delay = 60
            if args.range:
                if args.range[0].isdigit():
                    str_range = int(args.range[0])
                else:
                    print(f'{self.u.color("[-] --range 的值应为数字", "yellow")}')
                    return
            else:
                str_range = 0

            self.m.run(self.url_list, str_range, ua, delay)
        else:
            print(f'{self.u.color("[tips] 使用 -h 参数查看使用说明", "yellow")}')


if __name__ == "__main__":
    Hawkeye = Hawkeye()
    Hawkeye.run()
