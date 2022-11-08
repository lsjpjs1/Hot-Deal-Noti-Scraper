import random
from datetime import datetime
import os
import sys

import requests
from bs4 import BeautifulSoup
import bs4

from requests import Response
from selenium.webdriver.chrome.webdriver import WebDriver

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .Scraper import Scraper
from .WebdriverBuilder import WebdriverBuilder


class ProductPreview:
    def __init__(self, product_title, product_url, original_price, normal_discount_price, card_discount_percent,
                 normal_card_total_discount_percent,
                 is_more_discount_exist, thumbnail_url):
        self.product_title = product_title
        self.product_url = product_url
        self.original_price = original_price
        self.normal_discount_price = normal_discount_price
        self.card_discount_percent = card_discount_percent
        self.normal_card_total_discount_percent = normal_card_total_discount_percent
        self.is_more_discount_exist = is_more_discount_exist
        self.thumbnail_url = thumbnail_url

    def __str__(self):
        return self.product_title + "\n" + self.product_url + "\n" + str(self.original_price) + "\n" + str(
            self.card_discount_percent) + "\n" + str(self.normal_card_total_discount_percent) + "\n" + str(
            self.is_more_discount_exist) + "\n" + str(self.thumbnail_url) + "\n\n"


class ScraperCoupang(Scraper):
    candidate_products = []
    is_last_page = False
    item_count = 0

    def findCandidates(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("li", {"class": "baby-product renew-badge"})

        # 마지막 페이지 플래그 세팅
        if items is None:
            self.is_last_page = True
            print("items are None")
            return
        if len(items) <= 110:
            print("item size : ", len(items))
            self.is_last_page = True

        for item in items:
            item: bs4.element.Tag
            product_title = item.find("div", {"class": "name"}).get_text().replace("\n", "").strip()
            product_url = "https://www.coupang.com" + item.find("a", {"class": "baby-product-link"})["href"]

            first_price = None
            if item.find("del", {"class": "base-price"}) is not None:
                first_price = int(
                    item.find("del", {"class": "base-price"}).get_text().replace(",", "").replace("\n", "").replace(" ",
                                                                                                                    ""))

            second_price = None
            if item.find("strong", {"class": "price-value"}) is not None:
                second_price = int(
                    item.find("strong", {"class": "price-value"}).get_text().replace(",", "").replace("\n", "").replace(
                        " ", ""))

            original_price = None
            if first_price is not None:
                original_price = first_price
            elif second_price is not None:
                original_price = second_price
            else:
                continue

            normal_discount_price = original_price
            if second_price is not None:
                normal_discount_price = second_price

            normal_discount_percent = 0
            if item.find("span", {"class": "discount-percentage"}) is not None:
                normal_discount_text = item.find("span", {"class": "discount-percentage"}).get_text().replace("\n", "")
                try:
                    normal_discount_percent = int(re.findall("(\d)\%", normal_discount_text)[0])
                except Exception as e:
                    print(e)

            card_discount_percent = 0
            if item.find("span", {"class": "ccid-txt"}) is not None:
                card_discount_text = item.find("span", {"class": "ccid-txt"}).get_text().replace("\n", "")
                try:
                    card_discount_percent = int(re.findall("(\d)\%", card_discount_text)[0])
                except Exception as e:
                    print(e)

            normal_card_total_discount_percent = normal_discount_percent + card_discount_percent

            is_more_discount_exist = False
            if item.find("span", {"class": "badge badge-benefit"}) is not None:
                is_more_discount_exist = True

            thumbnail_url = ""
            if item.find("dt", {"class": "image"}) is not None:
                thumbnail_url = "https:" + item.find("dt", {"class": "image"}).find("img")["src"]

            product_preview = ProductPreview(product_title, product_url, original_price, normal_discount_price,
                                             card_discount_percent,
                                             normal_card_total_discount_percent, is_more_discount_exist, thumbnail_url)
            if self.validateCandidate(product_preview):
                self.candidate_products.append(product_preview)

    def validateCandidate(self, product_preview: ProductPreview):
        if product_preview.original_price < 200000:
            return False
        if product_preview.is_more_discount_exist:
            return True
        if product_preview.normal_card_total_discount_percent >= 15:
            return True
        return False

    def collectCandidate(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
        }
        for currentPage in range(1, 15):
            if not self.is_last_page:
                print("현재 페이지", currentPage)
                url = f'https://www.coupang.com/np/categories/497135?listSize=120&filterType=rocket&page={currentPage}'
                response = requests.get(url, headers=headers)
                self.findCandidates(response.text)
                time.sleep(random.randint(5, 7))

    def checkCandidates(self, driver: WebDriver):
        while self.candidate_products:
            self.item_count = self.item_count + 1
            print(f"현재 {self.item_count} 번째 아이템")
            try:
                candidate_product: ProductPreview = self.candidate_products.pop()
                driver.get(candidate_product.product_url)
                more_discount_amount = self.getMoreDiscountAmount(driver, candidate_product)
                card_discount_amount = self.getCardDiscountAmount(driver, candidate_product)
                total_discount_amount = candidate_product.original_price - candidate_product.normal_discount_price + more_discount_amount + card_discount_amount
                total_discount_percent = int(total_discount_amount / candidate_product.original_price * 100)
                if 15 <= total_discount_percent <= 100:
                    hot_deal = {
                        "discountRate": total_discount_percent,
                        "discountPrice": candidate_product.original_price - total_discount_amount,
                        "originalPrice": candidate_product.original_price, "title": candidate_product.product_title,
                        "url": candidate_product.product_url, "sourceSite": "쿠팡",
                        "hotDealThumbnailUrl": candidate_product.thumbnail_url
                    }
                    print(hot_deal)
                    self.mq.publish(json.dumps({"hotDealMessages": [hot_deal]}), 'inputHotDeal')
                driver.quit()
                driver = WebdriverBuilder.getDriver()
                time.sleep(random.randint(5, 10))
            except Exception as e:
                print(e)
                continue

    def getCardDiscountAmount(self, driver: WebDriver, product: ProductPreview):
        if product.card_discount_percent != 0:
            self.waitDuringTime(driver, (By.XPATH, "//div[@class='ccid-detail-tit']/a"), 10)
            driver.find_element_by_xpath("//div[@class='ccid-detail-tit']/a").click()
            self.waitDuringTime(driver, (By.XPATH, "//iframe[@class='card-benefit-popup__content-iframe']"), 10)
            driver.switch_to.frame(
                driver.find_element_by_xpath("//iframe[@class='card-benefit-popup__content-iframe']"))
            max_card_discount_amount = 0
            self.waitDuringTime(driver, (By.XPATH, "//span[@class='ccid-benefit__duration']/.."), 10)
            for ele in driver.find_elements_by_xpath("//span[@class='ccid-benefit__duration']/.."):
                max_card_discount_amount_area = re.findall("최대.*원", ele.text)
                if len(max_card_discount_amount_area) > 0:
                    max_card_discount_amount_area_str = max_card_discount_amount_area[0]
                    n_man_won = int(re.findall("(\d+)만", max_card_discount_amount_area_str)[0]) if len(
                        re.findall("(\d+)만", max_card_discount_amount_area_str)) > 0 else 0
                    n_chun_won = int(re.findall("(\d+)천", max_card_discount_amount_area_str)[0]) if len(
                        re.findall("(\d+)천", max_card_discount_amount_area_str)) > 0 else 0
                    max_card_discount_amount = max(n_man_won * 10000 + n_chun_won * 1000, max_card_discount_amount)
            return int(min(product.original_price * product.card_discount_percent / 100, max_card_discount_amount))
        else:
            return 0

    def getMoreDiscountAmount(self, driver: WebDriver, product: ProductPreview):
        if product.is_more_discount_exist:
            max_more_discount_amount = 0
            for coupon in driver.find_elements_by_xpath("//span[@class='prod-coupon-price']"):
                max_more_discount_amount = max(
                    int(coupon.get_attribute("innerHTML").replace(",", "").replace(" ", "").replace("원", "")),
                    max_more_discount_amount)
            return max_more_discount_amount
        else:
            return 0

    def startScraping(self):
        self.collectCandidate()
        print("후보 상품 개수: ", str(len(self.candidate_products)))
        driver = WebdriverBuilder.getDriver()
        try:
            self.checkCandidates(driver)
        except Exception as e:
            print(e)
        finally:
            driver.quit()


print(datetime.now(), ": 쿠팡 크롤링 시작합니다!")
scraperCoupang = ScraperCoupang()
scraperCoupang.startScraping()
