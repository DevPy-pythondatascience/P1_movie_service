#-*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import asyncio

from multiprocessing import Process

base_url = "http://www.cgv.co.kr/movies/finder.aspx"
scene_per_page = 10


# page per crawling
def page_worker_crawler(scene_length, page_number):

    # crawler import
    driver = webdriver.Chrome('/Users/yutw/Downloads/chromedriver')

    # cgv movie finder connect
    driver.get(base_url)

    # all movie find in cgv movie finder
    driver.find_element_by_xpath("//*[@class='round inred']").click()
    driver.find_element_by_xpath("//*[@class='paging']").click()

    # all movie info html component get
    html = driver.page_source
    soup = bs(html, 'html.parser')
    movies_list = soup.find("div", {"class": "sect-search-chart"}).findAll("ol")

    for x in movies_list:
        x.find("div", {"class": "box-contents"})


if __name__ == '__main__':

    # crawler import
    driver = webdriver.Chrome('/Users/yutw/Downloads/chromedriver')

    # cgv movie finder connect
    driver.get(base_url)

    # all movie find in cgv movie finder
    driver.find_element_by_xpath("//*[@class='round inred']").click()
    driver.find_element_by_xpath("//*[@class='btn-paging end']").click()

    # all movie info html component get
    html = driver.page_source
    soup = bs(html, 'html.parser')
    movies_list = soup.find("div", {"class": "paging"}).findAll("li")
    scene_length = int(movies_list[-1].text) / scene_per_page

    driver.close()

    # multi crawling
    proc_list = []
    for page in range(scene_per_page):
        page_number = page + 1
        proc = Process(target=page_worker_crawler, args=(scene_length, page_number,))
        proc_list.append(proc)

    for proc in proc_list:
        proc.start()

    for proc in proc_list:
        proc.join()

