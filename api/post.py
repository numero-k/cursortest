from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from models.database import get_db_connection
from functools import wraps

post = Blueprint('post', __name__)

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@post.route('/posts')
@login_required
def list_posts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT p.*, u.name as author_name, 
            (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count,
            DATE_FORMAT(p.created_at, '%Y-%m-%d %H:%i') as formatted_date
            FROM posts p
            JOIN users u ON p.author_id = u.id
            ORDER BY p.created_at DESC
        ''')
        posts = cursor.fetchall()
        return render_template('main.html', posts=posts)
        
    except Exception as e:
        print(f"Error: {e}")  # 디버깅을 위한 에러 출력
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close()

@post.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.')
            return render_template('new_post.html')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO posts (title, content, author_id)
                VALUES (%s, %s, %s)
            ''', (title, content, session['user_db_id']))
            
            conn.commit()
            flash('게시글이 작성되었습니다.')
            return redirect(url_for('post.list_posts'))
            
        except Exception as e:
            conn.rollback()
            return redirect(url_for('post.create_post'))
            
        finally:
            cursor.close()
            conn.close()
            
    return render_template('new_post.html')

@post.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 게시글 조회
        cursor.execute('''
            SELECT p.*, u.name as author_name,
                   DATE_FORMAT(p.created_at, '%Y-%m-%d %H:%i') as formatted_date
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.id = %s
        ''', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash('게시글이 존재하지 않습니다.')
            return redirect(url_for('post.list_posts'))
        
        # 댓글 조회
        cursor.execute('''
            SELECT c.*, u.name as author_name,
                   DATE_FORMAT(c.created_at, '%Y-%m-%d %H:%i') as formatted_date
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        ''', (post_id,))
        comments = cursor.fetchall()
        
        return render_template('view_post.html', post=post, comments=comments)
        
    except Exception as e:
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close()

@post.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 게시글 조회
        cursor.execute('''
            SELECT * FROM posts WHERE id = %s
        ''', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash('게시글이 존재하지 않습니다.')
            return redirect(url_for('post.list_posts'))
        
        if post['author_id'] != session['user_db_id']:
            flash('게시글을 수정할 권한이 없습니다.')
            return redirect(url_for('post.view_post', post_id=post_id))
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            if not title or not content:
                flash('제목과 내용을 모두 입력해주세요.')
                return render_template('edit_post.html', post=post)
            
            cursor.execute('''
                UPDATE posts SET title = %s, content = %s WHERE id = %s
            ''', (title, content, post_id))
            conn.commit()
            
            flash('게시글이 수정되었습니다.')
            return redirect(url_for('post.view_post', post_id=post_id))
        
        return render_template('edit_post.html', post=post)
        
    except Exception as e:
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close()

@post.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 게시글 조회
        cursor.execute('''
            SELECT * FROM posts WHERE id = %s
        ''', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash('게시글이 존재하지 않습니다.')
            return redirect(url_for('post.list_posts'))
        
        if post['author_id'] != session['user_db_id']:
            flash('게시글을 삭제할 권한이 없습니다.')
            return redirect(url_for('post.view_post', post_id=post_id))
        
        cursor.execute('''
            DELETE FROM posts WHERE id = %s
        ''', (post_id,))
        conn.commit()
        
        flash('게시글이 삭제되었습니다.')
        return redirect(url_for('post.list_posts'))
        
    except Exception as e:
        return redirect(url_for('post.list_posts'))
        
    finally:
        cursor.close()
        conn.close()

# 메인 페이지를 게시글 목록으로 리다이렉트
@post.route('/')
def index():
    return redirect(url_for('post.list_posts')) 