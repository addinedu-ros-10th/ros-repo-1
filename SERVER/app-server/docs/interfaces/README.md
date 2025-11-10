# 로봇 인식 인터페이스 명세서

## 개요

이 디렉토리는 로봇 인식 시스템의 4개 카테고리별 인터페이스 명세서를 포함합니다.

## 카테고리 목록

1. **[ArUco 마커](./aruco_marker.md)** - ArUco 마커 인식을 통한 출입구 제어 및 위치 인식
2. **[OCR 문자인식](./ocr_text.md)** - OCR을 통한 공간 식별 및 안내
3. **[얼굴 인식](./face_recognition.md)** - 얼굴 인식을 통한 면회자/보호자 식별
4. **[전신 인식](./person_tracking.md)** - 전신 추적을 통한 로봇 추종 기능

## 공통 인터페이스

모든 카테고리는 다음 공통 인터페이스를 사용합니다:

- **인식 이벤트 수집**: `POST /api/v1/detections`
- **인식 이벤트 목록 조회**: `GET /api/v1/detections`
- **인식 이벤트 단건 조회**: `GET /api/v1/detections/{event_id}`
- **레지스트리 조회**: `GET /api/v1/detections/registry/{category}/{unique_key}`
- **액션 실행**: `POST /api/v1/detections/actions/execute`

## 시스템 아키텍처

```
Robot Controller <-> Central Server <-> AI Server
```

- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **Central Server**: FastAPI 기반 중앙 서버 (이 프로젝트)
- **AI Server**: 딥러닝 모델 기반 인식 서버

## 관련 문서

- [사용 가이드](./USAGE_GUIDE.md) - 처음 보는 사람을 위한 종합 가이드
- [DB 설계 문서](../database/robot_detection_schema.md)
- [개발 리포트](../development/commit_report_20251110.md)
- [API 문서](../apis/robot_detections_api.md)
- [문서 업데이트 리포트](../development/document_update_report.md)

