from flask import Flask
from api.auth import auth
from api.post import post
from api.comment import comment
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
socketio = SocketIO(app)

# 환경 설정
app.config.update(
    DEBUG=False,  # 디버그 모드 비활성화
    ENV='production',  # 환경을 프로덕션으로 설정
    # 보안 관련 설정 추가
    SESSION_COOKIE_SECURE=True,  # HTTPS에서만 쿠키 전송
    SESSION_COOKIE_HTTPONLY=True,  # JavaScript에서 세션 쿠키 접근 방지
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF 공격 방지
    PERMANENT_SESSION_LIFETIME=1800  # 세션 만료 시간 30분으로 설정
)

# 블루프린트 등록
app.register_blueprint(auth)
app.register_blueprint(post)
app.register_blueprint(comment)

# 커스텀 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 환경 변수에서 포트 설정을 가져오거나 기본값 사용
    port = int(os.getenv('PORT', 5000))
    
    # 프로덕션 설정으로 실행
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False  # 프로덕션에서는 reloader 비활성화
    ) 