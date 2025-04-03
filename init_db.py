import os
from models.database import init_db

def main():
    # instance 디렉토리 생성
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # 데이터베이스 초기화
    init_db()
    print("데이터베이스가 초기화되었습니다.")

if __name__ == '__main__':
    main() 