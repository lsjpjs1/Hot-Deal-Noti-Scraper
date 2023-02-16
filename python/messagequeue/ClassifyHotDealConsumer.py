import pika
import os
from dotenv import load_dotenv
import json


from ..common.HotDealValidater import HotDealValidater

class ClassifyHotDealConsumer:
    def __init__(self):
        load_dotenv()
        self.__url = os.environ.get('RabbitMQUrl')
        self.__port = 5672
        self.__vhost = os.environ.get('RabbitMQVhost')
        self.__cred = pika.PlainCredentials(
            os.environ.get('RabbitMQId'),
            os.environ.get('RabbitMQPassword')
        )
        self.__queue = 'classifyHotDealCosine';
        return

    def on_message(channel, method_frame, header_frame, body):
        hotDealJson = json.loads(body)
        HotDealValidater().validateHotDeal(hotDealJson)

    def main(self):
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
            chan = conn.channel()
            chan.basic_consume(
                queue=self.__queue,
                on_message_callback=ClassifyHotDealConsumer.on_message,
                auto_ack=True
            )
            print('Consumer is starting...')
            chan.start_consuming()
            return
        except Exception as e:
            print(e)
            self.main()


consumer = ClassifyHotDealConsumer()
consumer.main()