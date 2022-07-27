from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from RabbitMQ import RabbitMQ


class Scraper:
    result = pd.DataFrame({"할인율": [], "할인가": [], "제목": [], "url": []})
    mq = RabbitMQ()

    def wait(self, driver, locator):
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    def waitDuringTime(self, driver, locator, waitTime):
        WebDriverWait(driver, waitTime).until(EC.presence_of_element_located(locator))
