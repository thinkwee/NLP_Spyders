from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string
import datetime
"""
从中国新闻网上爬取指定时间段内所有的新闻
在中国新闻网上，一天的新闻存在一个新闻标题列表上，列表的网址就是'http://www.chinanews.com/scroll-news/'+日期+'/news.shtml'
列表中每一个标题为：【分类】新闻标题
爬虫先依次遍历每一天，将该天所有新闻的标题及其分类爬下，同时存储这些标题对应的正文跳转链接

"""
NUMS = 12  # 线程数

queue_link = Queue()  # 单篇新闻的分类及链接队列
queue_content = Queue()  # 存放爬取后的文本内容的队列
queue_work = Queue()  # 线程队列

# 新闻的分类
category = {
    '证券', '生活', '娱乐', '汽车', '法治', '留学', '健康', '华教', '华人', '文化', '侨乡',
    'I\xa0\xa0T', '能源', '台湾', '报摘', '教育', '港澳', '侨界', '社会', '财经', '体育', '房产',
    '国内', '国际', '金融', '地方', '军事'
}

# 初始化一个计数词典，统计每一类爬了多少篇新闻
count = {c: 0 for c in category}

# 初始化一个分类到文件的词典，方便将不同类别的新闻存到不同的文件中
cat2file = dict()

# 每爬几天的新闻就统计各类别已经爬取的新闻数量，写入file_stat
file_stat = open("statistic.txt", "a")

# 完成分类到文件的词典
for c in category:
    file = open(c + ".txt", "a")
    cat2file[c] = file


# 遍历时间的函数，产生指定时间段内每一天的字符串的迭代器
def gettime():
    begin = datetime.date(2014, 8, 15)
    end = datetime.date(2015, 12, 31)
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        yield d.strftime("%Y/%m%d")
        d += delta


# 给定链接，返回该链接页面上的文本内容(html)，方便后续BeautifulSoup将其格式化来选取页面元素
def link2content(link):
    # headers = {
    #     'Connection': 'Upgrade',
    #     'Pragma': 'no-cache',
    #     'Cache-Control': 'no-cache',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
    #     'Upgrade': 'websocket',
    #     'Origin': 'https://news.sina.com.cn',
    #     'Sec-WebSocket-Version': '13',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'Sec-WebSocket-Key': 'pW0gCGJW01DOZk8/6SfhaA==',
    #     'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    # }

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


# 给定某一天所有新闻列表页面的链接，将列表中所有单条新闻的分类和链接写入队列
def parse_link(url):
    soup = BeautifulSoup(link2content(url), 'html.parser')
    for lm, bt in zip(soup.find_all("div", class_="dd_lm"),
                      soup.find_all("div", class_="dd_bt")):
        if lm.a and bt:
            queue_link.put([lm.a.string, bt.a.attrs['href']])
    print("parse link complete")


# id指示是哪一个线程在爬，线程从链接队列中取出分类与链接，做简单的清洗
# 之后用link2content得到链接对应的html，并用BeautifulSoup格式化html来获取指定页面元素
# 这里指定class为left_zw的div标签，即左侧正文，将新闻正文存为字符串，连同其分类写入内容队列
# 当链接队列中没有链接可以爬了，线程就结束
def parse_content(id):
    while not queue_link.empty():
        cat, url = queue_link.get()
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
            queue_content.put([cat, s])
            print("%.2d %.80s %.6d" % (id, url, link_left))


# 将内容队列中的所有新闻按分类写入文件，并统计各类数量
def write_file():
    global count
    while not queue_content.empty():
        cat, content = queue_content.get()
        cat2file[cat].write(content + '\n')
        count[cat] += 1


# 线程工作函数，多个线程共享单篇新闻链接队列和新闻内容队列，同时爬取同一天的所有新闻
def work():
    while True:
        id = queue_work.get()  # 默认当线程队列为空时暂停，因此可以写成while True循环
        parse_content(id)
        queue_work.task_done()  # 当所有线程都结束之后继续程序


# 初始化线程队列，指定线程工作函数
threads = []
for _ in range(NUMS):
    t = Thread(target=work)
    threads.append(t)
for item in threads:
    item.setDaemon(True)
    item.start()

# 每隔十天打印分类爬取量统计
date_count = 0

# 在指定时间段内遍历每一天
for date_id in gettime():
    # 先爬取好单天所有新闻链接
    print(date_id)
    link = 'http://www.chinanews.com/scroll-news/' + date_id + '/news.shtml'
    parse_link(link)

    # 启用多线程，爬取单篇新闻
    for id_thread in range(NUMS):
        queue_work.put(id_thread)

    # 所有线程爬取完毕后，继续将爬好的内容写入文件
    queue_work.join()
    write_file()

    # 打印统计
    date_count += 1
    if date_count % 10 == 0:
        print(count)
        file_stat.write(str(count))
        file_stat.write('\n')

# 关闭文件
for c in category:
    cat2file[c].close()

# 以下为测试代码，用来确定网页元素
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