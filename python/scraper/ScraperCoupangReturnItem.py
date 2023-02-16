import random
from datetime import datetime
import os
import sys
import traceback

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
from .CoupangPartnersLinkGenerator import CoupangPartnersLinkGenerator

class ProductPreview:
    NORMAL = "NORMAL"
    SOLD_OUT = "SOLD_OUT"
    ONLY_RETURN = "ONLY_RETURN"

    def __init__(self, product_title, product_url, original_price, normal_discount_price, card_discount_percent,
                 normal_card_total_discount_percent,
                 is_more_discount_exist, thumbnail_url, check_more_discount, sale_status):
        self.product_title = product_title
        self.product_url = product_url
        self.original_price = original_price
        self.normal_discount_price = normal_discount_price
        self.card_discount_percent = card_discount_percent
        self.normal_card_total_discount_percent = normal_card_total_discount_percent
        self.is_more_discount_exist = is_more_discount_exist
        self.thumbnail_url = thumbnail_url
        self.check_more_discount = check_more_discount
        self.sale_status = sale_status

    def __str__(self):
        return self.product_title + "\n" + self.product_url + "\n" + str(self.original_price) + "\n" + str(
            self.card_discount_percent) + "\n" + str(self.normal_card_total_discount_percent) + "\n" + str(
            self.is_more_discount_exist) + "\n" + str(self.thumbnail_url) + "\n" + str(
            self.check_more_discount) + "\n" + str(self.sale_status) + "\n\n"


class ScraperCoupangReturnItem(Scraper):
    candidate_products = []
    is_last_page = False
    item_count = 0

    def __init__(self,target_page):
        self.target_page = target_page

    def findCandidates(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_=re.compile('baby-product renew-badge'))

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
                pass

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

            check_more_discount = False
            if item.find("span", {"class": "badge badge-benefit"}) is not None and item.find("span", {
                "class": "instant-discount-text"}) is not None:
                instant_discount_text = item.find("span", {"class": "instant-discount-text"}).get_text()
                if len(re.findall("와우쿠폰", instant_discount_text)) == 0:
                    check_more_discount = True

            thumbnail_url = ""
            if item.find("dt", {"class": "image"}) is not None:
                thumbnail_url = "https:" + item.find("dt", {"class": "image"}).find("img")["src"]

            sale_status = ProductPreview.NORMAL
            if item.find("div", {"class": "out-of-stock"}) is not None:
                sale_status = ProductPreview.SOLD_OUT
            if item.find("strong", {"class": "price-value"}) is None:
                sale_status = ProductPreview.ONLY_RETURN

            product_preview = ProductPreview(product_title, product_url, original_price, normal_discount_price,
                                             card_discount_percent,
                                             normal_card_total_discount_percent, is_more_discount_exist, thumbnail_url,
                                             check_more_discount, sale_status)
            self.candidate_products.append(product_preview)

    def collectCandidate(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            'Cache-Control': 'no-cache'
        }
        target_page = self.target_page
        for currentPage in range(target_page, target_page+1):
            if not self.is_last_page:
                print("현재 페이지", currentPage)
                url = f'https://www.coupang.com/np/categories/497135?listSize=120&brand=42308%2C259%2C263%2C6619%2C258%2C17000%2C257%2C16890%2C17031%2C17350&offerCondition=PACKAGE_DAMAGED%2CNON_ACTIVATED%2CREPACKAGING%2CREFURBISHED%2CUSED%2CRETURN&filterType=rocket%2Crocket_wow%2Ccoupang_global&isPriceRange=false&minPrice=&maxPrice=&page={currentPage}&channel=user&fromComponent=N&selectedPlpKeepFilter=&sorter=bestAsc&filter=&component=497035&rating=0&rocketAll=true'
                response = requests.get(url, headers=headers)
                self.findCandidates(response.text)
                time.sleep(random.randint(5, 7))

    def checkCandidates(self, driver: WebDriver):
        while self.candidate_products:
            time.sleep(2)
            self.item_count = self.item_count + 1
            print(f"현재 {self.item_count} 번째 아이템")
            try:
                candidate_product: ProductPreview = self.candidate_products.pop()
                product_id = re.search('products/(\d+)', candidate_product.product_url).group(1)
                item_id = re.search('itemId=(\d+)', candidate_product.product_url).group(1)
                vendor_item_id = re.search('vendorItemId=(\d+)', candidate_product.product_url).group(1)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                    "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
                    'Cache-Control': 'no-cache',
                    "Pragma": "no-cache",
                }
                url = f'https://www.coupang.com/vp/products/{product_id}/item/{item_id}/offers?selectedVendorItemId={vendor_item_id}'
                response = requests.get(url, headers=headers)
                return_item_info_json = response.json()['vendorItems'][0]

                # 정상 케이스 - 일반 쿠팡 크롤링 하는 과정 거친 가격과 비교
                if candidate_product.sale_status == ProductPreview.NORMAL:
                    original_price = self.getDiscountPrice(driver, candidate_product)
                    driver.quit()
                    driver = WebdriverBuilder.getDriver()
                # 품절 케이스 - 반품 화면에 적혀있는 가격으로만 가져옴
                elif candidate_product.sale_status == ProductPreview.SOLD_OUT:
                    original_price = int(return_item_info_json["vendorItemSaleInfo"]["salePrice"])
                # 반품 상품만 있는 케이스 - 반품 화면에 적혀있는 가격으로만 가져옴
                elif candidate_product.sale_status == ProductPreview.ONLY_RETURN:
                    original_price = int(int(return_item_info_json["vendorItemSaleInfo"]["salePrice"]))

                discount_price = int(int(return_item_info_json["vendorItemSaleInfo"]["couponPrice"]))
                discount_percent = 100 - int(discount_price * 100 / original_price)

                return_item_quality = return_item_info_json["badgeMap"]["OFFER_BADGE"]["text"]
                return_item_quality_detail = return_item_info_json["badgeMap"]["USAGE_BADGE"]["text"]
                return_item_vendor_item_id = str(return_item_info_json["vendorItemId"])
                return_item_url = f"https://www.coupang.com/vp/products/{product_id}?itemId={item_id}&vendorItemId={return_item_vendor_item_id}&landingType=USED_DETAIL"

                if 15 <= discount_percent <= 100 and return_item_quality != "새 상품":

                    # try:
                    #     return_item_url = CoupangPartnersLinkGenerator.getCoupangPartnersLink(return_item_url)
                    # except Exception as e:
                    #     print(e)
                    # print(return_item_url)
                    hot_deal = {
                        "discountRate": discount_percent,
                        "discountPrice": discount_price,
                        "originalPrice": original_price, "title": candidate_product.product_title,
                        "url": return_item_url, "sourceSite": "쿠팡",
                        "hotDealThumbnailUrl": candidate_product.thumbnail_url,
                        "returnItemQuality": return_item_quality,
                        "returnItemQualityDetail": return_item_quality_detail,
                        "returnItemSaleStatus": candidate_product.sale_status
                    }
                    print(hot_deal)
                    self.mq.publish(json.dumps({"hotDealMessages": [hot_deal]}), 'inputClassifyHotDealCosine')
            except Exception as e:
                print(candidate_product.product_title)
                traceback.print_exc()
                print(e)
                driver = WebdriverBuilder.getDriver()
                continue

    def getDiscountPrice(self, driver: WebDriver, candidate_product: ProductPreview):
        driver.get(candidate_product.product_url)

        more_discount_amount = 0
        if candidate_product.check_more_discount:
            more_discount_amount = self.getMoreDiscountAmount(driver, candidate_product)

        card_discount_amount = self.getCardDiscountAmount(driver, candidate_product)
        total_discount_amount = candidate_product.original_price - candidate_product.normal_discount_price + more_discount_amount + card_discount_amount
        total_discount_percent = int(total_discount_amount / candidate_product.original_price * 100)
        discount_price = candidate_product.original_price - total_discount_amount
        return discount_price

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



for i in range(10,0,-1):
    start_time = datetime.now()
    print(datetime.now(), f": 쿠팡 반품 {i}페이지 크롤링 시작합니다!")
    scraperCoupang = ScraperCoupangReturnItem(i)
    scraperCoupang.startScraping()
    print("시작시간 : ", start_time)
    print(datetime.now(), f": 쿠팡 반품 {i}페이지 크롤링 종료합니다!")
