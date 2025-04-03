from flask import Blueprint, request, session, redirect, url_for, render_template
from models.database import get_db_connection

post = Blueprint('post', __name__)

@post.route('/posts', methods=['GET'])
def list_posts():
    # 게시글 목록 조회

@post.route('/post/new', methods=['GET', 'POST'])
def create_post():
    # 게시글 생성

@post.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    # 게시글 조회 