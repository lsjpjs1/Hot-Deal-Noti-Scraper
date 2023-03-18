
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

        print(cardDiscountDict)

        return {"CoupangCardDiscount" : cardDiscountDict}
        
 
tt = ScraperCoupangCard()
tt.collectData("https://www.coupang.com/vp/products/6216781914?itemId=12420242670&vendorItemId=79689590721&src=1139000&spec=10799999&addtag=400&ctag=6216781914&lptag=AF2581893&itime=20230317153449&pageType=PRODUCT&pageValue=6216781914&wPcid=16780872279579983401308&wRef=whendiscount.com&wTime=20230317153449&redirect=landing&traceid=V0-183-c221280a956f0957&mcid=0b09ab026fc54bcb9896c7dccd1b07f6&placementid=&clickBeacon=&campaignid=&contentcategory=&imgsize=&pageid=&deviceid=&token=&contenttype=&subid=&impressionid=&campaigntype=&requestid=&contentkeyword=&subparam=&isAddedCart=")
