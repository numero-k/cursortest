from flask import Blueprint, request, session, redirect, url_for
from models.database import get_db_connection
from utils.kafka_utils import send_notification

comment = Blueprint('comment', __name__)

@comment.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    # 댓글 작성

@comment.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    # 댓글 수정

@comment.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    # 댓글 삭제 