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
import os
import hmac
import hashlib
import requests
import json
from time import gmtime, strftime


class CoupangPartnersLinkGenerator:
    REQUEST_METHOD = "POST"
    DOMAIN = "https://api-gateway.coupang.com"
    URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"

    # Replace with your own ACCESS_KEY and SECRET_KEY
    ACCESS_KEY = os.environ.get('CoupangPartnersAccessKey')
    SECRET_KEY = os.environ.get('CoupangPartnersSecretKey')

    @staticmethod
    def generateHmac(method, url, secretKey, accessKey):
        path, *query = url.split("?")
        datetimeGMT = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'
        message = datetimeGMT + method + path + (query[0] if query else "")

        signature = hmac.new(bytes(secretKey, "utf-8"),
                             message.encode("utf-8"),
                             hashlib.sha256).hexdigest()

        return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(accessKey, datetimeGMT,
                                                                                              signature)

    @staticmethod
    def getCoupangPartnersLink(coupang_link):
        authorization = CoupangPartnersLinkGenerator.generateHmac(CoupangPartnersLinkGenerator.REQUEST_METHOD,
                                                                  CoupangPartnersLinkGenerator.URL,
                                                                  CoupangPartnersLinkGenerator.SECRET_KEY,
                                                                  CoupangPartnersLinkGenerator.ACCESS_KEY)
        url = "{}{}".format(CoupangPartnersLinkGenerator.DOMAIN, CoupangPartnersLinkGenerator.URL)
        response = requests.request(method=CoupangPartnersLinkGenerator.REQUEST_METHOD, url=url,
                                    headers={
                                        "Authorization": authorization,
                                        "Content-Type": "application/json"
                                    },
                                    data=json.dumps({"coupangUrls": [coupang_link]})
                                    )

        return response.json()["data"][0]["shortenUrl"]
