from flask import Blueprint, request, session, redirect, url_for, render_template
from models.database import get_db_connection
from functools import wraps

post = Blueprint('post', __name__)

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
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
            return redirect(url_for('post.create_post'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO posts (title, content, author_id)
                VALUES (%s, %s, %s)
            ''', (title, content, session['user_db_id']))
            
            conn.commit()
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

# 메인 페이지를 게시글 목록으로 리다이렉트
@post.route('/')
def index():
    return redirect(url_for('post.list_posts')) 