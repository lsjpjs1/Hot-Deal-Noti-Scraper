
import os
import sys
from datetime import datetime



sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from .Scraper11st import Scraper11st
from .ScraperGmarket import ScraperGmarket
from .ScraperLotteOn import ScraperLotteOn
from .ScraperAuction import ScraperAuction
from .ScraperHimart import ScraperHimart
from .ScraperCoupang import ScraperCoupang



searchWords = [
    "기가바이트 노트북", "asus 노트북", "lg 노트북", "삼성 노트북", "hp 노트북", "레노버 노트북", "델 노트북", "msi 노트북"
]
print(datetime.now(), ": 쿠팡 크롤링 시작합니다!")
scraperCoupang = ScraperCoupang()
scraperCoupang.startScraping()
print(datetime.now(),": 11번가 크롤링 시작합니다!")
scraper11st = Scraper11st()
scraper11st.startScraping(searchWords)
print(datetime.now(),": 지마켓 크롤링 시작합니다!")
scraper = ScraperGmarket()
scraper.startScraping(searchWords)
print(datetime.now(),": 롯데온 크롤링 시작합니다!")
scraper_lotte_on = ScraperLotteOn()
scraper_lotte_on.startScraping(searchWords)
print(datetime.now(),": 옥션 크롤링 시작합니다!")
scraper_auction = ScraperAuction()
scraper_auction.startScraping(searchWords)
print(datetime.now(),": 하이마트 크롤링 시작합니다!")
scraperHimart = ScraperHimart()
scraperHimart.startScraping(searchWords)

