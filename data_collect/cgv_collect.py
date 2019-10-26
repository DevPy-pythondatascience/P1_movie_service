#-*- coding: utf-8 -*-
import os, sys
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests
import time
from traceback import format_exc
from multiprocessing import Process
import glob

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../'))

from config.base_config import TEMP_STORAGE

base_url = "http://www.cgv.co.kr/movies/finder.aspx"
scene_per_page = 10

def recorder(activity, file_name, data):
    file_path = TEMP_STORAGE + "/" + activity

    if not os.path.isdir(file_path):
        path_list = TEMP_STORAGE.split("/")
        path_add = ""
        if not os.path.isdir(TEMP_STORAGE):
            for each_path in path_list[1:]:
                path_add += "/" + each_path
                if not os.path.isdir(path_add):
                    os.mkdir(path_add)

        if not os.path.isdir(TEMP_STORAGE + "/" + activity):
            os.mkdir(file_path)

    try:
        f = open(file_path + "/" + file_name, "a")
        f.write(data)
        f.close()
    except:
        pass

def read(activity, file_name):
    file_path = TEMP_STORAGE + "/" + activity

    try:
        f = open(file_path + "/" + file_name, "r")
        res = f.read()
        f.close()

        return res
    except:
        pass


# page per crawling
def page_worker_crawler(scene_length, page_number):

    # crawler import
    driver = webdriver.Chrome('/Users/yutw/Downloads/chromedriver')

    # cgv movie finder connect
    driver.get(base_url)

    # all movie find in cgv movie finder
    driver.find_element_by_xpath("//*[@class='round inred']").click()

    for i in range(scene_length):

        try:
            page_idx = driver.find_element_by_xpath("//*[@class='paging']")\
                .find_element_by_xpath("//*[@a=" + str((i + 1) * page_number) + "]")
            page_idx.find_element_by_xpath("a").click()
        except:
            print(format_exc())

        # all movie info html component get
        html = driver.page_source
        soup = bs(html, 'html.parser')
        movies_list = soup.find("div", {"class": "sect-search-chart"}).findAll("ol")


        for x in movies_list:
            for y in x.findAll("li"):
                try:
                    movie = y.find("div", {"class": "box-contents"}).a
                    each_movie_link = movie['href']
                    each_movie_info = requests.get("http://www.cgv.co.kr" + each_movie_link)
                    html = each_movie_info.text
                    soup_movie = bs(html, 'html.parser')

                    movie_info = soup_movie.find("div", {"class": "box-contents"})
                    title = movie_info.find("div", {"class": "title"}).strong.text
                    reserve_percent = movie_info.find("div", {"class": "score"}).find("strong", {"class": "percent"}).span.text
                    audience = movie_info.find("div", {"class": "score"}).find("span", {"class": "view"}).em.text
                    cast = movie_info.find("div", {"class": "spec"}).find("dl")

                    director_text = [cast.findAll("dd")[idx].text for idx, z in enumerate(cast.findAll("dt")) if '감독' in z.text][0]
                    producer_text = [cast.findAll("dd")[idx].text for idx, z in enumerate(cast.findAll("dt")) if '프로듀서' in z.text][0]
                    actor_and_actress_text = [cast.findAll("dd")[idx].text for idx, z in enumerate(cast.findAll("dt")) if '배우' in z.text][0]

                    director = ''.join([z for z in director_text if ord('가') <= ord(z) <= ord('힣') or
                                 ord(z) == ord(',') or ord('A') <= ord(z) <= ord('z')]).replace(',', '_')
                    producer = ''.join([z for z in producer_text if ord('가') <= ord(z) <= ord('힣') or
                                 ord(z) == ord(',') or ord('A') <= ord(z) <= ord('z')]).replace(',', '_')
                    actor_and_actress = ''.join([z for z in actor_and_actress_text if ord('가') <= ord(z) <= ord('힣') or
                                 ord(z) == ord(',') or ord('A') <= ord(z) <= ord('z')]).replace(',', '_')

                    genre_text = [z.text for idx, z in enumerate(cast.findAll("dt")) if '장르' in z.text][0]
                    genre = ''.join([z for z in genre_text if ord('가') <= ord(z) <= ord('힣') or
                                 ord(z) == ord(',') or ord('A') <= ord(z) <= ord('z')]).replace(',', '_')

                    release_date = cast.findAll("dd")[-1].text

                    recorder("movies_info", str(i + 1) + "_" + str(page_number) + ".csv",
                             title + "," + reserve_percent + "," + audience + "," +
                             director + "," + producer + "," + actor_and_actress +
                             "," + genre + "," + release_date + "\n")

                    print(title)
                    print(reserve_percent)
                    print(audience)
                    print(director)
                    print(producer)
                    print(actor_and_actress)
                    print(genre)
                    print(release_date)
                except:
                    print(format_exc())

        time.sleep(1)
        driver.find_element_by_xpath("//*[@class='btn-paging next']").click()

    driver.close()


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
    page_end = soup.find("div", {"class": "paging"}).findAll("li")
    scene_length = int(int(page_end[-1].a.text) / scene_per_page)

    driver.close()

    # multi crawling
    proc_list = []
    for page in range(1):
        page_number = page + 1
        proc = Process(target=page_worker_crawler, args=(scene_length, page_number,))
        proc_list.append(proc)

    for proc in proc_list:
        proc.start()

    for proc in proc_list:
        proc.join()

    recorder("movies_info", "total_movies_info.csv",
             "title,reserve_percent,audience,director,producer,actor_and_actress,genre,release_date\n")

    total_data = []
    movies_data = glob.glob(TEMP_STORAGE + "/movies_info/*.csv")
    for x in movies_data:
        total_data += read("movies_info", x.split("/")[-1]).split('\n')[:-1]

    for x in total_data:
        recorder("movies_info", "total_movies_info.csv", x + "\n")
