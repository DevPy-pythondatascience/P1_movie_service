#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime, timedelta
import time

base_url = "http://news.naver.com/#"

def collecting(base_url):

    while True:
        data = urlopen(base_url).read()
        soup = BeautifulSoup(data, "html.parser")
        total_data = soup.find_all(attrs={'class': 'main_component droppable'})


        for each_data in total_data:

            try:
                category = str(each_data.find_all(attrs={'class': 'tit_sec'})).split('>')[2][:-3]
            except:
                pass

            data = str(each_data.find_all(attrs={'class': 'mlist2 no_bg'}))

            news_list = data.split('<li>')

            for each_news in news_list[1:]:
                # 뉴스 개당 전문을 가져온다
                news_block = each_news.split('href="')[1]
                # print(news_block)

                title = news_block.split('<strong>')[1].split('</strong>')[0]
                # print(title)
                news_url = news_block.split('"')[0].replace("amp;", "")
                # print(news_url)
                soup2 = BeautifulSoup(urlopen(news_url).read(), "html.parser")
                # print(soup2)

                # article_info = soup2.find_all(attrs={'class': 'article_info'})
                # print(article_info)

                article_body = str(soup2.find_all(attrs={'id': 'articleBodyContents'}))

                insert_data = [category, "", "", title, "", article_body, str(datetime.utcnow() + timedelta(hours=9)), "release"]

                print(insert_data)


        time.sleep(3600)


collecting(base_url)
