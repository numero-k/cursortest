from models.database import get_db_connection
import os

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # schema.sql 파일 읽기
        with open('schema.sql', 'r') as f:
            sql_commands = f.read()
        
        # 각 명령어 실행
        for command in sql_commands.split(';'):
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("데이터베이스 초기화 완료")
        
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db() 