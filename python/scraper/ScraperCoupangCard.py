
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

class ScraperCoupangCard(Scraper):

    def collectData(self, url):

        try :

            cardDiscountDict = dict()

            discountCardList = []
            discountPercentList = []
            maxDiscountList = []

            driver = WebdriverBuilder.getDriver()
            driver.get(url)
            time.sleep(2)
            driver.find_element_by_xpath("//div[@class='ccid-detail-tit']//a[@role='button']").click()
            time.sleep(2)
            driver.switch_to.frame(
            driver.find_element_by_xpath("//iframe[@class='card-benefit-popup__content-iframe']"))
            items = driver.find_elements_by_xpath("//h3[text()='카드할인']/following-sibling::div[1]//img[@class='benefit-table__card-logo']")

            for item in items:
                discountCardList.append(item.get_attribute("alt"))
            
            hmItems = driver.find_elements_by_xpath("//h3[text()='카드할인']/following-sibling::div[1]//p")
            discountPercent_reg = re.compile("([0-9]+)% 할인")
            maxDiscount_reg = re.compile("최대 ([0-9]+[만,천])원")
            for hmItem in hmItems:
                hmItemText = hmItem.get_attribute("innerHTML")
                match_discountPercent = discountPercent_reg.findall(hmItemText)
                match_maxDiscount = maxDiscount_reg.findall(hmItemText)
                if len(match_discountPercent)!=0 and len(match_maxDiscount)!=0 :
                    manOrCheon = 0
                    if match_maxDiscount[0][len(match_maxDiscount[0])-1] == "만" : manOrCheon = 10000
                    else : manOrCheon = 1000
                    maxDiscountList.append(int(match_maxDiscount[0][:(len(match_maxDiscount[0])-1)]) * manOrCheon)
                    discountPercentList.append(int(match_discountPercent[0]))
            
            for i in range(len(items)):
                cardDiscountDict[discountCardList[i]] =  { "discountPercent" : discountPercentList[i], "maxDiscount" : maxDiscountList[i] } 

            return {"CoupangCardDiscount" : cardDiscountDict}
        
        except :
            return None
 

