# 커밋 메시지

## 실행 명령어

```bash
# 변경사항 확인
git status

# 문서 파일들 추가
git add SERVER/app-server/docs/

# 커밋
git commit -m "docs: 로봇 인식 인터페이스 문서 코드 기반 업데이트

- API 문서에 액션 실행기 동작 방식 상세 설명 추가
- 모든 카테고리 인터페이스 명세서 업데이트 (ArUco, OCR, 얼굴, 전신)
- 실제 코드 구현 반영한 처리 흐름 및 주의사항 업데이트
- 처음 보는 사람을 위한 사용 가이드 신규 작성
- 코드 위치 및 테스트 방법 안내 추가
- Redis 선택사항 명시 및 동작 방식 설명 추가

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

## 커밋 메시지 (간단 버전)

```bash
git commit -m "docs: 로봇 인식 인터페이스 문서 코드 기반 업데이트

- API 문서에 액션 실행기 동작 방식 상세 설명 추가
- 모든 카테고리 인터페이스 명세서 업데이트
- 사용 가이드 신규 작성
- 코드 위치 및 테스트 방법 안내 추가"
```

