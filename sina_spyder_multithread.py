from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string

NUMS = 12  # threads
JOBS = 1000  # how many jobs*12 for threads
category = "finance"
# url_start = ""

queue_link = Queue()  # for crawling iteratively
queue_content = Queue()  # for crawling content
# queue_link.put(url_start)
# queue_content.put(url_start)

queue_write_file = Queue()  # for writing content to file
queue_work = Queue()  # for setting jobs to threads

file_link = open("sina_link_" + category + ".txt", "w")
file_content = open("sina_news_" + category + ".txt", "w")

count_link = 0
count_line = 0


def link2content(link):
    headers = {
        'Connection': 'Upgrade',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
        'Upgrade': 'websocket',
        'Origin': 'https://news.sina.com.cn',
        'Sec-WebSocket-Version': '13',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Sec-WebSocket-Key': 'pW0gCGJW01DOZk8/6SfhaA==',
        'Sec-WebSocket-Extensions':
        'permessage-deflate; client_max_window_bits',
    }

    res = requests.get(url=link, headers=headers)
    res.encoding = 'UTF-8'
    return res.text


def parse_link(page):
    global count_link
    url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=" + str(
        page + 1
    ) + "&r=0.04431520805875233&callback=jQuery31103805908561688285_1541677612077&_"
    news_urls = re.findall(r'"url":"(.*?)"', link2content(url))

    for u in news_urls:
        link = u.replace('\\', '')
        if 'finance.sina.com.cn' in link:
            queue_link.put(link)
            file_link.write(link + '\n')
            count_link += 1
    print("------------------ %d links have been crawled " % count_link)


def parse_content(id):
    count = 0
    while not queue_link.empty():
        link = queue_link.get()
        soup = BeautifulSoup(link2content(link), 'html.parser')
        s = ""
        if soup.find('div', class_='article'):
            article = soup.find('div', class_='article').find_all('p')
            for p in article:
                if p.string:
                    s += p.string
            count += 1
            queue_content.put(s)
        print("%d parsed %d articles" % (id, count))


def write_file():
    global count_line
    while not queue_content.empty():
        content = queue_content.get()
        file_content.write(content + '\n')
        count_line += 1
    print("\n||     %d news have been crawled     ||\n" % count_line)


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

page = 0
for _ in range(JOBS):
    print("\n||     PAGE %d ~ %d   ||\n" % (page + 1, page + 3))
    parse_link(page + 1)
    parse_link(page + 2)
    parse_link(page + 3)
    page += 3
    for id_thread in range(NUMS):
        queue_work.put(id_thread)
    queue_work.join()  # continue when queue_work is empty
    write_file()

# close the file
file_link.close()
file_content.close()
