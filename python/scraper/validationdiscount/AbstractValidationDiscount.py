import abc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class AbstractValidationDiscount(abc.ABC):

    @abc.abstractmethod
    def validateDiscount(self, productPageUrl: str, discountPrice: int):
        pass

    @abc.abstractmethod
    def getRealPrice(self, driver):
        pass

    @abc.abstractmethod
    def login(self, driver):
        pass

    def wait(self, driver, locator):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    def waitUntilClickable(self, driver, locator):
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))