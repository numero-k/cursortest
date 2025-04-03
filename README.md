# Flask 게시판 프로젝트

## 설치 방법

1. 저장소 클론
```bash
git clone <repository-url>
cd <project-directory>
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
- `.env.example` 파일을 복사하여 `.env` 파일 생성
- `.env` 파일에 실제 설정 값 입력
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

5. 서버 실행
```bash
python app.py
```

## 환경 변수 설정

다음 환경 변수들을 `.env` 파일에 설정해야 합니다:

- `DB_HOST`: 데이터베이스 호스트 주소
- `DB_PORT`: 데이터베이스 포트 (기본값: 3306)
- `DB_USER`: 데이터베이스 사용자 이름
- `DB_PASSWORD`: 데이터베이스 비밀번호
- `DB_NAME`: 데이터베이스 이름
- `SECRET_KEY`: Flask 애플리케이션 시크릿 키 