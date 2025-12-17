# SERVER / path-planning-server

Path: `SERVER/path-planning-server`

## ⚠️ 개발 상태: 부분 구현

**현재 상태**: 데모 코드만 존재합니다. 실제 경로계획 서버는 아직 구현되지 않았습니다.

## Purpose
- A*, D* Lite 등 알고리즘을 사용한 경로계획 서버 (계획됨)

## Tech
- Python, C++ (옵션), ROS2 연동

## 현재 구현 내용

### extract_corner/
- `corner_demo.py`: 코너 추출 데모 코드
- `straight_path.py`: 직선 경로 알고리즘 데모
- `visualization.py`: 경로 시각화 데모

**참고**: 이 파일들은 데모/프로토타입 코드이며, 실제 서버 구현은 아직 진행되지 않았습니다.

## 향후 개발 계획

1. 경로계획 알고리즘 구현 (A*, D* Lite)
2. HTTP/gRPC API 서버 구현
3. ROS2 연동
4. 맵 포맷 문서화

## Maintainer
- TBD