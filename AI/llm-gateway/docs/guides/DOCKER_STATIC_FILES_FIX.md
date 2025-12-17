# Docker 컨테이너에서 Static 파일 업데이트 문제 해결

## 문제 상황
`docker compose down -v && docker compose up -d --build` 명령어로 재시작해도 테스트 UI(`test_alfred_voice.html`)의 변경사항이 반영되지 않음.

## 원인 분석

### 문제 원인
1. **Dockerfile에서 COPY만 사용**: `COPY tests/ ./tests/`로 빌드 시점에만 파일을 복사
2. **볼륨 마운트 없음**: docker-compose.yml에 tests 디렉토리 볼륨 마운트가 없어서 호스트의 변경사항이 컨테이너에 반영되지 않음
3. **빌드 시점 고정**: 빌드 시점의 파일만 컨테이너에 포함되어, 이후 호스트에서 수정한 파일이 반영되지 않음

## 해결 방법

### 수정 사항
`docker-compose.yml`에 tests 디렉토리를 볼륨으로 마운트 추가:

```yaml
volumes:
  # 로그 저장 (선택사항)
  - ./logs:/app/logs
  # 테스트 파일 (정적 파일 서빙용) - 개발 중 변경사항 반영
  - ./tests:/app/tests
```

### 작동 원리
- **볼륨 마운트**: 호스트의 `./tests` 디렉토리를 컨테이너의 `/app/tests`에 마운트
- **실시간 반영**: 호스트에서 파일을 수정하면 컨테이너 내부에서도 즉시 반영됨
- **우선순위**: 볼륨 마운트가 Dockerfile의 COPY보다 우선 적용됨

## 적용 방법

### 1. 컨테이너 재시작
```bash
cd AI/llm-gateway
docker compose down -v
docker compose up -d --build
```

### 2. 변경사항 확인
1. 브라우저에서 `http://localhost:8000/tests/test_alfred_voice.html` 접속
2. 파일을 수정하고 새로고침 (Ctrl+Shift+R 또는 Cmd+Shift+R)
3. 변경사항이 즉시 반영되는지 확인

### 3. 컨테이너 내부 확인 (선택사항)
```bash
# 컨테이너 내부에서 파일 확인
docker exec -it llm-gateway ls -la /app/tests/user_testing/

# 파일 내용 확인
docker exec -it llm-gateway cat /app/tests/user_testing/test_alfred_voice.html | head -20
```

## 추가 개선 사항

### 개발 환경 최적화
개발 중에는 소스 코드도 볼륨 마운트하는 것을 고려:

```yaml
volumes:
  - ./logs:/app/logs
  - ./tests:/app/tests
  # 개발 중 소스 코드도 볼륨 마운트 (선택사항)
  - ./src:/app/src
```

**주의**: 소스 코드를 볼륨 마운트하면 uvicorn의 `--reload` 옵션이 필요합니다.

### 프로덕션 환경
프로덕션에서는 볼륨 마운트 대신 COPY를 사용하는 것이 안전합니다:
- 이미지에 파일이 포함되어 일관성 보장
- 호스트 파일 시스템 의존성 제거

## 검증 체크리스트

- [ ] docker-compose.yml에 `./tests:/app/tests` 볼륨 마운트 추가됨
- [ ] 컨테이너 재시작 후 테스트 UI 접속 가능
- [ ] 호스트에서 파일 수정 시 컨테이너에 즉시 반영됨
- [ ] 브라우저 새로고침 시 변경사항 확인 가능

## 문제 해결

### 여전히 변경사항이 반영되지 않는 경우

1. **브라우저 캐시 확인**
   - 강력 새로고침: Ctrl+Shift+R (Windows/Linux) 또는 Cmd+Shift+R (Mac)
   - 개발자 도구에서 "Disable cache" 체크

2. **컨테이너 상태 확인**
   ```bash
   docker compose ps
   docker compose logs llm-gateway | tail -20
   ```

3. **볼륨 마운트 확인**
   ```bash
   docker inspect llm-gateway | grep -A 10 Mounts
   ```

4. **파일 권한 확인**
   ```bash
   ls -la tests/user_testing/test_alfred_voice.html
   ```

5. **컨테이너 내부 파일 확인**
   ```bash
   docker exec -it llm-gateway cat /app/tests/user_testing/test_alfred_voice.html | grep -i "유사도"
   ```

## 참고 사항

- 볼륨 마운트는 개발 환경에서 유용하지만, 프로덕션에서는 주의가 필요합니다
- 볼륨 마운트 시 호스트 파일 시스템의 권한 문제가 발생할 수 있습니다
- Windows에서 볼륨 마운트 시 경로 문제가 발생할 수 있으므로 WSL2 사용 권장

