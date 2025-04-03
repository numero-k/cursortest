# 빈 파일로 두어도 됩니다 

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
post_bp = Blueprint('post', __name__)
comment_bp = Blueprint('comment', __name__)
notification_bp = Blueprint('notification', __name__)

from . import auth, post, comment, notification 