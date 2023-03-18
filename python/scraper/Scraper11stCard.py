
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

class Scraper11stCard(Scraper):

    def collectData(self, url):

        try :

            tmp = dict()
            cardDiscountDict = dict()

            driver = WebdriverBuilder.getDriver()
            driver.get("https://www.11st.co.kr/")
            #driver.get("https://www.11st.co.kr/products/4232553607?trTypeCd=20&trCtgrNo=585021")
            driver.get(url)
            #self.wait(driver, (By.XPATH, "//dl[@class='cont_info']//dt"))
            time.sleep(2)

            maxItems = driver.find_elements_by_xpath("//div[contains(@id,'ar-layerSale')]//dt[contains(@id,'ar-layerTitleSale')]") #최대할인 추출
            maxDiscount = 0
            maxDiscount_reg = re.compile('카드추가할인 최대 [0-9]+% \(([0-9]+,[0-9]+)원\)')

            for maxItem in maxItems:
                maxItemText = maxItem.get_attribute("innerHTML")
                match_maxDiscount = maxDiscount_reg.findall(maxItemText)
                if(len(match_maxDiscount) != 0):
                    maxDiscount = int(match_maxDiscount[0].replace(',',''))

            items = driver.find_elements_by_xpath("//div[contains(@id,'ar-layerSale')]//dl[@class='cont_info']//dd") #카드별할인 추출
            cardDiscount_reg = re.compile('([\s\S]+) [0-9]+% 할인')
            cardDiscountPercent_reg = re.compile('([0-9]+)% 할인')

            for item in items:
                itemText = item.get_attribute("innerHTML")
                cardNames = []
                cardDiscountPercent = 0
                match_cardDiscount = cardDiscount_reg.findall(itemText)
                if (len(match_cardDiscount) != 0) :
                    cardNames = match_cardDiscount[0].split(',')
                    match_cardDiscountPercent = cardDiscountPercent_reg.findall(itemText)
                    cardDiscountPercent = int(match_cardDiscountPercent[0])
                    for i in range(len(cardNames)):
                        cardNames[i] = cardNames[i].replace(' ','')
                        cardDiscountDict[cardNames[i]] = { "discountPercent" : cardDiscountPercent, "maxDiscount" : maxDiscount }

            print(cardDiscountDict, maxDiscount)

            return { "11stCardDiscount" : cardDiscountDict}

        except :
            return None
