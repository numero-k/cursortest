from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
from functools import wraps
from markupsafe import Markup
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 데이터베이스 연결 함수
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# 데이터베이스 초기화 함수
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # users 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            user_id VARCHAR(20) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            birthdate DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # posts 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            author_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    
    # comments 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            author_id INT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# 아이디 유효성 검사 함수
def is_valid_userid(user_id):
    pattern = re.compile(r'^[a-zA-Z0-9]{4,20}$')
    return bool(pattern.match(user_id))

# 비밀번호 유효성 검사 함수
def is_valid_password(password):
    pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,20}$')
    return bool(pattern.match(password))

# nl2br 필터 추가
@app.template_filter('nl2br')
def nl2br(value):
    if not value:
        return ''
    return Markup(value.replace('\n', '<br>'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['user_name'] = user['name']
                session['user_db_id'] = user['id']
                flash('로그인 성공!', 'success')
                return redirect(url_for('main'))
            else:
                flash('아이디 또는 비밀번호가 잘못되었습니다.', 'error')
                
        except mysql.connector.Error as err:
            flash(f'로그인 중 오류가 발생했습니다: {err}', 'error')
            
        finally:
            cursor.close()
            conn.close()
            
    return render_template('login.html')

@app.route('/main')
@login_required
def main():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT p.*, u.name as author_name, 
        (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
        FROM posts p
        JOIN users u ON p.author_id = u.id
        ORDER BY p.created_at DESC
    ''')
    posts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('main.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.', 'error')
            return redirect(url_for('new_post'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO posts (title, content, author_id)
                VALUES (%s, %s, %s)
            ''', (title, content, session['user_db_id']))
            
            conn.commit()
            flash('게시글이 작성되었습니다.', 'success')
            return redirect(url_for('main'))
            
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'게시글 작성 중 오류가 발생했습니다: {err}', 'error')
            
        finally:
            cursor.close()
            conn.close()
            
    return render_template('new_post.html')

@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 게시글 조회
        cursor.execute('''
            SELECT p.*, u.name as author_name, 
                   DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i') as formatted_date
            FROM posts p
            JOIN users u ON p.author_id = u.id
            WHERE p.id = %s
        ''', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash('존재하지 않는 게시글입니다.', 'error')
            return redirect(url_for('main'))
        
        # 댓글 조회
        cursor.execute('''
            SELECT c.*, u.name as author_name,
                   DATE_FORMAT(c.created_at, '%%Y-%%m-%%d %%H:%%i') as formatted_date
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        ''', (post_id,))
        comments = cursor.fetchall()
        
        return render_template('view_post.html', post=post, comments=comments)
        
    except mysql.connector.Error as err:
        flash(f'게시글을 불러오는 중 오류가 발생했습니다: {err}', 'error')
        return redirect(url_for('main'))
        
    finally:
        cursor.close()
        conn.close()

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form['content']
    
    if not content:
        flash('댓글 내용을 입력해주세요.', 'error')
        return redirect(url_for('view_post', post_id=post_id))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO comments (post_id, author_id, content)
            VALUES (%s, %s, %s)
        ''', (post_id, session['user_db_id'], content))
        
        conn.commit()
        flash('댓글이 작성되었습니다.', 'success')
        
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'댓글 작성 중 오류가 발생했습니다: {err}', 'error')
        
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        user_id = request.form['user_id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        birthdate = request.form['birthdate']

        # 입력값 검증
        if not name or len(name) < 2:
            flash('이름은 2자 이상이어야 합니다.', 'error')
            return redirect(url_for('register'))

        if not is_valid_userid(user_id):
            flash('아이디는 영문과 숫자 조합으로 4~20자여야 합니다.', 'error')
            return redirect(url_for('register'))

        if not is_valid_password(password):
            flash('비밀번호는 8~20자의 영문, 숫자, 특수문자를 포함해야 합니다.', 'error')
            return redirect(url_for('register'))

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 아이디 중복 검사
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            if cursor.fetchone():
                flash('이미 존재하는 아이디입니다.', 'error')
                return redirect(url_for('register'))

            # 비밀번호 해시화 및 사용자 추가
            hashed_password = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (name, user_id, password, birthdate)
                VALUES (%s, %s, %s, %s)
            ''', (name, user_id, hashed_password, birthdate))
            
            conn.commit()
            flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
            return redirect(url_for('login'))
            
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'회원가입 중 오류가 발생했습니다: {err}', 'error')
            return redirect(url_for('register'))
            
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 