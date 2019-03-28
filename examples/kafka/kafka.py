import fire
from kafka import KafkaProducer
from kafka import KafkaConsumer


class KafkaFireExample:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def kafka_producer(self, topic_name='Hello Topic'):
        while True:
            self.producer.send(topic_name, b'Hello, World!')

    def kafka_consumer(self, topic_name='Hello Topic'):
        consumer = KafkaConsumer(topic_name)
        for message in consumer:
            return message


def main():
    fire.Fire(KafkaFireExample)


if __name__ == '__main__':
    main()
