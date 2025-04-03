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
- API 구조 모듈화
- Kafka 기반 실시간 알림 시스템 추가
- 프로젝트 구조 개선
- Docker 컨테이너화 추가

## 프로젝트 구조
```
cursor test/
├── api/              # API 모듈
├── models/           # 데이터베이스 모델
├── utils/            # 유틸리티 함수
├── static/           # 정적 파일
├── templates/        # HTML 템플릿
├── app.py           # 메인 애플리케이션
├── config.py        # 설정 파일
├── Dockerfile       # Docker 이미지 설정
├── docker-compose.yml # Docker Compose 설정
└── README.md
```

## Docker로 실행하기

### 사전 요구사항
- Docker
- Docker Compose

### 환경 설정
1. `.env.example` 파일을 `.env`로 복사하고 필요한 환경 변수를 설정합니다:
```bash
cp .env.example .env
```

2. `.env` 파일에서 다음 설정을 확인/수정합니다:
```
SECRET_KEY=your-secret-key-here
```

### 실행 방법
1. Docker 이미지 빌드 및 컨테이너 실행:
```bash
docker-compose up --build
```

2. 백그라운드에서 실행:
```bash
docker-compose up -d
```

3. 컨테이너 중지:
```bash
docker-compose down
```

4. 로그 확인:
```bash
docker-compose logs -f
```

### 컨테이너 정보
- 웹 애플리케이션: http://localhost:5000
- Kafka: localhost:9092
- Zookeeper: localhost:2181

### 볼륨
- `instance/`: SQLite 데이터베이스 파일
- `logs/`: 애플리케이션 로그 파일

### 네트워크
- `app-network`: 모든 서비스가 연결된 브릿지 네트워크

## API 명세서

### 인증 API (auth)

#### 로그인
- **엔드포인트**: `/auth/login`
- **메소드**: `POST`
- **요청 데이터**:
  ```json
  {
    "user_id": "string",
    "password": "string"
  }
  ```
- **응답**: 로그인 성공 시 메인 페이지로 리다이렉트

#### 회원가입
- **엔드포인트**: `/auth/register`
- **메소드**: `POST`
- **요청 데이터**:
  ```json
  {
    "name": "string",
    "user_id": "string",
    "password": "string",
    "password_confirm": "string",
    "birthdate": "YYYY-MM-DD"
  }
  ```
- **응답**: 회원가입 성공 시 로그인 페이지로 리다이렉트

#### 로그아웃
- **엔드포인트**: `/auth/logout`
- **메소드**: `GET`
- **응답**: 로그인 페이지로 리다이렉트

### 게시글 API (post)

#### 게시글 목록 조회
- **엔드포인트**: `/post/list`
- **메소드**: `GET`
- **응답**: 게시글 목록 페이지

#### 게시글 작성
- **엔드포인트**: `/post/create`
- **메소드**: `POST`
- **요청 데이터**:
  ```json
  {
    "title": "string",
    "content": "string"
  }
  ```
- **응답**: 게시글 목록으로 리다이렉트

#### 게시글 조회
- **엔드포인트**: `/post/<int:post_id>`
- **메소드**: `GET`
- **응답**: 게시글 상세 페이지

### 댓글 API (comment)

#### 댓글 작성
- **엔드포인트**: `/comment/post/<int:post_id>`
- **메소드**: `POST`
- **요청 데이터**:
  ```json
  {
    "content": "string"
  }
  ```
- **응답**: 게시글 상세 페이지로 리다이렉트

#### 댓글 수정
- **엔드포인트**: `/comment/<int:comment_id>/edit`
- **메소드**: `POST`
- **요청 데이터**:
  ```json
  {
    "content": "string"
  }
  ```
- **응답**: 게시글 상세 페이지로 리다이렉트

#### 댓글 삭제
- **엔드포인트**: `/comment/<int:comment_id>/delete`
- **메소드**: `POST`
- **응답**: 게시글 상세 페이지로 리다이렉트

### 알림 API (notification)

#### WebSocket 이벤트

##### 연결
- **이벤트**: `connect`
- **설명**: 클라이언트 WebSocket 연결 시 호출

##### 알림 수신
- **이벤트**: `notification`
- **데이터 형식**:
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

## 인증 및 권한

### 로그인 필요
- 게시글 작성/수정/삭제
- 댓글 작성/수정/삭제
- 알림 수신

### 작성자 권한
- 댓글 수정/삭제는 작성자만 가능

## 실시간 알림 시스템

### Kafka 토픽
- `notifications`: 새 댓글 알림

### 알림 종류
- 새 댓글 알림
  - 게시글 작성자에게 전송
  - 댓글 작성자 정보 포함
  - 게시글 제목 포함

## 설치 및 실행

### 요구사항
- Python 3.x
- MySQL
- Apache Kafka

### 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 환경 설정
1. `.env.example`을 `.env`로 복사
2. 데이터베이스 및 Kafka 설정 입력

### 실행
```bash
# 데이터베이스 초기화
python init_db.py

# 애플리케이션 실행
python app.py
```

## 테스트

### 알림 시스템 테스트
```bash
# 테스트 스크립트 실행
python test_notification.py
```

## 보안 설정
- 디버그 모드 비활성화
- HTTPS 강제
- 세션 보안 설정
- CSRF 보호

## 모니터링
- 로그 파일: `app.log`
- Kafka 이벤트 모니터링
- 에러 추적

## 문제 해결

### 알림이 수신되지 않는 경우
1. Kafka 서버 실행 확인
2. WebSocket 연결 상태 확인
3. 브라우저 콘솔 로그 확인

### 데이터베이스 연결 오류
1. MySQL 서버 실행 확인
2. 데이터베이스 접속 정보 확인
3. 테이블 존재 여부 확인 