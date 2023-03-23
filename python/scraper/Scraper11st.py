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
from .validationdiscount.ValidationDiscount11st import ValidationDiscount11st


class Scraper11st(Scraper):
    isPowerProduct = True
    validationDiscount = ValidationDiscount11st()
    res = {}

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
            except Exception as e:
                self.isPowerProduct = False
                print("파워상품->일반상품 전환")
        if not self.isPowerProduct:
            self.waitDuringTime(driver, (
                By.XPATH, "//section[@data-log-actionid-area='common']//div[@class='c_card c_card_list']"), 10)
            items = driver.find_elements_by_xpath(
                "//section[@data-log-actionid-area='common']//div[@class='c_card c_card_list']")

        comma_won_re = re.compile('([0-9]{1,3}(,[0-9]{3})+)')
        man_won_re = re.compile('([0-9]+)만')

        for item in items:
            sub_title = None
            try:
                original_title = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']").text
                title = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']").text.replace(" ",
                                                                                                                "").replace(
                    ".", "")
                url = item.find_element_by_xpath(".//div[@class='c_prd_name c_prd_name_row_1']/a").get_attribute("href")
                thumbnail_url = item.find_element_by_xpath(".//img").get_attribute("src")
                original_price = int(
                    item.find_element_by_xpath(".//dd//span[@class='value']").text.replace(",", ""))

                print(original_title)
                print(f"원가{original_price}")
                try:
                    sub_title = item.find_element_by_xpath(".//div[@class='c_prd_advertise']").text.replace(" ",
                                                                                                            "").replace(
                        ".", "")
                except Exception as e:
                    print("부제목 없음")
            except Exception as e:
                print(e)
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

            # 부제에서 특가정보 긁어오는 부분
            if sub_title:
                match_comma_sub = comma_won_re.finditer(sub_title)
                match_man_sub = man_won_re.finditer(sub_title)
                if match_comma_sub:
                    for comma_won in match_comma_sub:
                        price_candidates.append(int(comma_won[0].replace(",", "")))
                if match_man_sub:
                    for man_won in match_man_sub:
                        price_candidates.append(int(man_won[1]) * 10000)

            for price_candidate in price_candidates:
                if price_candidate / original_price > 0.5:
                    discount_list.append([int(100 - 100 * price_candidate / original_price), price_candidate, url])

            if discount_list:
                print(discount_list[0][0])
                if 15 <= discount_list[0][0] <= 100 and original_price > 200000:
                    hot_deal = {
                        "discountRate": discount_list[0][0], "discountPrice": discount_list[0][1],
                        "originalPrice": original_price, "title": original_title,
                        "url": discount_list[0][2], "sourceSite": "11번가",
                        "hotDealThumbnailUrl": thumbnail_url
                    }

                    self.res.get("hotDealMessages").append(
                        hot_deal
                    )

        # self.mq.publish(json.dumps(res), 'inputHotDeal')
        # self.mq.publish(json.dumps(res), 'inputKeywordNotification')

    def getCurrentPage(self, driver):
        self.wait(driver, (By.XPATH, "//li[@class='active']"))
        return int(driver.find_element_by_xpath("//li[@class='active']").text)

    def goNextPage(self, driver):
        current_page = self.getCurrentPage(driver)
        print(f"{current_page}페이지 완료")
        if current_page % 10 == 0:
            self.wait(driver, (By.XPATH, "//li[@class='next']/a"))
            driver.find_element_by_xpath("//li[@class='next']/a").click()
        else:
            next_page = str(current_page + 1)
            self.wait(driver, (By.XPATH, f"//a[text()='{next_page}']"))
            driver.find_element_by_xpath(f"//a[text()='{next_page}']").click()

    def startScraping(self, searchWords):
        self.res = {"hotDealMessages": [], "productTypeId": self.productTypeId}
        driver = WebdriverBuilder.getDriver()
        try:
            for searchWord in searchWords:
                print(f"현재검색어 : {searchWord}")
                self.initSite(driver, searchWord)
                try:
                    for i in range(15):
                        self.collectData(driver)
                        self.goNextPage(driver)
                        time.sleep(1)
                        print(len(self.res.get("hotDealMessages")))
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    continue
        except Exception as e:
            print(e)
            traceback.print_exc()
        finally:

            for hotDeal in self.res.get("hotDealMessages"):
                (isValid, realPrice) = self.validationDiscount.validateDiscount(hotDeal["url"],
                                                                                hotDeal["discountPrice"])
                if isValid:
                    hotDeal["discountPrice"] = realPrice
                    print("hit")
                    print(hotDeal)
                    self.mq.publish(json.dumps({"hotDealMessages": [hotDeal], "productTypeId": self.productTypeId}),
                                    'inputClassifyHotDealCosine')

            driver.quit()
            self.validationDiscount.driver.quit()
