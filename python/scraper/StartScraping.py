
import os
import sys
from datetime import datetime



sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from .Scraper11st import Scraper11st
from .ScraperGmarket import ScraperGmarket
from .ScraperLotteOn import ScraperLotteOn
from .ScraperAuction import ScraperAuction
from .ScraperHimart import ScraperHimart
from .ScraperWeMakePrice import ScraperWeMakePrice

# productTypeId = 2
# searchWords = [
#     "모니터"
# ]
#
# print(datetime.now(),": 위메프 크롤링 시작합니다!")
# ScraperWeMakePrice(productTypeId=productTypeId).startScraping([
#     'https://front.wemakeprice.com/category/division/2100135'
# ])
#
# print(datetime.now(),": 11번가 크롤링 시작합니다!")
# scraper11st = Scraper11st(productTypeId=productTypeId)
# scraper11st.startScraping(searchWords)
# print(datetime.now(),": 지마켓 크롤링 시작합니다!")
# scraper = ScraperGmarket(productTypeId=productTypeId)
# scraper.startScraping(searchWords)
# print(datetime.now(),": 롯데온 크롤링 시작합니다!")
# scraper_lotte_on = ScraperLotteOn(productTypeId=productTypeId)
# scraper_lotte_on.startScraping(searchWords)
#
# print(datetime.now(),": 하이마트 크롤링 시작합니다!")
# scraperHimart = ScraperHimart(productTypeId=productTypeId)
# scraperHimart.startScraping(searchWords)
# print(datetime.now(),": 옥션 크롤링 시작합니다!")
# scraper_auction = ScraperAuction(productTypeId=productTypeId)
# scraper_auction.startScraping(searchWords)


productTypeId = 1
searchWords = [
    "레노버 노트북","레이저 노트북","기가바이트 노트북", "asus 노트북", "lg 노트북", "노트북 삼성", "hp 노트북",  "델 노트북", "msi 노트북"
]

print(datetime.now(),": 11번가 크롤링 시작합니다!")
scraper11st = Scraper11st(productTypeId=productTypeId)
scraper11st.startScraping(searchWords)

# print(datetime.now(),": 위메프 크롤링 시작합니다!")
# ScraperWeMakePrice(productTypeId=productTypeId).startScraping([
#     'https://front.wemakeprice.com/category/division/2100132',
# 'https://front.wemakeprice.com/category/division/2100751',
# 'https://front.wemakeprice.com/category/division/2100753',
# 'https://front.wemakeprice.com/category/division/2100754',
# 'https://front.wemakeprice.com/category/division/2100755',
# 'https://front.wemakeprice.com/category/division/2100756',
# 'https://front.wemakeprice.com/category/division/2100757',
# 'https://front.wemakeprice.com/category/division/2100758',
# 'https://front.wemakeprice.com/category/division/2100759',
# 'https://front.wemakeprice.com/category/division/2100760',
# 'https://front.wemakeprice.com/category/division/2100761',
# 'https://front.wemakeprice.com/category/division/2100752'
# ])

print(datetime.now(),": 지마켓 크롤링 시작합니다!")
scraper = ScraperGmarket(productTypeId=productTypeId)
scraper.startScraping(searchWords)
print(datetime.now(),": 롯데온 크롤링 시작합니다!")
scraper_lotte_on = ScraperLotteOn(productTypeId=productTypeId)
scraper_lotte_on.startScraping(searchWords)

print(datetime.now(),": 하이마트 크롤링 시작합니다!")
scraperHimart = ScraperHimart(productTypeId=productTypeId)
scraperHimart.startScraping(searchWords)
print(datetime.now(),": 옥션 크롤링 시작합니다!")
scraper_auction = ScraperAuction(productTypeId=productTypeId)
scraper_auction.startScraping(searchWords)






