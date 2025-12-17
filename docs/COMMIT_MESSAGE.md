# Git 커밋 메시지

## 커밋 메시지 (권장)

```
docs: 프로젝트 문서 정리 및 미구현 모듈 폴더 삭제

- 루트 README.md 업데이트: 미구현 모듈 제거 및 구현 상태 표시 추가
- path-planning-server README.md 업데이트: 부분 구현 상태 명시
- 미구현 모듈 폴더 6개 삭제 (local-hub, vllm-server, sim-resource-server, mcp-server, web-app, web-page)
- 프로젝트 분석 및 정리 작업 리포트 추가

변경 사항:
- README.md: 실제 구현된 모듈만 표시, 구현 상태 표시 추가
- SERVER/path-planning-server/README.md: 부분 구현 상태 명시
- 삭제: AI/mcp-server/, APP/web-app/, APP/web-page/, SERVER/local-hub/, SERVER/vllm-server/, SERVER/sim-resource-server/
- 추가: PROJECT_ANALYSIS_REPORT.md, PROJECT_CLEANUP_REPORT.md

통계: 8 files changed, 82 insertions(+), 156 deletions(-)
```

---

## 커밋 메시지 (간단 버전)

```
docs: 프로젝트 문서 정리 및 미구현 모듈 삭제

- README.md 업데이트: 미구현 모듈 제거, 구현 상태 표시 추가
- path-planning-server README.md: 부분 구현 상태 명시
- 미구현 모듈 폴더 6개 삭제
- 프로젝트 분석 리포트 추가
```

---

## 커밋 명령어

### 전체 변경사항 커밋
```bash
# 변경사항 스테이징
git add README.md
git add SERVER/path-planning-server/README.md
git add PROJECT_ANALYSIS_REPORT.md
git add PROJECT_CLEANUP_REPORT.md
git add CURRENT_STATUS_REPORT.md
git add COMMIT_MESSAGE.md

# 삭제된 파일 스테이징
git rm AI/mcp-server/README.md
git rm APP/web-app/README.md
git rm APP/web-page/README.md
git rm SERVER/local-hub/README.md
git rm SERVER/sim-resource-server/README.md
git rm SERVER/vllm-server/README.md

# 또는 한 번에
git add -A

# 커밋
git commit -m "docs: 프로젝트 문서 정리 및 미구현 모듈 폴더 삭제

- 루트 README.md 업데이트: 미구현 모듈 제거 및 구현 상태 표시 추가
- path-planning-server README.md 업데이트: 부분 구현 상태 명시
- 미구현 모듈 폴더 6개 삭제 (local-hub, vllm-server, sim-resource-server, mcp-server, web-app, web-page)
- 프로젝트 분석 및 정리 작업 리포트 추가

변경 사항:
- README.md: 실제 구현된 모듈만 표시, 구현 상태 표시 추가
- SERVER/path-planning-server/README.md: 부분 구현 상태 명시
- 삭제: AI/mcp-server/, APP/web-app/, APP/web-page/, SERVER/local-hub/, SERVER/vllm-server/, SERVER/sim-resource-server/
- 추가: PROJECT_ANALYSIS_REPORT.md, PROJECT_CLEANUP_REPORT.md

통계: 8 files changed, 82 insertions(+), 156 deletions(-)"
```

---

## 커밋 메시지 가이드

### 커밋 타입
- `docs`: 문서 변경
- `refactor`: 코드 리팩토링
- `chore`: 기타 작업

### 커밋 메시지 구조
1. **제목**: 간단한 설명 (50자 이내)
2. **본문**: 상세 설명 (선택사항)
3. **변경 사항**: 구체적인 변경 내용
4. **통계**: 변경된 파일 수 및 라인 수

---

## 참고사항

- 모든 변경사항은 문서 관련 작업입니다
- 삭제된 파일은 미구현 모듈의 README.md 파일입니다
- 실제 코드는 변경되지 않았습니다
- 프로젝트 구조 정리 및 문서화 개선 작업입니다

