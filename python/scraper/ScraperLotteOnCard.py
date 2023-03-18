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

        try:

            cardDiscountDict = dict()

            cardNames = []
            discountPercent = []
            maxDiscount = []

            driver = WebdriverBuilder.getDriver()
            driver.get(url)
            time.sleep(2)
            driver.find_element_by_xpath("//div[@class='content benefitContent']//button[@data-object='prd_info=more']").click()
            time.sleep(2)
            cardNameItems = driver.find_elements_by_xpath("//div[@class='historyText']//strong")
            for i in range(len(cardNameItems)) :
                itemText = cardNameItems[i].get_attribute("innerHTML")
                if i%2 == 1: cardNames.append(itemText)

            discountPercent_reg = re.compile("([0-9]+)%할인")
            maxDiscount_reg = re.compile("([0-9]+,[0-9]+)원")
            percentItems = driver.find_elements_by_xpath("//div[@class='tableBox']//td[@class='right']")
            for i in range(len(percentItems)) :
                itemText = percentItems[i].get_attribute("innerHTML")
                itemText = itemText.replace("\n","")
                itemText = itemText.replace(" ","")
                if i % 2 == 0 :
                    match_discountPercent = discountPercent_reg.findall(itemText)
                    discountPercent.append(int(match_discountPercent[0]))
                else :
                    match_maxDiscount = maxDiscount_reg.findall(itemText)
                    match_maxDiscount[0] = match_maxDiscount[0].replace(",","")
                    maxDiscount.append(int(match_maxDiscount[0]))

            for i in range(len(cardNames)):
                cardDiscountDict[cardNames[i]] = {"discountPercent" : discountPercent[i], "maxDiscount" : maxDiscount[i]}

            return {"LotteOnCardDiscount" : cardDiscountDict}
        
        except :
            return None
    
