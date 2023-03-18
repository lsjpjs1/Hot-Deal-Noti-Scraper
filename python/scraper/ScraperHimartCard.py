
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

class ScraperHimartCard(Scraper):

    def collectData(self, url):

        try:

            cardDiscountDict = dict()

            cardNames = []
            discountPercent = []
            maxDiscount = []

            driver = WebdriverBuilder.getDriver()
            driver.get(url)
            time.sleep(2)
            items = driver.find_elements_by_xpath("//div[@class='sectionDashed']//h4[@class='cardName colorRed']")

            cardNames_reg = re.compile("([\S]+)카드")
            discountPercent_reg = re.compile("([0-9]+)%")

            for item in items:
                itemText = item.get_attribute("innerHTML")
                match_cardName = cardNames_reg.findall(itemText)
                match_discountPercent = discountPercent_reg.findall(itemText)
                cardNames.append(match_cardName[0])
                discountPercent.append(int(match_discountPercent[0]))

            maxDiscount_reg = re.compile("최대 ([0-9]+,[0-9]+)원")
            maxDiscountItems = driver.find_elements_by_xpath("//div[@class='sectionDashed']//li")
            for item in maxDiscountItems:
                itemText = item.get_attribute("innerHTML")
                match_maxDiscount = maxDiscount_reg.findall(itemText)
                if len(match_maxDiscount) > 0 : 
                    match_maxDiscount[0] = match_maxDiscount[0].replace(',','')
                    maxDiscount.append(int(match_maxDiscount[0]))

            for i in range(len(items)) :
                cardDiscountDict[cardNames[i]] = {"discountPercent" : discountPercent[i], "maxDiscount" : maxDiscount[i]}
            
            return {"HimartCardDiscount" : cardDiscountDict }

        except :
            return None
