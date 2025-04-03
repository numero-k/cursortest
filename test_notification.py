from kafka import KafkaProducer
import json
from datetime import datetime
import time

def test_notification():
    # Kafka 프로듀서 설정
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # 테스트 알림 메시지
    test_notifications = [
        {
            'type': 'new_comment',
            'post_id': 1,
            'post_title': '테스트 게시글 1',
            'commenter': '테스트 사용자 B',
            'receiver': 'test_user_a',  # 수신할 사용자 ID
            'timestamp': datetime.now().isoformat()
        },
        {
            'type': 'new_comment',
            'post_id': 2,
            'post_title': '테스트 게시글 2',
            'commenter': '테스트 사용자 C',
            'receiver': 'test_user_a',
            'timestamp': datetime.now().isoformat()
        }
    ]

    # 각 테스트 알림 전송
    for notification in test_notifications:
        try:
            producer.send('notifications', notification)
            producer.flush()
            print(f"알림 전송 성공: {notification}")
            time.sleep(2)  # 2초 간격으로 전송
        except Exception as e:
            print(f"알림 전송 실패: {e}")

    producer.close()

if __name__ == '__main__':
    test_notification() 