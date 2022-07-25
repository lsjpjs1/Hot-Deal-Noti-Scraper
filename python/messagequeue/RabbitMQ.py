import os

import pika
from dotenv import load_dotenv


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

    def publish(self, body):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        connection.channel().basic_publish(exchange='amq.direct', routing_key='inputHotDeal', body=body)
        connection.close()


# mq = RabbitMQ()
# mq.publish(json.dumps({"hotDealMessages": [
#     {
#         "discountRate": 1, "discountPrice": 1,
#         "originalPrice": 1, "title": "original_title",
#         "url": "discount_list[0][2]"
#     }
# ]}))
