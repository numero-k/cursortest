from flask import Flask
from api.auth import auth
from api.post import post
from api.comment import comment
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
socketio = SocketIO(app)

# 블루프린트 등록
app.register_blueprint(auth)
app.register_blueprint(post)
app.register_blueprint(comment)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 