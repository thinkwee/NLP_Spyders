from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string
import datetime
import os
import urllib


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


def parse_content(path, txt):
    count = 0
    with open(path + txt, 'r') as f:
        for line in f:
            if count == 0:
                count += 1
                continue
            urllib.request.urlretrieve(
                line, path + line.split('/')[-1][:-1] + '.pdf')
            count += 1
    print("parse %d paper in %s" % (count, txt))
    return


threads = []
for i in range(9):
    year = 2010 + i
    path = './' + str(year) + '/'
    for txt in os.listdir(path):
        t = MyThread(parse_content, args=(
            path,
            txt,
        ))
        threads.append(t)

for t in threads:
    t.start()
for t in threads:
    t.join()

# # test
# url = 'https://aclanthology.coli.uni-saarland.de/'
# soup = BeautifulSoup(link2content(url), 'html.parser')
# for p in soup.find('div', class_="span12").find_all('a'):
#     if 'event' in p.attrs['href'] and p.attrs['href'].split('-')[-1] >= '2010':
#         t = MyThread(parse_link, args=(str(p.attrs['href']),))
#         threads.append(t)
