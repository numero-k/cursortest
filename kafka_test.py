from kafka import KafkaProducer
import json

try:
    producer = KafkaProducer(
        bootstrap_servers='your_kafka_server:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Kafka 연결 성공!")
except Exception as e:
    print(f"Kafka 연결 실패: {str(e)}") 