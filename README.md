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

### 실시간 알림 시스템 (Kafka 기반)
- 새 댓글 알림
- 실시간 사용자 활동 로깅
- 비동기 이메일 알림

## 기술 스택

### 백엔드
- Python 3.x
- Flask
- MySQL
- Apache Kafka

### 프론트엔드
- HTML/CSS
- JavaScript
- Socket.IO

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

## 환경 변수 설정

다음 환경 변수들을 `.env` 파일에 설정해야 합니다:

### 데이터베이스 설정
- `DB_HOST`: 데이터베이스 호스트 주소
- `DB_PORT`: 데이터베이스 포트 (기본값: 3306)
- `DB_USER`: 데이터베이스 사용자 이름
- `DB_PASSWORD`: 데이터베이스 비밀번호
- `DB_NAME`: 데이터베이스 이름

### Kafka 설정
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka 서버 주소 (예: localhost:9092)
- `KAFKA_NOTIFICATION_TOPIC`: 알림용 토픽 이름
- `KAFKA_ACTIVITY_LOG_TOPIC`: 활동 로깅용 토픽 이름
- `KAFKA_EMAIL_NOTIFICATION_TOPIC`: 이메일 알림용 토픽 이름

### 기타 설정
- `SECRET_KEY`: Flask 애플리케이션 시크릿 키

## Kafka 기능

### 실시간 알림
- 새 댓글 작성 시 게시글 작성자에게 실시간 알림
- WebSocket을 통한 브라우저 알림 표시
- 알림 이력 저장 및 조회

### 활동 로깅
- 사용자 활동 자동 기록
- 시스템 감사(audit) 로그 생성
- 활동 통계 데이터 수집

### 비동기 작업 처리
- 이메일 알림 비동기 처리
- 대용량 작업 비동기 처리
- 외부 서비스 연동

## 시작하기

1. 서버 실행
```bash
python app.py
```

2. Kafka 서버 실행 확인
```bash
# Kafka 연결 테스트
python kafka_test.py
```

## 주의사항
- Kafka 서버가 실행 중이어야 실시간 알림 기능이 동작합니다.
- 실시간 알림을 위해서는 WebSocket 연결이 필요합니다.
- 환경 변수 설정이 올바르게 되어있는지 확인하세요.

## 최근 업데이트 (2024-04-03)
- 댓글 수정 기능 추가
  - 작성자 본인만 수정 가능
  - 인라인 수정 폼 제공
- 댓글 삭제 기능 추가
  - 작성자 본인만 삭제 가능
  - 삭제 전 확인 절차 추가

## API 명세서

### 인증 API

#### 로그인
- **URL:** `/login`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "user_id": "string",
    "password": "string"
  }
  ```
- **Response:**
  - 성공: 메인 페이지로 리다이렉트
  - 실패: 로그인 페이지로 리다이렉트

#### 회원가입
- **URL:** `/register`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "name": "string",
    "user_id": "string",
    "password": "string",
    "password_confirm": "string",
    "birthdate": "YYYY-MM-DD"
  }
  ```
- **Response:**
  - 성공: 로그인 페이지로 리다이렉트
  - 실패: 회원가입 페이지로 리다이렉트

#### 로그아웃
- **URL:** `/logout`
- **Method:** `GET`
- **Response:** 로그인 페이지로 리다이렉트

### 게시글 API

#### 게시글 목록 조회
- **URL:** `/posts`
- **Method:** `GET`
- **Query Parameters:**
  - `page` (optional): 페이지 번호
- **Response:** 게시글 목록 페이지

#### 게시글 작성
- **URL:** `/post/new`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "title": "string",
    "content": "string"
  }
  ```
- **Response:**
  - 성공: 게시글 목록으로 리다이렉트
  - 실패: 게시글 작성 페이지로 리다이렉트

#### 게시글 조회
- **URL:** `/post/<post_id>`
- **Method:** `GET`
- **Response:** 게시글 상세 페이지

### 댓글 API

#### 댓글 작성
- **URL:** `/post/<post_id>/comment`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "content": "string"
  }
  ```
- **Response:** 게시글 상세 페이지로 리다이렉트

#### 댓글 수정
- **URL:** `/comment/<comment_id>/edit`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "content": "string"
  }
  ```
- **Response:** 게시글 상세 페이지로 리다이렉트

#### 댓글 삭제
- **URL:** `/comment/<comment_id>/delete`
- **Method:** `POST`
- **Response:** 게시글 상세 페이지로 리다이렉트

### 실시간 알림 API (WebSocket)

#### 알림 구독
- **Event:** `connect`
- **Description:** 클라이언트가 WebSocket 연결을 시작할 때 호출

#### 알림 수신
- **Event:** `notification`
- **Data Format:**
  ```json
  {
    "type": "string",
    "post_id": "number",
    "post_title": "string",
    "commenter": "string",
    "receiver": "string",
    "timestamp": "string"
  }
  ```

## 응답 코드

- `200`: 성공
- `301`, `302`: 리다이렉션
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `500`: 서버 오류

## 인증

- 대부분의 API는 로그인이 필요합니다.
- 로그인하지 않은 상태에서 접근 시 로그인 페이지로 리다이렉트됩니다.
- 세션을 통해 사용자 인증을 관리합니다. 