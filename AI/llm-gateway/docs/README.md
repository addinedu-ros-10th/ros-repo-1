# 문서 인덱스

이 디렉토리는 LLM Gateway 프로젝트의 모든 문서를 포함합니다.

## 📁 디렉토리 구조

```
docs/
├── api/              # API 관련 문서
├── commits/          # 커밋 메시지 및 변경 이력
├── database/         # 데이터베이스 관련 문서 및 SQL 스크립트
├── guides/           # 사용자 가이드 및 테스트 가이드
└── reports/          # 개발 리포트 및 상태 보고서
```

## 📚 문서 카테고리

### API 문서 (`api/`)
- API 엔드포인트 업데이트 내역
- Voiceprint 기능 설명
- ALFRED 음성 인터페이스 업데이트

### 커밋 메시지 (`commits/`)
- 주요 기능 개발 커밋 메시지
- 변경 이력 기록

### 데이터베이스 문서 (`database/`)
- 데이터베이스 스키마 설계
- 테이블 생성 및 초기화 스크립트
- 권한 부여 스크립트
- 데이터베이스 쿼리 예시

### 가이드 문서 (`guides/`)
- 프로젝트 개요
- Redis 설정 가이드
- WebSocket 테스트 가이드
- Voiceprint 테스트 가이드
- Docker 설정 가이드

### 리포트 (`reports/`)
- 개발 현황 리포트
- 디버깅 리포트
- 기능별 개발 완료 리포트
- 데이터베이스 사용 현황 리포트

## 🔍 빠른 찾기

### 프로젝트 시작하기
- [프로젝트 개요](guides/PROJECT_OVERVIEW.md)
- [README.md](../README.md) (프로젝트 루트)

### 개발 현황 확인
- [최신 개발 현황 리포트](reports/CURRENT_DEVELOPMENT_REPORT.md)
- [종합 개발 현황 리포트](reports/DEVELOPMENT_STATUS.md)

### API 사용하기
- [API 문서](../README.md#api-엔드포인트) (프로젝트 루트 README)
- [Swagger UI](http://localhost:8000/docs) (서버 실행 시)

### 데이터베이스 설정
- [데이터베이스 스키마](database/database_schema.md)
- [Redis 설정 가이드](guides/REDIS_SETUP.md)

### 테스트 가이드
- [WebSocket 테스트 가이드](guides/WEBSOCKET_TEST_GUIDE.md)
- [Voiceprint 테스트 가이드](guides/KEYWORD_VOICEPRINT_VERIFICATION_GUIDE.md)

## 📝 문서 작성 규칙

1. **마크다운 형식** 사용
2. **한국어**로 작성 (기술 용어는 영어 병기)
3. **날짜 및 버전 정보** 명시
4. **관련 문서 링크** 포함

## 🔄 문서 업데이트

문서는 기능 개발과 함께 업데이트됩니다. 주요 변경사항은 `reports/` 디렉토리에 리포트로 기록됩니다.

