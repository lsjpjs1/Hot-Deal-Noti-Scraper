
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests


import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from .Scraper import Scraper
from .WebdriverBuilder import WebdriverBuilder

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import re

class ScraperGmarketCard(Scraper):

    def collectData(self, url):

        discountCardList = []

        cardInfo_reg = re.compile("[\S]+ [0-9]+% \(최대  [0-9]+,[0-9]+원\)")

        driver = WebdriverBuilder.getDriver()
        driver.get(url)
        time.sleep(2)
        items = driver.find_elements_by_xpath("//div[@id='box__information-sub4']//li[@class='list-item']")
        # items = driver.find_elements_by_xpath("//div[@id='box__information-sub4']//em[text()='\" 즉시할인 \"']/following-sibling::ul[1]//li[@class='list-item']")
        print(len(items))
        for item in items :
            print(item.get_attribute("innerHTML"))

        return {"CoupangCardDiscount" : {"cardList": discountCardList} }
        

tt = ScraperGmarketCard()
tt.collectData("http://item.gmarket.co.kr/Item?goodscode=2752591809")