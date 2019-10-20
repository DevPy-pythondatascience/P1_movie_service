#-*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time

search_keyword = "초코파이"

# 크롤링 도구
driver = webdriver.Chrome('/Users/yutw/Downloads/chromedriver')
driver.implicitly_wait(3)
time.sleep(5)


# 오픈마켓 접속
driver.get('http://www.auction.co.kr/')
time.sleep(5)


# 상품 검색
driver.find_element_by_xpath("//*[@class='search_input_keyword']").send_keys(search_keyword)
time.sleep(3)
driver.find_element_by_xpath("//*[@class='search_btn_ok']").click()
time.sleep(5)


# 상품리스트 가져오기
html = driver.page_source
soup = bs(html, 'html.parser')
itemlist = soup.findAll("div", {"class": "section--itemcard"})
time.sleep(10)


# 가져온 상품리스트에서 필요한 상품명, 가격, 상품링크를 출력!!
for item in itemlist:
    title = item.find("span", {"class": "text--title"}).text
    price = item.find("strong", {"class": "text--price_seller"}).text
    link = item.find("span", {"class": "text--itemcard_title ellipsis"}).a['href']
    print("상품명 : " + title)
    print("가격 : " + price + "원")
    print("상품 링크 : " + link)
    print("------------------------")

time.sleep(10)

driver.close()