# Flask 게시판 프로젝트

## 기능 목록

### 사용자 관리
- 회원가입
- 로그인/로그아웃
- 사용자 인증

### 게시판
- 게시글 작성
- 게시글 조회
- 댓글 기능
  - 댓글 작성
  - 댓글 수정 (작성자만 가능)
  - 댓글 삭제 (작성자만 가능)

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

## 최근 업데이트 (2024-04-03)
- 댓글 수정 기능 추가
  - 작성자 본인만 수정 가능
  - 인라인 수정 폼 제공
- 댓글 삭제 기능 추가
  - 작성자 본인만 삭제 가능
  - 삭제 전 확인 절차 추가 