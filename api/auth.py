from flask import Blueprint, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('post.list_posts'))
            else:
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            return redirect(url_for('auth.login'))
            
        finally:
            cursor.close()
            conn.close()
            
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        user_id = request.form['user_id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        birthdate = request.form['birthdate']

        # 입력값 검증
        if not name or len(name) < 2:
            return redirect(url_for('auth.register'))

        if not is_valid_userid(user_id):
            return redirect(url_for('auth.register'))

        if not is_valid_password(password):
            return redirect(url_for('auth.register'))

        if password != password_confirm:
            return redirect(url_for('auth.register'))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 아이디 중복 검사
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            if cursor.fetchone():
                return redirect(url_for('auth.register'))

            # 비밀번호 해시화 및 사용자 추가
            hashed_password = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (name, user_id, password, birthdate)
                VALUES (%s, %s, %s, %s)
            ''', (name, user_id, hashed_password, birthdate))
            
            conn.commit()
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            conn.rollback()
            return redirect(url_for('auth.register'))
            
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def is_valid_userid(user_id):
    pattern = re.compile(r'^[a-zA-Z0-9]{4,20}$')
    return bool(pattern.match(user_id))

def is_valid_password(password):
    pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,20}$')
    return bool(pattern.match(password)) 