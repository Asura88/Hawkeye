# python3
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


class Util:

    def __init__(self):
        self.user_agent = {
            'pc': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
            'baidu': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'google': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            '360': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36; 360Spider',
            'bing': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'sm': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 YisouSpider/5.0 Safari/537.36',
            'sogou': 'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)'
        }

    # 无头浏览器访问web，支持渲染
    def getPage(self, url, ua):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.new_context(user_agent=self.user_agent[ua])
                page = browser.new_page()
                page.goto(url, )
                title = page.title()
                content = page.content()
                browser.close()
            return url, title, content
        except:
            return url, '无法访问', '无法访问'

    # 获取base url
    def getBaseUrl(self, url):
        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc + '/'
        return base_url

    # 颜色
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
