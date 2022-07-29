import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .Scraper import Scraper
from .WebdriverBuilder import WebdriverBuilder

class Scraper11st(Scraper):
    isPowerProduct = True

    def initSite(self, driver, searchWord):
        self.isPowerProduct = True
        driver.get("https://www.11st.co.kr/main")
        self.wait(driver, (By.XPATH, "//input[@title='통합검색']"))
        driver.find_element_by_xpath("//input[@title='통합검색']").send_keys(searchWord)
        driver.find_element_by_xpath("//button[@class='search_button']").click()
        # wait(driver,(By.XPATH,"//label[text()='일반 모니터']"))
        # driver.find_element_by_xpath("//label[text()='일반 모니터']").click()
        # wait(driver,(By.XPATH,"//label[text()='모니터']"))
        # driver.find_element_by_xpath("//label[text()='모니터']").click()

    def collectData(self, driver):
        if self.isPowerProduct:
            try:
                self.waitDuringTime(driver, (
                    By.XPATH, "//section[@data-log-actionid-area='plus']//div[@class='c_card c_card_list']"), 10)
                items = driver.find_elements_by_xpath(
                    "//section[@data-log-actionid-area='plus']//div[@class='c_card c_card_list']")
            except:
                self.isPowerProduct = False
        if not self.isPowerProduct:
            self.waitDuringTime(driver, (
                By.XPATH, "//section[@data-log-actionid-area='common']//div[@class='c_card c_card_list']"), 10)
            items = driver.find_elements_by_xpath(
                "//section[@data-log-actionid-area='common']//div[@class='c_card c_card_list']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages":[]}
        for item in items:
            original_title = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']").text
            title = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']").text.replace(" ", "")
            url = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']/a").get_attribute("href")
            original_price = int(
                item.find_element_by_xpath(".//dl[@class='price']/dd/span[@class='value']").text.replace(",", ""))
            discount_list = []
            match_comma = comma_won_re.finditer(title)
            match_man = man_won_re.finditer(title)
            price_candidates = []
            if match_comma:
                for comma_won in match_comma:
                    price_candidates.append(int(comma_won[0].replace(",", "")))
            if match_man:
                for man_won in match_man:
                    price_candidates.append(int(man_won[1]) * 10000)
            for price_candidate in price_candidates:
                if price_candidate / original_price > 0.5:
                    discount_list.append([int(100 - 100 * price_candidate / original_price), price_candidate, url])
            if discount_list:
                if 0 <= discount_list[0][0] <= 100:
                    res.get("hotDealMessages").append(
                        {
                            "discountRate": discount_list[0][0], "discountPrice": discount_list[0][1],
                            "originalPrice": original_price, "title": original_title,
                            "url": discount_list[0][2]
                        }
                    )
        self.mq.publish(json.dumps(res))

    def getCurrentPage(self, driver):
        self.wait(driver, (By.XPATH, "//li[@class='active']"))
        return int(driver.find_element_by_xpath("//li[@class='active']").text)

    def goNextPage(self, driver):
        current_page = self.getCurrentPage(driver)
        if current_page % 10 == 0:
            self.wait(driver, (By.XPATH, "//li[@class='next']/a"))
            driver.find_element_by_xpath("//li[@class='next']/a").click()
        else:
            next_page = str(current_page + 1)
            self.wait(driver, (By.XPATH, f"//a[text()='{next_page}']"))
            driver.find_element_by_xpath(f"//a[text()='{next_page}']").click()

    def startScraping(self, searchWords):
        driver = WebdriverBuilder.getDriver()
        for searchWord in searchWords:
            self.initSite(driver, searchWord)
            try:
                for i in range(25):
                    self.collectData(driver)
                    self.goNextPage(driver)
                    time.sleep(1)
            except Exception as e:
                print(e)
                continue



