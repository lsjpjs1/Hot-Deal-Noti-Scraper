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


class ScraperAuction(Scraper):

    def initSite(self, driver, searchWord):
        driver.get("http://www.auction.co.kr/")
        self.wait(driver, (By.XPATH, "//input[@title='검색어 입력']"))
        driver.find_element_by_xpath("//input[@title='검색어 입력']").send_keys(searchWord)
        driver.find_element_by_xpath("//input[@class='search_btn_ok']").click()

    def collectData(self, driver):

        self.waitDuringTime(driver, (
            By.XPATH,
            "//div[@class='section--itemcard']"),
                            10)
        items = driver.find_elements_by_xpath(
            "//div[@class='section--itemcard']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages": []}

        page_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, page_height, 40):
            j = i + 1
            driver.execute_script(f"window.scrollTo({i}, {j})")

        for item in items:
            try:
                original_title = item.find_element_by_xpath(
                    ".//span[@class='text--itemcard_title ellipsis']//span[@class='text--title']").text
                title = original_title.replace(" ", "").replace(".", "")
                url = item.find_element_by_xpath(
                    ".//span[@class='text--itemcard_title ellipsis']//a[@class='link--itemcard']").get_attribute("href")
                original_price = int(
                    item.find_element_by_xpath(".//strong[@class='text--price_seller']").text.replace(",", "")
                )
                thumbnail_url = item.find_element_by_xpath(".//img[@class='image--itemcard  ']").get_attribute("src")
            except Exception as e:
                print(original_title)
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
                            "url": discount_list[0][2], "sourceSite": "옥션",
                            "hotDealThumbnailUrl": thumbnail_url
                        }
                    print(hot_deal)
                    res.get("hotDealMessages").append(
                        hot_deal
                    )
        self.mq.publish(json.dumps(res), 'inputHotDeal')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def goNextPage(self, driver):
        self.wait(driver, (By.XPATH, "//a[@class='link--next_page']"))
        driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("//a[@class='link--next_page']"))

    def startScraping(self, searchWords):
        driver = WebdriverBuilder.getDriver()
        try:
            for searchWord in searchWords:
                print(f"현재검색어 {searchWord}")
                self.initSite(driver, searchWord)
                try:
                    for i in range(15):
                        print(driver.find_element_by_xpath("//span[@class='link--page on']").text+"페이지")
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
