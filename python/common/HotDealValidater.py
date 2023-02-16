import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2

from ..messagequeue.RabbitMQ import RabbitMQ

class HotDealValidater:
    mq = RabbitMQ()
    def validateHotDeal(self,hotDealJson):
        # 1. 디비에서 프로덕트 제목 목록 쭉 가져오기
        conn = None
        try:
            conn = psycopg2.connect(host="hot-deal-noti-db-1.ccgzvp0lrzfk.ap-northeast-2.rds.amazonaws.com",
                                    dbname="hotDealNotification", user="Rudder", password="forRudder")
        except:
            print("DB Not Connected!.")
            return
        cur = conn.cursor()
        cur.execute("select product_id, model_name from product;")
        products = cur.fetchall()

        hotDeals = hotDealJson["hotDealMessages"]
        for hotDeal in hotDeals:
            # 2. for문 돌면서 코사인 유사도 제일 높은 것 뽑기
            max_similarity = 0
            result_product_id = 1
            result_model_name = ''
            for (product_id, candidate_model_name) in products:
                tfidf_vectorizer = TfidfVectorizer()
                tfidf_matrix = tfidf_vectorizer.fit_transform((hotDeal["title"], candidate_model_name))
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                if similarity>max_similarity:
                    max_similarity = similarity
                    result_product_id = product_id
                    result_model_name = candidate_model_name
            hotDeal["candidateProductId"] = result_product_id
            print(hotDeal["title"])
            print(result_model_name, max_similarity)
            print("")
        print(hotDealJson)
        self.mq.publish(json.dumps(hotDealJson), 'inputHotDeal')
        # 3-1. 코사인 유사도 n 이상인 경우 최저가 보다 싸면 큐에 등록

        # 3-2. 코사인 유사도 n 이하인 경우 주의 표시와 함께 표시 일단 제품명은 그걸로 매칭하고 대신 최저가 검증 안하고 큐에 보내기

