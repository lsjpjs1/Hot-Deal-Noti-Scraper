import os
import sys

from selenium.webdriver import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .Scraper import Scraper
from .WebdriverBuilder import WebdriverBuilder


class IpChanger():


    def wait(self, driver, locator):
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    def waitDuringTime(self, driver, locator, waitTime):
        WebDriverWait(driver, waitTime).until(EC.presence_of_element_located(locator))

    def validateCoupang(self, driver):
        driver.get("https://www.coupang.com/")
        driver2 = WebdriverBuilder.getDriver()
        driver2.get(
            'https://www.coupang.com/vp/products/6884681205/item/16509749179/offers?selectedVendorItemId=83697119196')
        time.sleep(5)
        if len(re.findall("Access Denied",driver.page_source))>0:
            return False

        if len(re.findall("Access Denied",driver2.page_source))>0:
            return False
        driver2.quit()

        return True

    def getIptimeSite(self, driver):
        driver.get("http://192.168.0.1")

    def loginIptime(self, driver):
        self.waitDuringTime(driver, (By.XPATH, "//input[@name='username']"),15)
        driver.find_element_by_xpath("//input[@name='username']").send_keys("lsjpjs1")
        driver.find_element_by_xpath("//input[@name='passwd']").send_keys("vosejmouse92")
        time.sleep(5)
        driver.find_element_by_xpath("//img[@id='submit_bt']").click()

    def navigateIpSetUpPage(self, driver):
        driver.get("http://192.168.0.1/sess-bin/timepro.cgi?tmenu=netconf&smenu=wansetup")

    def changeMACAddress(self,driver):
        self.waitDuringTime(driver, (By.XPATH, "//input[@name='hw_dynamic6']"), 15)
        hex_str = "0x" + driver.find_element_by_xpath("//input[@name='hw_dynamic6']").get_attribute("value")
        dec = int(hex_str, 16)
        next_hex_str = hex((dec + 1) % 256)
        if len(next_hex_str) == 3:
            next_hex_str = "0" + next_hex_str[2:]
        else:
            next_hex_str = next_hex_str[2:]
        driver.find_element_by_xpath("//input[@name='hw_dynamic6']").clear()
        driver.find_element_by_xpath("//input[@name='hw_dynamic6']").send_keys(next_hex_str)
        self.waitDuringTime(driver, (By.XPATH, "//input[@id='appbtn']"), 15)
        driver.find_element_by_xpath("//input[@id='appbtn']").click()
        time.sleep(20)

    def startScraping(self):
        try:
            driver = WebdriverBuilder.getDriver()
            #쿠팡 접속 안되면 실행하는 조건문
            if not self.validateCoupang(driver):
                self.getIptimeSite(driver)
            #로그인
                self.loginIptime(driver)
            #로그인 완료시 아이피 설정화면으로 이동하는 로직
                self.navigateIpSetUpPage(driver)

            #맥주소 변경
                self.changeMACAddress(driver)

            #아이피 변경 쿠팡 접속될 때까지 반복

        finally:
            driver.quit()



IpChanger().startScraping()



