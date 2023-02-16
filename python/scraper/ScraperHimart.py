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


class ScraperHimart(Scraper):

    def initSite(self, driver, searchWord):
        driver.get("https://www.e-himart.co.kr/")
        self.wait(driver, (By.XPATH, "//input[@id='topSearchQuery']"))
        driver.find_element_by_xpath("//input[@id='topSearchQuery']").send_keys(searchWord)
        self.wait(driver, (By.XPATH, "//a[@id='btnSearch']"))
        driver.find_element_by_xpath("//a[@id='btnSearch']").click()

    def collectData(self, driver):

        self.waitDuringTime(driver, (
            By.XPATH,
            "//div[@class='prdItem ']"),
                            10)
        items = driver.find_elements_by_xpath(
            "//div[@class='prdItem ']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages":[]}
        for item in items:
            try:
                original_title = item.find_element_by_xpath(".//p[@class='prdName']").text
                title = original_title.replace(" ", "").replace(".", "")
                url = item.find_element_by_xpath(".//a[@class='prdLink']").get_attribute("href")
                original_price = int(
                    item.find_element_by_xpath(
                        ".//div[@class='priceInfo']//span[@class='discountPrice']//strong").text.replace(
                        ",", "")
                )
                try:
                    discount_price = int(
                        item.find_element_by_xpath(
                            ".//div[@class='priceInfo priceBenefit']//span[@class='discountPrice']//strong").text.replace(
                            ",", "")
                    )
                except:
                    continue
                is_sold_out = len(item.find_elements_by_xpath(".//div[@class='soldout']"))>0
                thumbnail_url = item.find_element_by_xpath(".//div[@class='prdImg']//img").get_attribute("src")

            except Exception as e:
                traceback.print_exc()
                continue
            if original_price<300000 or is_sold_out:
                continue
            discount_rate=int(100 - 100 * discount_price / original_price)

            if 15 <= discount_rate <= 100:
                hot_deal = {
                                "discountRate": discount_rate, "discountPrice": discount_price,
                                "originalPrice": original_price, "title": original_title,
                                "url": url, "sourceSite": "하이마트",
                            "hotDealThumbnailUrl": thumbnail_url
                            }
                res.get("hotDealMessages").append(
                            hot_deal
                )
                print(hot_deal)
        self.mq.publish(json.dumps(res), 'inputClassifyHotDealCosine')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def getCurrentPage(self, driver):
        self.wait(driver, (By.XPATH, "//div[@id='pageNavigator']//a[@class='on']"))
        return int(driver.find_element_by_xpath("//div[@id='pageNavigator']//a[@class='on']").text)

    def goNextPage(self, driver):
        current_page = self.getCurrentPage(driver)
        print(current_page)
        if current_page % 10 == 0:
            self.wait(driver, (By.XPATH, "//div[@id='pageNavigator']//a[@class='next']"))
            driver.find_element_by_xpath("//div[@id='pageNavigator']//a[@class='next']").click()
        else:
            next_page = str(current_page + 1)
            self.wait(driver, (By.XPATH, f"//div[@id='pageNavigator']//a[text()='{next_page}']"))
            driver.find_element_by_xpath(f"//div[@id='pageNavigator']//a[text()='{next_page}']").click()

    def startScraping(self, searchWords):
        driver = WebdriverBuilder.getDriver()
        try:
            for searchWord in searchWords:
                print(f"현재검색어 {searchWord}")
                self.initSite(driver, searchWord)
                try:
                    for i in range(35):
                        print(f"현재페이지 {self.getCurrentPage(driver)}")
                        self.collectData(driver)
                        self.goNextPage(driver)
                        time.sleep(1.5)
                except Exception as e:
                    traceback.print_exc()
                    continue
        except Exception as e:
            traceback.print_exc()
        finally:
            driver.quit()





