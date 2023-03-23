import re
import time
import traceback

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from .AbstractValidationDiscount import AbstractValidationDiscount
from ..WebdriverBuilder import WebdriverBuilder


class ValidationDiscount11st(AbstractValidationDiscount):

    driver = None

    def login(self, driver):
        self.wait(driver, (By.XPATH, "//a[@data-log-actionid-label='login']"))
        driver.find_element_by_xpath("//a[@data-log-actionid-label='login']").send_keys(Keys.ENTER)
        self.wait(driver, (By.XPATH, "//input[@id='memId']"))
        driver.find_element_by_xpath("//input[@id='memId']").send_keys("vosejmouse98")
        driver.find_element_by_xpath("//input[@id='memPwd']").send_keys("!aa667383")
        driver.find_element_by_xpath("//button[@data-log-actionid-label='login']").send_keys(Keys.ENTER)
        time.sleep(1)
        self.waitUntilClickable(driver, (By.XPATH, "//a[@data-log-actionid-label='cancel']"))
        driver.find_element_by_xpath("//a[@data-log-actionid-label='cancel']").send_keys(Keys.ENTER)
        time.sleep(1)

    def getTotalCouponDiscountAmount(self, driver):
        totalCouponDiscountAmount = 0
        shoppingCardDiscountAmount = 0
        try:
            self.waitUntilClickable(driver, (By.XPATH, "//button[@data-log-actionid-label='coupon']"))
            driver.find_element_by_xpath("//button[@data-log-actionid-label='coupon']").send_keys(Keys.ENTER)

            maxCoupons = list()
            self.wait(driver, (By.XPATH, "//ul[@class='r-coupon-down__list']"))
            try:
                couponLists = driver.find_elements_by_xpath("//ul[@class='r-coupon-down__list']")
                for couponList in couponLists:
                    couponPriceList = couponList.find_elements_by_xpath(
                        ".//span[@class='r-couponbox__price']")
                    maxCouponAmount = 0
                    for couponPrice in couponPriceList:
                        candidateCouponAmount = int(couponPrice.text.replace(",", "").replace("원", "").strip())
                        maxCouponAmount = max(maxCouponAmount, candidateCouponAmount)
                    if len(couponList.find_elements_by_xpath(".//span[@class='r-couponbox__icon-store' and contains(text(), '장바구니')]"))>0:
                        shoppingCardDiscountAmount = maxCouponAmount
                    maxCoupons.append(maxCouponAmount)
            except:
                traceback.print_exc()

            for maxCoupon in maxCoupons:
                totalCouponDiscountAmount += maxCoupon
        except:
            traceback.print_exc()
        return (totalCouponDiscountAmount,shoppingCardDiscountAmount)

    def getCardDiscountAmount(self, driver, discountedPrice):
        cardDiscountAmount = 0
        try:
            cardDiscountText = driver.find_element_by_xpath("//button[contains(text(), '카드결제 최대')]").text
            cardDiscountRate = int(re.findall("(\d+)%", cardDiscountText)[0])
            cardDiscountAmount = int(discountedPrice * cardDiscountRate / 100)
        except:
            traceback.print_exc()
        return cardDiscountAmount

    def getOriginalPrice(self,driver):
        originalPrice = None
        try:
            originalPrice = int(driver.find_element_by_xpath("//dl[@class='price_regular']//span[@class='value']").get_attribute(
                "innerHTML").replace(",", ""))
        except:
            pass
        if originalPrice == None:
            try:
                originalPrice = int(
                    driver.find_element_by_xpath("//dl[@class='price']//span[@class='value']").get_attribute(
                        "innerHTML").replace(",", ""))
            except:
                pass
        return originalPrice

    def getRealPrice(self, driver):
        self.wait(driver, (By.XPATH, "//div[contains(@class,'c_product_info_title')]"))
        originalPrice = self.getOriginalPrice(driver)
        if originalPrice==None:
            return None
        (couponDiscountAmount,shoppingCardDiscountAmount) = self.getTotalCouponDiscountAmount(driver)
        couponDiscountedPrice = originalPrice - couponDiscountAmount
        cardDiscountAmount = self.getCardDiscountAmount(driver,couponDiscountedPrice+shoppingCardDiscountAmount)
        print(originalPrice)
        print(couponDiscountAmount)
        print(couponDiscountedPrice+shoppingCardDiscountAmount)
        print(cardDiscountAmount)
        print(couponDiscountedPrice-cardDiscountAmount)
        finalPrice = couponDiscountedPrice-cardDiscountAmount
        return finalPrice


    def validateDiscount(self, productPageUrl: str, discountPrice: int):
        try:
            if self.driver == None:
                self.driver = WebdriverBuilder.getDriver()
                self.driver.get("https://www.11st.co.kr/")
                self.login(self.driver)

            self.driver.get(productPageUrl)
            realPrice = self.getRealPrice(self.driver)

            if realPrice==None:
                return (False,None)

            if realPrice - discountPrice < 20000:
                return (True,realPrice)
            else:
                return (False,None)
        except:
            print(productPageUrl)
            traceback.print_exc()
            return (False,None)





