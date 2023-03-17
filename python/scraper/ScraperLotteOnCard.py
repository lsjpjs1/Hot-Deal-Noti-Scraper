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

class ScraperLotteOnCard(Scraper):

    def collectData(self, url):

        cardDiscountDict = dict()

        cardName_reg = re.compile('([\s\S]+) [0-9]+%')
        cardDiscountPercent_reg = re.compile('[\s\S]+ ([0-9]+)%')

        driver = WebdriverBuilder.getDriver()
        driver.get(url)
        time.sleep(2)
        driver.find_element_by_xpath("//div[@class='content benefitContent']//button[@data-object='prd_info=more']").click()
        
        items = driver.find_elements_by_xpath("//div[@class='historyText']//strong")

        for item in items :
            print(item.get_attribute("innerHTML"))

        # items = driver.find_elements_by_xpath("//div[@class='content benefitContent']//span[@class='cards']")
        # for item in items:
        #     print(item.get_attribute("innerHTML"))
        # if len(items) == 0: return None
        # for item in items :
        #     itemText = item.get_attribute("innerHTML")
        #     cardName = cardName_reg.findall(itemText)
        #     cardDiscountPercent = cardDiscountPercent_reg.findall(itemText)
        #     cardDiscountDict[cardName[0]] = int(cardDiscountPercent[0])

        # print(cardDiscountDict)
        # return {"LotteOnCardDiscount": {"cardList" : cardDiscountDict}}
    
tt = ScraperLotteOnCard()
tt.collectData("https://www.lotteon.com/p/product/LO2056427037?sitmNo=LO2056427037_2056427038&mall_no=1&dp_infw_cd=SCHlg%20%EB%85%B8%ED%8A%B8%EB%B6%81")
