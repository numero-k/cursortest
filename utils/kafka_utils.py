from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_notification(topic, message):
    producer.send(topic, message) 