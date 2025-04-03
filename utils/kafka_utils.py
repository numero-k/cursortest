from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Kafka 프로듀서를 전역 변수로 선언
producer = None

def init_kafka_producer():
    global producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return True
    except Exception as e:
        print(f"Kafka 연결 실패: {e}")
        return False

def send_notification(notification_data):
    global producer
    if producer is None:
        if not init_kafka_producer():
            print("Kafka 연결 실패로 알림을 전송할 수 없습니다.")
            return
    
    try:
        producer.send('notifications', notification_data)
        producer.flush()
    except Exception as e:
        print(f"알림 전송 실패: {e}") 