from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string
import random

url_book_list = 'https://book.douban.com/tag/%E6%8E%A8%E7%90%86?start=0&type=T'
url_book_reviews = 'https://book.douban.com/subject/2567698/reviews'
url_book_review = 'https://book.douban.com/review/2038942/'
url_book_comments = 'https://book.douban.com/subject/3259440/comments/'

PROXY_POOL_URL = 'http://localhost:5555/random'


# 从代理池随机获取代理
def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


# 使用代理，访问link返回html页面内容
def link2content(link):
    sleep(0.1)
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/56.0.2924.87 Safari/537.36 ',
        'Referer':
        link
    }
    proxy = get_proxy()
    proxies = {"http": proxy}
    cookies = {
        "Cookies":
        "bid=%s" %
        "".join(random.sample(string.ascii_letters + string.digits, 11))
    }
    return requests.get(url=link,
                        headers=headers,
                        proxies=proxies,
                        cookies=cookies).text


# 得到书本列表页上每一本书的链接
def get_book_urls_perpage(link):
    book_list = BeautifulSoup(link2content(link), 'html.parser')
    urls = []
    for book_url in book_list.find('div',
                                   id='subject_list').find_all('a',
                                                               class_='nbg'):
        urls.append(book_url.attrs['href'])

    return urls


# 得到一本书指定数量的长评链接
def get_review_urls_perbook(link, page_num):
    urls = []
    for i in range(page_num):
        link = link + '/reviews?start=' + str(i) * 20
        review_list = BeautifulSoup(link2content(link), 'html.parser')
        for review_url in review_list.find_all(
                'a', href=re.compile("S*(/review/)[0-9]*/$")):
            urls.append(review_url.attrs['href'])
    return urls


# 访问长评链接，返回长评文本
def link2review(link):
    content = BeautifulSoup(link2content(link), 'html.parser')
    review = ""
    for p in content.find('div', class_='review-content clearfix').contents:
        if p.string:
            review += p.string
    return review


# 给出某一本书链接，写入指定数量的长评到文件
def write_review_to_file(link, page_num):
    f = open('book_review.txt', 'a')
    list_review = get_review_urls_perbook(link, page_num)
    for link_review in list_review:
        f.write(link2review(link_review).strip().replace("\n", "") + "\n")

    f.close()


# 给出一本书的短评链接，返回短评列表
def link2comments(link):
    comments = BeautifulSoup(link2content(link), 'html.parser')
    comments_list = []
    for c in comments.find_all('span', class_='short'):
        comments_list.append(c.string)
    return comments_list


# 将某一本书的短评写入文件
def write_comment_to_file(link):
    f = open('book_comments_baiyexing.txt', 'a')

    list_comments = link2comments(link)
    for line in list_comments:
        f.write(line + '\n')

    f.close()


for book_list_id in range(1):
    url_book_list = 'https://book.douban.com/tag/%E6%8E%A8%E7%90%86?start=' + str(
        book_list_id * 20) + '&type=T'
    url_book_per_page = get_book_urls_perpage(url_book_list)
    for url_book in url_book_per_page:
        print(url_book)
        write_review_to_file(url_book, 5)
