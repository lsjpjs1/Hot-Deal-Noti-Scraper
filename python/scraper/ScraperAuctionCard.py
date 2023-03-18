
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

class ScraperAuctionCard(Scraper):

    def collectData(self, url):

        try :

            cardDiscountDict = dict()

            cardNames = []
            discountPercent = []
            maxDiscount = []

            cardName_reg = re.compile("([\S][\S])카드")
            discountPercent_reg = re.compile(" ([0-9]+)%")
            maxDiscount_reg = re.compile("최대 ([0-9]+,[0-9]+)원")

            driver = WebdriverBuilder.getDriver()
            driver.get(url)
            time.sleep(2)
            items = driver.find_elements_by_xpath("//ul[@class='list__discount']//li")
            # items = driver.find_elements_by_xpath("//div[@id='box__information-sub4']//em[text()='\" 즉시할인 \"']/following-sibling::ul[1]//li[@class='list-item']")
            
            for item in items :
                itemText = item.get_attribute("innerHTML")
                match_cardName = cardName_reg.findall(itemText)
                cardNames.append(match_cardName[0])
                match_discountPercent = discountPercent_reg.findall(itemText)
                discountPercent.append(int(match_discountPercent[0]))
                match_maxDiscount = maxDiscount_reg.findall(itemText)
                match_maxDiscount[0] = match_maxDiscount[0].replace(",","")
                maxDiscount.append(int(match_maxDiscount[0]))

            for i in range(len(cardNames)) :
                cardDiscountDict[cardNames[i]] = {"discountPercent" : discountPercent[i], "maxDiscount" : maxDiscount[i]}
        
            return {"AuctionDiscount" : cardDiscountDict }
        
        except :
            return None
        
        
