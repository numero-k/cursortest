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
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka 연결 성공")
        return True
    except Exception as e:
        print(f"Kafka 연결 실패: {e}")
        return False

def send_notification(topic, message):
    if producer is None:
        print("Kafka 프로듀서가 초기화되지 않았습니다.")
        return False
    
    try:
        producer.send(topic, message)
        producer.flush()
        return True
    except Exception as e:
        print(f"Kafka 메시지 전송 실패: {e}")
        return False 