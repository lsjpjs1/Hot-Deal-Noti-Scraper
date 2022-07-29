import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from .Scraper11st import Scraper11st
from .ScraperGmarket import ScraperGmarket

searchWords = [
    "기가바이트 노트북", "asus 노트북", "lg 노트북", "삼성 노트북", "hp 노트북", "레노버 노트북", "델 노트북"
]
scraper11st = Scraper11st()
scraper11st.startScraping(searchWords)


searchWords = [
    "노트북"
]
scraper = ScraperGmarket()
scraper.startScraping(searchWords)
