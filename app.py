from flask import Flask, redirect, url_for
from flask_socketio import SocketIO
from api import auth_bp, post_bp, comment_bp, notification_bp
from models.database import init_db, init_app as init_db_app
from utils.kafka_utils import init_kafka_producer
from config import Config
import os
import logging
from kafka import KafkaConsumer
import json
import threading

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 데이터베이스 초기화
    init_db_app(app)
    
    # 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(notification_bp, url_prefix='/notification')
    
    # Kafka 초기화
    if init_kafka_producer():
        logger.info("Kafka 연결 성공")
    else:
        logger.warning("Kafka 연결 실패")
    
    # 메인 페이지 리다이렉션
    @app.route('/')
    def index():
        return redirect(url_for('post.list_posts'))
    
    return app

def create_socketio(app):
    socketio = SocketIO(app)
    
    def kafka_consumer():
        try:
            consumer = KafkaConsumer(
                'notifications',
                bootstrap_servers=[app.config['KAFKA_BOOTSTRAP_SERVERS']],
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            for message in consumer:
                notification = message.value
                socketio.emit('notification', notification)
                logger.info(f"알림 전송: {notification}")
                
        except Exception as e:
            logger.error(f"Kafka 소비자 오류: {e}")
    
    # Kafka 소비자 스레드 시작
    if init_kafka_producer():
        consumer_thread = threading.Thread(target=kafka_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Kafka 소비자 스레드 시작")
    
    return socketio

def init_app():
    app = create_app()
    socketio = create_socketio(app)
    
    # 데이터베이스 초기화
    with app.app_context():
        init_db()
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = init_app()
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False) 