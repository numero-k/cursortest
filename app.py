from flask import Flask, render_template, redirect, url_for
from api.auth import auth_bp
from api.post import post_bp
from api.comment import comment_bp
from api.notification import notification_bp
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from kafka import KafkaConsumer
import json
import threading
from utils.kafka_utils import init_kafka_producer
import logging
from config import Config

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # SocketIO 초기화
    socketio = SocketIO(app)
    
    # 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(notification_bp, url_prefix='/notification')
    
    # 메인 페이지 리다이렉션
    @app.route('/')
    def index():
        return redirect(url_for('post.list_posts'))
    
    return app, socketio

# Kafka 컨슈머 스레드
def kafka_consumer_thread():
    try:
        consumer = KafkaConsumer(
            'notifications',
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='flask_notification_group',
            auto_offset_reset='latest'
        )
        
        logger.info("Kafka 컨슈머 시작")
        
        for message in consumer:
            try:
                notification = message.value
                logger.info(f"새로운 알림 수신: {notification}")
                socketio.emit('notification', notification)
                logger.info("알림 전송 완료")
            except Exception as e:
                logger.error(f"알림 처리 중 오류 발생: {e}")
                
    except Exception as e:
        logger.error(f"Kafka 컨슈머 초기화 실패: {e}")

# Kafka 연결 시도
kafka_available = init_kafka_producer()

if kafka_available:
    # Kafka가 사용 가능한 경우에만 컨슈머 스레드 시작
    kafka_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    kafka_thread.start()
else:
    print("Kafka 사용 불가 - 알림 기능이 비활성화됩니다.")

# 커스텀 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app, socketio = create_app()
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False) 