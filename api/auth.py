from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_db_id'] = user['id']
                return redirect(url_for('post.list_posts'))
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            return redirect(url_for('auth.login'))
            
        finally:
            cursor.close()
            conn.close()
            
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        birthdate = request.form.get('birthdate')
        
        # 입력값 검증
        if not all([name, user_id, password, password_confirm, birthdate]):
            flash('모든 필드를 입력해주세요.')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.')
            return render_template('auth/register.html')
        
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            flash('비밀번호는 최소 8자 이상이며, 영문과 숫자를 포함해야 합니다.')
            return render_template('auth/register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 아이디 중복 검사
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            if cursor.fetchone():
                flash('이미 사용 중인 아이디입니다.')
                return render_template('auth/register.html')

            # 비밀번호 해시화 및 사용자 추가
            hashed_password = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (name, user_id, password, birthdate)
                VALUES (%s, %s, %s, %s)
            ''', (name, user_id, hashed_password, birthdate))
            
            conn.commit()
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            conn.rollback()
            return redirect(url_for('auth.register'))
            
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/register.html')

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