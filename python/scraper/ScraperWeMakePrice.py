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


class ScraperWeMakePrice(Scraper):
    candidate_collection_links = set()
    def initSite(self, driver, searchPage):
        driver.get(searchPage)

    def collectData(self, driver):
        self.waitDuringTime(driver, (By.XPATH, "//div[@class='desc_btnarea']//span"), 10)
        items = driver.find_elements_by_xpath("//div[@class='desc_btnarea']//span/../../../..")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages": [], "productTypeId": self.productTypeId}
        for item in items:
            try:
                original_title = item.find_element_by_xpath(".//div[@class='item_img']/img").get_attribute("alt")
                url = item.get_attribute("href")
                title = original_title.replace(" ","").replace(".", "")
                if len(re.findall("모음|기획",title)) > 0:
                    self.candidate_collection_links.add(url)
                    continue
                thumbnail_url = item.find_element_by_xpath(".//div[@class='item_img']/img").get_attribute("src")
                if thumbnail_url == None:
                    thumbnail_url = item.find_element_by_xpath(".//div[@class='item_img']/img").get_attribute("data-lazy-src")
                original_price = None
                try:
                    original_price = int(
                    item.find_element_by_xpath(".//div[@class='price_text']//span[@class='num']").text.replace(",", ""))
                except Exception as e:
                    print("할인 없음")
                    continue

                discount_price = None
                try:
                    discount_price = int(
                    item.find_element_by_xpath(".//div[@class='price_info']//em[@class='num']").text.replace(",", ""))
                except Exception as e:
                    print("할인 없음")
                    continue
                print(original_title)

            except Exception as e:
                print(e)
                traceback.print_exc()
                continue

            discount_rate = int(((original_price-discount_price)/original_price)*100)

            if 15 <= discount_rate <= 100 and discount_price>200000 and len(re.findall("중고|리퍼|반품",title))==0:
                hot_deal = {
                    "discountRate": discount_rate, "discountPrice": discount_price,
                    "originalPrice": original_price, "title": original_title,
                    "url": url, "sourceSite": "위메프",
                    "hotDealThumbnailUrl": thumbnail_url
                }
                print(hot_deal)
                print("")
                res.get("hotDealMessages").append(
                    hot_deal
                )
        self.mq.publish(json.dumps(res), 'inputClassifyHotDealCosine')
        # self.mq.publish(json.dumps(res), 'inputHotDeal')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def getCurrentPage(self, driver):
        self.wait(driver, (By.XPATH, "//li[@class='active']"))
        return int(driver.find_element_by_xpath("//li[@class='active']").text)

    def goNextPage(self, driver):
        self.wait(driver, (By.XPATH, "//a[@class='ico btn_next']"))
        driver.find_element_by_xpath("//a[@class='ico btn_next']").click()

    def collectDataFromLinks(self, driver):
        res = {"hotDealMessages": [], "productTypeId": self.productTypeId}
        while self.candidate_collection_links:
            candidate_collection_link = self.candidate_collection_links.pop()
            driver.get(candidate_collection_link)
            try:
                self.wait(driver, (By.XPATH, "//ul[@id='_itemslist']//li[@data-option='list']"))
                items = driver.find_elements_by_xpath("//ul[@id='_itemslist']//li[@data-option='list']")
                for item in items:
                    original_title = item.find_element_by_xpath(".//p[@class='text']").text
                    url = candidate_collection_link
                    title = original_title.replace(" ", "").replace(".", "")
                    thumbnail_url = item.find_element_by_xpath(".//div[@class='item_img']//img").get_attribute("src")
                    if thumbnail_url == None:
                        thumbnail_url = item.find_element_by_xpath(".//div[@class='item_img']//img").get_attribute(
                            "data-lazy-src").strip()
                    original_price = None
                    try:
                        original_price = int(
                            item.find_element_by_xpath(".//span[@class='sale']//span[@class='num']").text.replace(",",
                                                                                                                  ""))
                    except Exception as e:
                        print("할인 없음")
                        continue

                    discount_price = None
                    try:
                        discount_price = int(
                            item.find_element_by_xpath(".//span[@class='cp_price']//strong").text.replace(",", ""))
                    except Exception as e:
                        print("할인 없음2")
                        continue
                    discount_rate = int(((original_price - discount_price) / original_price) * 100)

                    if 15 <= discount_rate <= 100 and discount_price > 200000 and len(
                            re.findall("중고|리퍼|반품", title)) == 0:
                        hot_deal = {
                            "discountRate": discount_rate, "discountPrice": discount_price,
                            "originalPrice": original_price, "title": original_title,
                            "url": url, "sourceSite": "위메프",
                            "hotDealThumbnailUrl": thumbnail_url
                        }
                        print(hot_deal)
                        print("")
                        res.get("hotDealMessages").append(
                            hot_deal
                        )
            except:
                traceback.print_exc()
                continue
        self.mq.publish(json.dumps(res), 'inputClassifyHotDealCosine')

    def startScraping(self, searchPages):
        driver = WebdriverBuilder.getDriver()
        try:
            for searchPage in searchPages:
                print(f"현재페이지 : {searchPage}")
                self.initSite(driver, searchPage=searchPage)
                try:
                    for i in range(3):
                        self.collectData(driver)
                        self.goNextPage(driver)
                        time.sleep(1)
                    self.collectDataFromLinks(driver)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    continue
        except Exception as e:
            print(e)
            traceback.print_exc()
        finally:
            driver.quit()



