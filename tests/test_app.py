import pytest
from app import create_app
from models.database import init_db
import os

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE_PATH': 'instance/test.db',
        'SECRET_KEY': 'test_secret_key'
    })
    
    with app.app_context():
        init_db()
        yield app
        # 테스트 후 정리
        if os.path.exists('instance/test.db'):
            os.remove('instance/test.db')

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 302  # 로그인 페이지로 리다이렉트

def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page(client):
    response = client.get('/auth/register')
    assert response.status_code == 200

def test_post_list_page(client):
    response = client.get('/post/list')
    assert response.status_code == 302  # 로그인 페이지로 리다이렉트 