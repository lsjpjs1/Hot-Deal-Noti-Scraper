
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

        cardDiscountDict = dict()

        driver = WebdriverBuilder.getDriver()
        driver.get(url)
        time.sleep(2)
        items = driver.find_elements_by_xpath("//div[@class='par']//p[@class='txt wordBreak']")
        if len(items) == 0: return None
        cardText = items[0].get_attribute("innerHTML").strip().replace(" ","")
        tmpCardList = cardText.split(",")
        for card in tmpCardList:
            cardDiscountDict[card[:2]] = int(card[2])

        return {"HimartCardDiscount": {"cardList" : cardDiscountDict}}