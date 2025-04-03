from flask import Blueprint, request, session, redirect, url_for
from models.database import get_db_connection
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
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@comment.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    
    if not content:
        return redirect(url_for('post.view_post', post_id=post_id))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 댓글 저장
        cursor.execute('''
            INSERT INTO comments (post_id, author_id, content)
            VALUES (%s, %s, %s)
        ''', (post_id, session['user_db_id'], content))
        
        # 게시글 작성자 정보 조회
        cursor.execute('''
            SELECT p.title, u.user_id, u.name as author_name
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.id = %s
        ''', (post_id,))
        post_info = cursor.fetchone()
        
        # 자신의 게시글이 아닌 경우에만 알림 발송 시도
        if post_info and post_info['user_id'] != session['user_id']:
            try:
                notification = {
                    'type': 'new_comment',
                    'post_id': post_id,
                    'post_title': post_info['title'],
                    'commenter': session['user_name'],
                    'receiver': post_info['user_id'],
                    'timestamp': datetime.now().isoformat()
                }
                send_notification('notifications', notification)
            except Exception as e:
                print(f"알림 전송 실패: {e}")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('post.view_post', post_id=post_id))

@comment.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    content = request.form.get('content')
    
    if not content:
        return redirect(url_for('post.list_posts'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT post_id, author_id FROM comments 
            WHERE id = %s
        ''', (comment_id,))
        comment_data = cursor.fetchone()
        
        if not comment_data or comment_data['author_id'] != session['user_db_id']:
            return redirect(url_for('post.list_posts'))
        
        cursor.execute('''
            UPDATE comments 
            SET content = %s 
            WHERE id = %s AND author_id = %s
        ''', (content, comment_id, session['user_db_id']))
        
        conn.commit()
        return redirect(url_for('post.view_post', post_id=comment_data['post_id']))
        
    except Exception as e:
        conn.rollback()
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close()

@comment.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT post_id, author_id FROM comments 
            WHERE id = %s
        ''', (comment_id,))
        comment_data = cursor.fetchone()
        
        if not comment_data or comment_data['author_id'] != session['user_db_id']:
            return redirect(url_for('post.list_posts'))
        
        cursor.execute('''
            DELETE FROM comments 
            WHERE id = %s AND author_id = %s
        ''', (comment_id, session['user_db_id']))
        
        conn.commit()
        return redirect(url_for('post.view_post', post_id=comment_data['post_id']))
        
    except Exception as e:
        conn.rollback()
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close() 