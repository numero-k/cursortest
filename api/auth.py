from flask import Blueprint, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 기존 로그인 로직

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # 기존 회원가입 로직

@auth.route('/logout')
def logout():
    # 기존 로그아웃 로직 