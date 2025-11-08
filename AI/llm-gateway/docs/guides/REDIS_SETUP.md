# Redis 메모리 Overcommit 설정 가이드

## 문제

Redis 컨테이너가 시작될 때 다음 경고가 나타납니다:
```
WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition.
```

## 해결 방법

### 방법 1: 호스트에서 영구 설정 (권장)

호스트 시스템에서 다음 명령을 실행하여 영구적으로 설정합니다:

```bash
# 현재 세션에만 적용 (임시)
sudo sysctl vm.overcommit_memory=1

# 영구적으로 적용 (재부팅 후에도 유지)
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 방법 2: 현재 세션에만 적용 (임시)

```bash
sudo sysctl vm.overcommit_memory=1
```

**주의**: 이 설정은 재부팅 후 초기화됩니다.

## 확인

설정이 적용되었는지 확인:

```bash
sysctl vm.overcommit_memory
```

출력이 `vm.overcommit_memory = 1`이면 성공입니다.

## 영향

- `vm.overcommit_memory = 0`: 기본값 (경고 발생, 대부분의 경우 문제없음)
- `vm.overcommit_memory = 1`: 항상 overcommit 허용 (Redis 권장)
- `vm.overcommit_memory = 2`: 메모리 제한 엄격 적용

## 참고

- 이 설정은 호스트 시스템 전체에 영향을 미칩니다.
- Docker 컨테이너 내부에서는 설정할 수 없습니다 (커널 파라미터이므로).
- 경고가 나타나도 Redis는 정상적으로 동작합니다.
- 대용량 데이터 저장 시에만 실제로 문제가 될 수 있습니다.

