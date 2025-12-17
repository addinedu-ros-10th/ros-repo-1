# Git 커밋 명령어

## 1. 변경사항 확인

```bash
git status
```

## 2. 문서 파일들 추가

```bash
git add SERVER/app-server/docs/
```

## 3. 커밋 (프로젝트 템플릿 형식)

```bash
git commit -m "docs(robot-detection): UPDATE, 로봇 인식 인터페이스 문서 코드 기반 업데이트

- API 문서에 액션 실행기 동작 방식 상세 설명 추가
  * Redis Streams 기반 비동기 처리 설명
  * Redis 활성화/비활성화 시나리오 명시
  * 환경 변수 및 워커 프로세스 설명 추가

- 모든 카테고리 인터페이스 명세서 업데이트
  * ArUco 마커, OCR 텍스트, 얼굴 인식, 전신 인식
  * 실제 코드 구현 반영한 처리 흐름 상세화
  * X-Robot-ID 헤더 필수 사항 명시
  * 액션 실행 방식 설명 추가
  * 코드 위치 및 테스트 방법 안내 추가

- 처음 보는 사람을 위한 사용 가이드 신규 작성
  * 빠른 시작 가이드
  * API 사용 예시 (curl 명령어)
  * 테스트 가이드
  * 카테고리별 사용 예시
  * 문제 해결 가이드

- 문서 업데이트 현황 리포트 작성

업데이트된 문서:
- docs/apis/robot_detections_api.md
- docs/interfaces/aruco_marker.md
- docs/interfaces/ocr_text.md
- docs/interfaces/face_recognition.md
- docs/interfaces/person_tracking.md
- docs/interfaces/README.md

신규 작성 문서:
- docs/interfaces/USAGE_GUIDE.md
- docs/development/document_update_report.md"
```

## 4. 커밋 (간단 버전)

```bash
git commit -m "docs(robot-detection): UPDATE, 로봇 인식 인터페이스 문서 코드 기반 업데이트

- API 문서에 액션 실행기 동작 방식 상세 설명 추가
- 모든 카테고리 인터페이스 명세서 업데이트
- 사용 가이드 신규 작성
- 코드 위치 및 테스트 방법 안내 추가"
```

## 커밋 메시지 형식 설명

프로젝트의 Git 메시지 템플릿 형식:
- `docs`: 문서 변경
- `robot-detection`: 로봇 인식 관련
- `UPDATE`: 업데이트 작업
- 제목: 50자 이내, 명령형 어조



