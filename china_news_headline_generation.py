from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string
import datetime

NUMS = 32  # threads

queue_link = Queue()
queue_content = Queue()
queue_work = Queue()  # for setting jobs to threads

file_src = open("./src.txt", "w")
file_tgt = open("./tgt.txt", "w")


def gettime():
    begin = datetime.date(2018, 1, 1)
    end = datetime.date(2018, 12, 31)
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        yield d.strftime("%Y/%m%d")
        d += delta


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
        else:
            sleep(0.1)
            break
    return ""


def parse_link(url):
    soup = BeautifulSoup(link2content(url), 'html.parser')
    for lm, bt in zip(soup.find_all("div", class_="dd_lm"),
                      soup.find_all("div", class_="dd_bt")):
        if lm.a and bt:
            queue_link.put([bt.a.string, lm.a.string, bt.a.attrs['href']])
    print("parse link complete")


def parse_content(id):
    while not queue_link.empty():
        headline, cat, url = queue_link.get()
        link_left = queue_link.qsize()
        if 'http' not in url:
            url = 'http://www.chinanews.com' + url
        if cat == '图片' or cat == '视频':
            continue
        soup = BeautifulSoup(link2content(url), 'html.parser')
        sleep(0.5)
        s = ""
        if soup.find('div', class_="left_zw"):
            for p in soup.find('div', class_="left_zw").find_all('p'):
                if p.string:
                    s += p.string
            if headline != "" and s != "":
                queue_content.put([headline, s])
            print("%.2d %.80s %.6d" % (id, url, link_left))


def write_file():
    while not queue_content.empty():
        headline, content = queue_content.get()
        file_src.write(content + '\n')
        file_tgt.write(headline + '\n')


def work():
    while True:
        id = queue_work.get()  # pause when queue is empty by default
        parse_content(id)
        queue_work.task_done()


threads = []

for _ in range(NUMS):
    t = Thread(target=work)
    threads.append(t)

for item in threads:
    item.setDaemon(True)
    item.start()

for date_id in gettime():
    print(date_id)
    link = 'http://www.chinanews.com/scroll-news/' + date_id + '/news.shtml'
    parse_link(link)
    for id_thread in range(NUMS):
        queue_work.put(id_thread)
    queue_work.join()  # continue when queue_work is empty
    write_file()

# close the file
file_src.close()
file_tgt.close()

# # test
# for data_id in gettime():
#     url = 'http://www.chinanews.com/scroll-news/'+data_id+'/news.shtml'
#     soup = BeautifulSoup(link2content(url), 'html.parser')
#     for lm,bt in zip(soup.find_all("div",class_="dd_lm"),soup.find_all("div",class_="dd_bt")):
#         print(lm.a.string,bt.a.attrs['href'])

# url ='http://www.chinanews.com/sh/2012/01-11/3598251.shtml'
# soup = BeautifulSoup(link2content(url), 'html.parser')
# s=""
# for p in soup.find('div',class_="left_zw").find_all('p'):
#     if p.string:
#         s+=p.string
# print(s)
