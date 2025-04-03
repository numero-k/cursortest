from flask import Blueprint, request, session, redirect, url_for, flash
from models.database import get_db
from functools import wraps
from utils.kafka_utils import send_notification
from datetime import datetime
import json

comment = Blueprint('comment', __name__)

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@comment.route('/post/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    
    if not content:
        flash('댓글 내용을 입력해주세요.')
        return redirect(url_for('post.view_post', post_id=post_id))
    
    db = get_db()
    
    # 게시글 작성자 확인
    post = db.execute('SELECT author_id FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        flash('게시글이 존재하지 않습니다.')
        return redirect(url_for('post.list_posts'))
    
    # 댓글 작성
    db.execute(
        'INSERT INTO comments (content, post_id, author_id) VALUES (?, ?, ?)',
        (content, post_id, session['user_id'])
    )
    db.commit()
    
    # 게시글 작성자에게 알림 전송 (자신의 게시글에 댓글을 달은 경우 제외)
    if post['author_id'] != session['user_id']:
        post_title = db.execute('SELECT title FROM posts WHERE id = ?', (post_id,)).fetchone()['title']
        commenter = db.execute('SELECT name FROM users WHERE id = ?', (session['user_id'],)).fetchone()['name']
        
        notification_data = {
            'type': 'new_comment',
            'post_id': post_id,
            'post_title': post_title,
            'commenter': commenter,
            'receiver': post['author_id']
        }
        send_notification(notification_data)
    
    flash('댓글이 작성되었습니다.')
    return redirect(url_for('post.view_post', post_id=post_id))

@comment.route('/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    content = request.form.get('content')
    
    if not content:
        flash('댓글 내용을 입력해주세요.')
        return redirect(url_for('post.view_post', post_id=post_id))
    
    db = get_db()
    comment = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    
    if not comment:
        flash('댓글이 존재하지 않습니다.')
        return redirect(url_for('post.list_posts'))
    
    if comment['author_id'] != session['user_id']:
        flash('댓글을 수정할 권한이 없습니다.')
        return redirect(url_for('post.view_post', post_id=comment['post_id']))
    
    db.execute(
        'UPDATE comments SET content = ? WHERE id = ?',
        (content, comment_id)
    )
    db.commit()
    
    flash('댓글이 수정되었습니다.')
    return redirect(url_for('post.view_post', post_id=comment['post_id']))

@comment.route('/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    db = get_db()
    comment = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    
    if not comment:
        flash('댓글이 존재하지 않습니다.')
        return redirect(url_for('post.list_posts'))
    
    if comment['author_id'] != session['user_id']:
        flash('댓글을 삭제할 권한이 없습니다.')
        return redirect(url_for('post.view_post', post_id=comment['post_id']))
    
    db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    db.commit()
    
    flash('댓글이 삭제되었습니다.')
    return redirect(url_for('post.view_post', post_id=comment['post_id'])) 