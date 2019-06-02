from urllib import request
from bs4 import BeautifulSoup
import re
from queue import Queue
from threading import Thread
from time import sleep
import requests
import string

NUMS = 12  # threads
JOBS = 800  # how many jobs*12 for threads
start_keyword = "Philosophy"
url_start = "https://en.wikipedia.org/wiki/" + start_keyword

queue_link = Queue()  # for crawling iteratively
queue_content = Queue()  # for crawling content
queue_link.put(url_start)
queue_content.put(url_start)

queue_write_file = Queue()  # for writing content to file
queue_work = Queue()  # for setting jobs to threads

sets_url = set()  # avoid duplicate urls
sets_url.add(url_start)

file_link = open("wiki_link.txt", "w")
file_content = open("wiki_entry.txt", "w")

count_link = 0
count_content = 0
count_line = 0


def link2content(link):
    session = requests.Session()
    session.headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/56.0.2924.87 Safari/537.36 '
    }
    return session.get(link).text


def parse_link():
    global count_link
    link_for_parse = queue_link.get()
    soup_for_sparse = BeautifulSoup(link2content(link_for_parse),
                                    'html.parser')

    for link in soup_for_sparse.find('div', id="bodyContent").find_all(
            'a', href=re.compile("^(/wiki/)((?!;)\S)*$")):
        link_content = 'https://en.wikipedia.org' + link.attrs['href']
        if 'Category:' in link_content or 'File:' in link_content:
            continue
        if "Special:" in link_content or "Template:" in link_content or "Help:" in link_content:
            continue
        if link_content in sets_url or "%" in link_content:
            continue
        file_link.write(link_content + "\n")
        queue_link.put(link_content)
        queue_content.put(link_content)
        sets_url.add(link_content)
        count_link += 1
    print("------------------ %d links have been crawled " % count_link)


def parse_content(id_th):
    global count_content
    count_every_crawl = 0
    while True:
        link_content = queue_content.get()
        soup_for_content = BeautifulSoup(link2content(link_content),
                                         'html.parser')
        contents = soup_for_content.find('div', id="bodyContent").find_all('p')
        if len(contents) < 3:
            continue
        if contents[2] is None:
            continue
        content = contents[2]
        str_list = ""
        for c in content.contents:
            str_list += "" if c.string is None else c.string
        str_list = str_list.split(('. '))

        queue_write_file.put(str_list[0])

        if len(str_list) > 1:
            queue_write_file.put(str_list[1])

        if len(str_list) > 2:
            queue_write_file.put(str_list[2])

        if len(str_list) > 3:
            queue_write_file.put(str_list[3])

        if len(str_list) > 4:
            queue_write_file.put(str_list[4])

        count_content += 1
        count_every_crawl += 1
        print("thread %.2d parsed No.%.6d entry: %s" %
              (id_th, count_content, link_content[30:]))
        if count_every_crawl == 10:
            break


def write_file():
    global count_line
    while not queue_write_file.empty():
        content = queue_write_file.get()
        if content == b"":
            continue
        file_content.write(content + '\n')
        count_line += 1
    print("------------------ %d lines have been written in to files" %
          count_line)


def work():
    while True:
        id = queue_work.get()  # pause when queue is empty by default
        parse_content(id)
        sleep(0.5)
        queue_work.task_done()


threads = []

for _ in range(NUMS):
    t = Thread(target=work)
    threads.append(t)

for item in threads:
    item.setDaemon(True)
    item.start()

for j in range(JOBS):
    print("-------------- job %d" % j)
    parse_link()
    for id_thread in range(NUMS):
        queue_work.put(id_thread)
    queue_work.join()  # continue when queue_work is empty
    write_file()

# close the file
file_link.close()
file_content.close()
