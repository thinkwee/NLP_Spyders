from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string
import datetime


class MyThread(Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def link2content(link):
    headers_new = {
        'Accept':
        '*/*',
        'Accept-Encoding':
        'gzip, deflate',
        'Accept-Language':
        'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection':
        'keep-alive',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    }
    for i in range(4):
        try:
            res = requests.get(url=link, headers=headers_new)
            res.encoding = 'GBK'
            return res.text
        except Exception:
            sleep(0.1)
    return ""


def parse_link(link_str):
    count = 0
    with open('./' + link_str[-4:] + '/' + link_str.split('/')[-1] + '.txt',
              'w') as f:
        url = 'https://aclanthology.coli.uni-saarland.de' + link_str
        soup = BeautifulSoup(link2content(url), 'html.parser')
        for p in soup.find('div', class_='span12').find_all('p'):
            f.write(str(p.contents[1].attrs['href']) + '\n')
            count += 1
    print("parse %d paper link in %s" % (count, link_str))
    return


threads = []
url = 'https://aclanthology.coli.uni-saarland.de/'
soup = BeautifulSoup(link2content(url), 'html.parser')
for p in soup.find('div', class_="span12").find_all('a'):
    if 'event' in p.attrs['href'] and p.attrs['href'].split('-')[-1] >= '2010':
        t = MyThread(parse_link, args=(str(p.attrs['href']), ))
        threads.append(t)

for t in threads:
    t.start()
for t in threads:
    t.join()
