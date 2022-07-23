import pandas as pd
import pika
from dotenv import load_dotenv
import os


class RabbitMQ:
    def __init__(self):
        load_dotenv()
        self.__url = os.environ.get('RabbitMQUrl')
        self.__port = 5672
        self.__vhost = os.environ.get('RabbitMQVhost')
        self.__cred = pika.PlainCredentials(
            os.environ.get('RabbitMQId'),
            os.environ.get('RabbitMQPassword')
        )
        return

    def publish(self,body):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        connection.channel().basic_publish(exchange='amq.direct',routing_key='hi',body=body)
        connection.close()


# frame = pd.DataFrame({"aa": [], "bb": [], "cc": [], "url": []})
# frame = frame.append({"aa": 13, "bb": 10000, "cc": "하이", "url": "www.naver.com"},ignore_index=True)
# mq = RabbitMQ()
# mq.publish(frame.to_json())
