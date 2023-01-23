import os
import sys

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
        time.sleep(5)
        if len(re.findall("Access Denied",driver.page_source))>0:
            return False
        else:
            return True

    def getIptimeSite(self, driver):
        driver.get("http://192.168.0.1")

    def loginIptime(self, driver):
        self.waitDuringTime(driver, (By.XPATH, "//input[@name='username']"),15)
        driver.find_element_by_xpath("//input[@name='username']").send_keys("lsjpjs1")
        driver.find_element_by_xpath("//input[@name='passwd']").send_keys("vosejmouse92")
        driver.find_element_by_xpath("//img[@id='submit_bt']").click()

    def navigateIpSetUpPage(self, driver):
        self.waitDuringTime(driver, (By.XPATH, "//img[@src='/images2/login_main.newwizard.kr.gif']"),15)
        driver.execute_script("window.open('http://' + top.location.host + '/netinfo/waninfo/iux.cgi');")

    def startScraping(self):
        driver = WebdriverBuilder.getDriver()
        #쿠팡 접속 안되면 실행하는 조건문
        if not self.validateCoupang(driver):
            self.getIptimeSite(driver)
        #로그인
            self.loginIptime(driver)
        #로그인 완료시 아이피 설정화면으로 이동하는 로직

        #아이피 변경 쿠팡 접속될 때까지 반복



IpChanger().startScraping()



