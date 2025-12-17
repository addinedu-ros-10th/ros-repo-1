# GitHub 브랜치 정리 작업 계획

**작성일**: 2025-11-18  
**작업자**: Development Team

---

## 요청사항 이해 확인

### ✅ 이해한 요청사항

1. **staging 브랜치 → release 브랜치로 변경**
   - 로컬 및 원격의 `staging` 브랜치를 `release`로 이름 변경
   - 기존 `staging` 브랜치는 삭제

2. **feat/* 브랜치 유지**
   - 개발 중인 모든 `feat/*` 브랜치는 그대로 유지
   - 로컬: 3개, 원격: 9개

3. **메인 브랜치 구조**
   - `main`: 프로덕션 브랜치
   - `release`: 릴리스 브랜치 (기존 staging)
   - `dev`: 개발 브랜치

4. **base/* 브랜치를 dev에 머지**
   - 모든 `base/*` 브랜치 (16개)를 `dev` 브랜치에 머지
   - 머지 후 `base/*` 브랜치는 유지 (히스토리 보존)

---

## 현재 브랜치 상태

### 메인 브랜치
- ✅ `main` (로컬 및 원격)
- ✅ `dev` (로컬 및 원격)
- ⚠️ `staging` (로컬 및 원격) → `release`로 변경 필요

### 베이스 브랜치 (base/*) - 16개
로컬 및 원격 모두 존재:
1. `base/AI/llm-gateway`
2. `base/AI/mcp-server`
3. `base/APP/web-app`
4. `base/APP/web-page`
5. `base/DEEP_LEARNING/deep-learning-server`
6. `base/IOT/arduino`
7. `base/ROS2/pinky_pro`
8. `base/ROS2/rfred`
9. `base/ROS2/util`
10. `base/SERVER/app-server`
11. `base/SERVER/iot-data-server`
12. `base/SERVER/local-hub`
13. `base/SERVER/path-planning-server`
14. `base/SERVER/ros2-server`
15. `base/SERVER/sim-resource-server`
16. `base/SERVER/vllm-server`

### 피처 브랜치 (feat/*) - 유지
로컬: 3개
- `feat/AI/llm-gateway__voice_interface__RP-22`
- `feat/SERVER/app-server__DL_model_interface__RP-57__app-server_init`
- `feat/SERVER/ros2-server__build_state_management__RP-58__make_robot_state_manageable` (현재 작업 중)

원격: 9개 (로컬에 없는 것 포함)

---

## 작업 계획

### Phase 1: 사전 준비 및 안전 확인

1. **현재 작업 상태 확인**
   - 현재 브랜치: `feat/SERVER/ros2-server__build_state_management__RP-58__make_robot_state_manageable`
   - 커밋되지 않은 변경사항 확인
   - 작업 중인 내용 백업 (필요시)

2. **브랜치 상태 확인**
   - 각 base/* 브랜치의 최신 커밋 확인
   - dev 브랜치의 현재 상태 확인
   - 충돌 가능성 사전 검토

### Phase 2: base/* 브랜치를 dev에 머지

**순서:**
1. `dev` 브랜치로 체크아웃
2. `dev` 브랜치를 최신 상태로 업데이트
3. 각 `base/*` 브랜치를 순차적으로 `dev`에 머지
   - 충돌 발생 시 해결
   - 머지 커밋 메시지 작성

**머지 순서 (카테고리별):**
```
1. base/AI/llm-gateway
2. base/AI/mcp-server
3. base/APP/web-app
4. base/APP/web-page
5. base/DEEP_LEARNING/deep-learning-server
6. base/IOT/arduino
7. base/ROS2/pinky_pro
8. base/ROS2/rfred
9. base/ROS2/util
10. base/SERVER/app-server
11. base/SERVER/iot-data-server
12. base/SERVER/local-hub
13. base/SERVER/path-planning-server
14. base/SERVER/ros2-server
15. base/SERVER/sim-resource-server
16. base/SERVER/vllm-server
```

### Phase 3: staging → release 브랜치 변경

1. **로컬 브랜치 변경**
   - `staging` 브랜치를 `release`로 이름 변경
   - 또는 `staging`의 내용을 `release`에 복사

2. **원격 브랜치 변경**
   - 원격 `staging` 브랜치를 `release`로 이름 변경
   - 원격 `staging` 브랜치 삭제

### Phase 4: 원격 저장소 동기화

1. **dev 브랜치 푸시**
   - 머지된 `dev` 브랜치를 원격에 푸시

2. **release 브랜치 푸시**
   - 변경된 `release` 브랜치를 원격에 푸시

3. **원격 브랜치 정리**
   - 원격 `staging` 브랜치 삭제 확인

---

## 예상 작업 시간

- Phase 1: 사전 준비 (5분)
- Phase 2: base/* 브랜치 머지 (30-60분, 충돌 해결 시간 포함)
- Phase 3: staging → release 변경 (5분)
- Phase 4: 원격 동기화 (5분)

**총 예상 시간**: 45-75분

---

## 주의사항

### ⚠️ 위험 요소

1. **머지 충돌 가능성**
   - 여러 base/* 브랜치가 같은 파일을 수정했을 경우 충돌 발생 가능
   - 충돌 해결 시 신중하게 처리 필요

2. **원격 브랜치 삭제**
   - `staging` 브랜치 삭제는 되돌릴 수 없음
   - 삭제 전 백업 권장

3. **feat/* 브랜치 영향**
   - feat/* 브랜치가 base/* 브랜치를 기반으로 하는 경우
   - base/* 브랜치 머지 후 rebase 필요할 수 있음

### ✅ 안전 조치

1. **작업 전 백업**
   - 현재 상태를 별도 브랜치로 백업
   - 원격 저장소는 이미 백업 역할

2. **단계별 확인**
   - 각 단계마다 상태 확인
   - 문제 발생 시 즉시 중단

3. **로컬에서 먼저 테스트**
   - 원격 푸시 전 로컬에서 모든 작업 완료
   - 검증 후 원격에 푸시

---

## 작업 후 예상 결과

### 브랜치 구조
```
main (프로덕션)
  ↑
release (릴리스) ← staging에서 변경
  ↑
dev (개발) ← 모든 base/* 브랜치 머지됨
  ↑
feat/* (개발 중인 피처 브랜치들)
```

### 브랜치 목록
- ✅ `main`
- ✅ `release` (기존 staging)
- ✅ `dev` (모든 base/* 머지됨)
- ✅ `feat/*` (개발 중인 피처 브랜치들)
- ✅ `base/*` (히스토리 보존용, 유지)

---

## 확인 질문

1. **base/* 브랜치 머지 방식**
   - 모든 base/* 브랜치를 하나의 큰 머지로 할까요?
   - 아니면 각각 개별 머지 커밋으로 할까요?
   - → **제안**: 개별 머지 커밋 (히스토리 추적 용이)

2. **base/* 브랜치 삭제 여부**
   - 머지 후 base/* 브랜치를 삭제할까요?
   - 아니면 히스토리 보존을 위해 유지할까요?
   - → **제안**: 유지 (히스토리 보존)

3. **충돌 해결 전략**
   - 충돌 발생 시 자동 해결 시도할까요?
   - 아니면 수동 확인 후 해결할까요?
   - → **제안**: 수동 확인 후 해결 (안전)

4. **staging 브랜치 처리**
   - staging을 release로 이름만 변경할까요?
   - 아니면 staging의 내용을 release에 복사할까요?
   - → **제안**: 이름 변경 (히스토리 보존)

---

## 작업 시작 전 확인사항

- [ ] 현재 작업 중인 변경사항 커밋/스태시 완료
- [ ] 원격 저장소와 동기화 완료
- [ ] 백업 브랜치 생성 (선택사항)
- [ ] 작업 계획 승인 확인

---

**작업 시작 전 피드백 요청**

위 계획이 요청사항을 정확히 반영했는지 확인 부탁드립니다.
특히 다음 사항에 대한 피드백을 요청합니다:

1. base/* 브랜치 머지 방식 선호도
2. base/* 브랜치 삭제 여부
3. 충돌 해결 전략
4. staging → release 변경 방식
5. 작업 시작 시점

피드백 주시면 즉시 작업을 시작하겠습니다.

