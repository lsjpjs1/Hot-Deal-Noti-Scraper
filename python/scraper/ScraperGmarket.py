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


class ScraperGmarket(Scraper):

    def initSite(self, driver, searchWord):
        driver.get("https://www.gmarket.co.kr/")
        self.wait(driver, (By.XPATH, "//input[@title='검색창']"))
        driver.find_element_by_xpath("//input[@title='검색창']").send_keys(searchWord)
        driver.find_element_by_xpath("//button[@class='button__search']").click()

    def collectData(self, driver):

        self.waitDuringTime(driver, (
            By.XPATH,
            "//div[@class='box__item-container']"),
                            10)
        items = driver.find_elements_by_xpath(
            "//div[@class='box__item-container']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')
        res = {"hotDealMessages":[]}

        page_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, page_height, 40):
            j = i + 1
            driver.execute_script(f"window.scrollTo({i}, {j})")

        for item in items:
            try:
                original_title = item.find_element_by_xpath(".//span[@class='text__item']").text
                title = original_title.replace(" ", "").replace(".", "")
                url = item.find_element_by_xpath(".//a[@class='link__item']").get_attribute("href")

                original_price = int(
                    item.find_element_by_xpath(".//strong[@class='text text__value']").text.replace(",", ""))
                thumbnail_url = item.find_element_by_xpath(".//img[@class='image__item  ']").get_attribute("src")

                coupon_discount_percent = 0
                try:
                    coupon_discount_percent = int(re.findall("([0-9]+)%",item.find_element_by_xpath(".//span[@class='box__tag box__tag-coupon']").text)[0])
                except:
                    pass

                card_discount_percent = 0
                try:
                    card_discount_percent = int(re.findall("([0-9]+)%",item.find_element_by_xpath(".//span[@class='box__tag box__tag-card']").text)[0])
                except:
                    pass

                real_original_price = original_price
                try:
                    real_original_price = int(
                    item.find_element_by_xpath(".//div[@class='box__price-original']//span[@class='text text__value']").text.replace(",", ""))
                except:
                    pass

            except Exception as e:
                traceback.print_exc()
                print(e)
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
                if 12 <= discount_list[0][0] <= 100:
                    hot_deal = {
                                    "discountRate": discount_list[0][0], "discountPrice": discount_list[0][1],
                                    "originalPrice": original_price, "title": original_title,
                                    "url": discount_list[0][2], "sourceSite": "G마켓",
                            "hotDealThumbnailUrl" : thumbnail_url
                                }
                    res.get("hotDealMessages").append(
                                hot_deal
                    )
                    print(hot_deal)
                continue

            # if 12 <=card_discount_percent + coupon_discount_percent <=100:
            #     second_driver = WebdriverBuilder.getDriver()
            #     second_driver.get(url)
            #
            #     card_discount_amount = real_original_price*card_discount_percent/100
            #     try:
            #         card_discount_amount = min(self.getCardDiscountAmount(second_driver),card_discount_amount)
            #     except:
            #         print("카드할인 검색에러")
            #         pass
            #
            #
            #     coupon_discount_amount = real_original_price * coupon_discount_percent / 100
            #     try:
            #         coupon_discount_amount = min(self.getCouponDiscountAmount(second_driver), coupon_discount_amount)
            #     except:
            #         print("쿠폰할인 검색에러")
            #         pass
            #     print(f"원가 {original_price}")
            #     print(f"카드할인 {card_discount_amount}")
            #     print(f"쿠폰할인 {coupon_discount_amount}")
            #
            #     total_discount_rate = round((card_discount_amount + coupon_discount_amount) / original_price * 100)
            #     if 12 <= total_discount_rate <=100:
            #         hot_deal = {
            #                 "discountRate": total_discount_rate, "discountPrice": int(original_price-card_discount_amount-coupon_discount_amount),
            #                 "originalPrice": original_price, "title": original_title,
            #                 "url": url, "sourceSite": "G마켓",
            #                 "hotDealThumbnailUrl": thumbnail_url
            #             }
            #         res.get("hotDealMessages").append(
            #             hot_deal
            #         )
            #         print("2유형 할인")
            #         print(url)
            #         print(hot_deal)
            #     second_driver.quit()


        self.mq.publish(json.dumps(res), 'inputHotDeal')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def getCouponDiscountAmount(self, driver):
        self.wait(driver, (By.XPATH, "//a[@class='box__coupon']"))
        driver.find_element_by_xpath("//a[@class='box__coupon']").click()
        self.wait(driver, (By.XPATH, "//button[@class='button__detail js-button_detail']"))
        card_discount_text = driver.find_element_by_xpath("//button[@class='button__detail js-button_detail']").text
        return int(re.findall(" ([0-9]+)만원", card_discount_text)[0]) * 10000

    def getCardDiscountAmount(self, driver):
        self.wait(driver, (By.XPATH, "//li[@class='list-item-credticard uxeslide_item']"))
        driver.find_element_by_xpath("//li[@class='list-item-credticard uxeslide_item']").click()
        self.wait(driver, (By.XPATH, "//li[@class='list-item-credticard uxeslide_item on']//em[@class='text__card-title']/..//ul/li"))
        max_card_discount_amount = 0
        for element in driver.find_elements_by_xpath(
                "//li[@class='list-item-credticard uxeslide_item on']//em[@class='text__card-title']/..//ul/li"):
            try:
                card_discount_amount = int(re.findall("최대 (.*)원", element.text)[0].replace(",", "").replace(" ", ""))
                max_card_discount_amount = max(max_card_discount_amount,card_discount_amount)
            except:
                pass
        return max_card_discount_amount

    def goNextPage(self, driver):
        self.wait(driver, (By.XPATH, "//a[@class='link__page-next']"))
        driver.execute_script("arguments[0].click();", driver.find_element_by_xpath("//a[@class='link__page-next']"))

    def printCurrentPage(self, driver):
        try:
            self.wait(driver, (By.XPATH, "//span[@class='link__page link--on']"))
            print(driver.find_element_by_xpath(".//span[@class='link__page link--on']/span").text)
        except Exception as e:
            print("현재페이지 표시 에러")

    def startScraping(self, searchWords):
        driver = WebdriverBuilder.getDriver()
        try:
            for searchWord in searchWords:
                print(f"현재검색어: {searchWord}")
                self.initSite(driver, searchWord)
                try:
                    for i in range(25):
                        self.printCurrentPage(driver)
                        self.collectData(driver)
                        self.goNextPage(driver)
                        time.sleep(1)
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    continue
        except Exception as e:
            traceback.print_exc()
            print(e)
        finally:
            driver.quit()

