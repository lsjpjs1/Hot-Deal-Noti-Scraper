from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class WebdriverBuilder:
    @staticmethod
    def getDriver():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(chrome_options=chrome_options, executable_path=ChromeDriverManager().install())
