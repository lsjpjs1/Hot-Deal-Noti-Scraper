from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class WebdriverBuilder:
    @staticmethod
    def getDriver():
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        return webdriver.Chrome(chrome_options=chrome_options, executable_path=ChromeDriverManager().install())
