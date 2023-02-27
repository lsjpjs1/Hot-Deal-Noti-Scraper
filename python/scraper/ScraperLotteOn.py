import os
import sys



sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import re
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .Scraper import Scraper
from .WebdriverBuilder import WebdriverBuilder


class ScraperLotteOn(Scraper):

    def initSite(self, driver, searchWord):
        driver.get("https://www.lotteon.com/")
        self.wait(driver, (By.XPATH, "//input[@title='검색어 입력']"))
        driver.find_element_by_xpath("//input[@title='검색어 입력']").send_keys(searchWord)
        driver.find_element_by_xpath("//button[@class='btnSearchInner']").click()

    def collectData(self, driver):

        self.waitDuringTime(driver, (
            By.XPATH,
            "//li[@class='srchProductItem']"),
                            10)
        items = driver.find_elements_by_xpath(
            "//li[@class='srchProductItem']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages":[],"productTypeId":self.productTypeId}
        for item in items:
            try:
                original_title = item.find_element_by_xpath(".//div[@class='srchProductUnitTitle']").text
                if original_title.replace(" ","")=="":
                    continue
                title = original_title.replace(" ", "").replace(".", "")
                url = item.find_element_by_xpath(".//a[@class='srchGridProductUnitLink']").get_attribute("href")
                original_price = int(
                    item.find_element_by_xpath(
                        ".//strong[@class='s-product-price__final']/span[@class='s-product-price__number']").text.replace(
                        ",", "")
                )
                thumbnail_url = item.find_element_by_xpath(".//div[@class='srchThumbImageWrap']//img").get_attribute("src")
            except Exception as e:
                print(item.text)
                traceback.print_exc()
                continue
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
                if 15 <= discount_list[0][0] <= 100:
                    hot_deal = {
                        "discountRate": discount_list[0][0], "discountPrice": discount_list[0][1],
                        "originalPrice": original_price, "title": original_title,
                        "url": discount_list[0][2], "sourceSite": "롯데ON",
                        "hotDealThumbnailUrl": thumbnail_url
                    }
                    res.get("hotDealMessages").append(
                        hot_deal
                    )
                    print(hot_deal)
        self.mq.publish(json.dumps(res), 'inputClassifyHotDealCosine')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def goNextPage(self, driver):
        self.wait(driver, (By.XPATH, "//a[@class='srchPaginationNext']"))
        driver.find_element_by_xpath("//a[@class='srchPaginationNext']").click()

    def printCurrentPage(self, driver):
        try:
            self.wait(driver, (By.XPATH, "//span[@class='srchPaginationActive']"))
            print(driver.find_element_by_xpath("//span[@class='srchPaginationActive']").text)
        except:
            print("현재페이지 찾기 오류")

    def startScraping(self, searchWords):
        driver = WebdriverBuilder.getDriver()
        try:
            for searchWord in searchWords:
                print(f"현재검색어 {searchWord}")
                self.initSite(driver, searchWord)
                try:
                    for i in range(35):
                        self.printCurrentPage(driver)
                        self.collectData(driver)
                        self.goNextPage(driver)
                        time.sleep(1)
                except Exception as e:
                    traceback.print_exc()
                    continue
        except Exception as e:
            traceback.print_exc()
        finally:
            driver.quit()



