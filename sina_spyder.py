import requests
from bs4 import BeautifulSoup
import json
import re


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


def parse_link(page_num):
    link_list = []
    for i in range(page_num):
        link = 'http://sports.sina.com.cn/roll/index.shtml#pageid=13&lid=2503&k=&num=50&page=' + str(
            i + 1)
        soup = BeautifulSoup(link2content(link), 'html.parser')
        for news in soup.find_all('span', class_='c_tit'):
            link_list.append(news.a.attrs['href'])
    return link_list


def link2news(link):
    soup = BeautifulSoup(link2content(link), 'html.parser')
    if soup.find('div', class_='article'):
        article = soup.find('div', class_='article').find_all('p')
        s = ""
        for p in article:
            if p.string:
                s += p.string
        return s
    else:
        print("fail")
        return ""


#
# file = open("china_news_gedi.txt", "a")
# NUM = 10
# linklist = parse_link(NUM)
# count = 0
# for l in linklist:
#     count += 1
#     print("%d:%s" % (count, l))
#     file.write(link2news(l) + "\n")
# file.close()

# i = 0
# url = 'https://news.sina.com.cn/world/'
# soup = BeautifulSoup(link2content(url), 'html.parser')
# for s in soup.find_all('div', class_='news-item'):
#     if s.h2:
#         print(s.h2.a.attrs['href'])

# i = 0
# # soup = BeautifulSoup(link2content(url), 'html.parser')

file_link = open("sina_world_link.txt", "w")
file_content = open("sina_world_content.txt", "w")

for page in range(100):
    print(page)
    url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=' + str(
        page + 1
    ) + '&r=0.04431520805875233&callback=jQuery31103805908561688285_1541677612077&_'

    news_urls = re.findall(r'"url":"(.*?)"', link2content(url))

    for u in news_urls:
        link = u.replace('\\', '')
        if 'mil' in link:
            continue
        file_link.write(link + "\n")
        file_content.write(link2news(link) + "\n")

file_link.close()
