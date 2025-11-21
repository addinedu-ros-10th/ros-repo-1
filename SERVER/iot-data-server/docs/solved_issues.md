# 해결된 주요 문제들

## 📋 **개요**
이 문서는 IoT Care Backend Service 개발 과정에서 발생한 주요 문제들과 그 해결 방법을 기록합니다.

## 🔧 **해결된 문제 목록**

### **1. 데이터베이스 연결 문제**
**문제 설명**: Docker 환경에서 `host.docker.internal:15432`로 데이터베이스 연결 시 `[Errno 111] Connection refused` 오류 발생

**원인**: Docker 컨테이너 내부에서 `host.docker.internal` 호스트명이 제대로 해석되지 않음

**해결 방법**: 
- 호스트 머신의 실제 IP 주소 사용 (`192.168.2.81:15432`)
- `env.dev`, `env.local`, `alembic.ini` 파일 수정

**수정된 파일들**:
```bash
# services/was-server/env.dev
DATABASE_URL=postgresql://svc_dev:IOT_dev_123!@#@192.168.2.81:15432/iot_care

# services/was-server/env.local
DB_HOST=192.168.2.81

# services/was-server/alembic.ini
sqlalchemy.url = postgresql://svc_dev:IOT_dev_123!@#@192.168.2.81:15432/iot_care
```

**결과**: 데이터베이스 연결 성공, 애플리케이션 정상 시작

---

### **2. 데이터베이스 스키마 불일치 문제**
**문제 설명**: ORM 모델과 실제 데이터베이스 테이블 구조가 일치하지 않아 `UndefinedColumnError` 발생

**원인**: 
- Alembic 마이그레이션 설정 문제 (`target_metadata = None`)
- 일부 테이블의 컬럼 누락

**해결 방법**: 
- 수동 스키마 동기화 스크립트 생성 및 실행
- `fix_database.py`, `fix_edge_tables.py`, `fix_raw_sensor_tables.py`

**주요 수정 사항**:
```sql
-- Edge 센서 테이블 컬럼 추가
ALTER TABLE sensor_edge_reed ADD COLUMN IF NOT EXISTS confidence NUMERIC;
ALTER TABLE sensor_edge_reed ADD COLUMN IF NOT EXISTS magnetic_strength NUMERIC;
ALTER TABLE sensor_edge_reed ADD COLUMN IF NOT EXISTS processing_time NUMERIC;

-- Raw 센서 테이블 컬럼 추가
ALTER TABLE sensor_raw_dht ADD COLUMN IF NOT EXISTS temperature NUMERIC;
ALTER TABLE sensor_raw_dht ADD COLUMN IF NOT EXISTS humidity NUMERIC;
ALTER TABLE sensor_raw_dht ADD COLUMN IF NOT EXISTS heat_index NUMERIC;
```

**결과**: 모든 테이블의 컬럼이 ORM 모델과 일치

---

### **3. 의존성 주입 (DI) 문제**
**문제 설명**: API 엔드포인트에서 `db_session` 주입 실패로 `object NoneType can't be used in 'await' expression` 오류 발생

**원인**: 
- 일부 API에서 `get_db` 대신 `get_db_session` 사용 필요
- 의존성 주입 함수명 불일치

**해결 방법**: 
- 모든 Raw 센서 API에서 `get_db` → `get_db_session` 변경
- `cds.py`, `dht.py`, `flame.py`, `imu.py` 등 수정

**수정된 코드**:
```python
# Before
from app.infrastructure.database import get_db
db: AsyncSession = Depends(get_db)

# After
from app.infrastructure.database import get_db_session
db: AsyncSession = Depends(get_db_session)
```

**결과**: 모든 API에서 데이터베이스 세션 정상 주입

---

### **4. User API 이메일 중복 문제**
**문제 설명**: 사용자 생성 시 데이터베이스 레벨에서만 중복 검증으로 인한 `UniqueViolationError` 발생

**원인**: 
- UserService에서 이메일 중복 검증 로직 누락
- 데이터베이스 제약 조건 위반 후 오류 처리

**해결 방법**: 
- UserService.create_user() 메서드에 이메일 중복 검증 로직 추가
- 비즈니스 로직 레벨에서 사전 검증

**추가된 코드**:
```python
async def create_user(self, name: str, role: str = "user", email: str = None, phone: str = None) -> User:
    # 비즈니스 로직 검증
    if not self.validate_user_data(name, email, phone):
        raise ValueError("사용자 데이터가 유효하지 않습니다")
    
    # 이메일 중복 검증
    if email:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"이메일 '{email}'이 이미 사용 중입니다")
    
    # ... 나머지 로직
```

**결과**: 명확한 오류 메시지와 함께 중복 이메일 사용 방지

---

### **5. API 경로 문제 (307 Temporary Redirect)**
**문제 설명**: Python 테스트 코드에서 `/api/v1`로 요청 시 HTTP 307 Temporary Redirect 오류 발생

**원인**: 
- User API가 `/api/v1/users/`에 등록되어 있어 `/api/v1`로는 접근 불가
- FastAPI에서 경로 불일치 시 자동 리다이렉트

**해결 방법**: 
- User API에 `/api/v1` 경로 직접 추가
- `@router.post("")` 데코레이터 추가

**수정된 코드**:
```python
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(...):
    # ... 구현 내용
```

**결과**: `/api/v1` 경로에서 User API 정상 접근 가능

---

### **6. UserService 추상 메서드 구현 문제**
**문제 설명**: `Can't instantiate abstract class UserService with abstract methods can_manage_user, validate_user_permissions` 오류 발생

**원인**: 
- UserService가 IUserService 인터페이스의 모든 추상 메서드를 구현하지 않음
- `validate_user_permissions`, `can_manage_user` 메서드 누락

**해결 방법**: 
- 누락된 추상 메서드들 구현
- 인터페이스와 구현체의 메서드 시그니처 일치

**구현된 메서드들**:
```python
async def validate_user_permissions(self, user: User, required_role: str) -> bool:
    """사용자 권한을 검증합니다."""
    role_hierarchy = {"admin": 4, "caregiver": 3, "family": 2, "user": 1}
    user_level = role_hierarchy.get(user.user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    return user_level >= required_level

async def can_manage_user(self, admin_user: User, target_user: User) -> bool:
    """사용자 관리 권한을 확인합니다."""
    # 역할별 관리 권한 로직 구현
    # ... 구현 내용
```

**결과**: UserService 클래스 정상 인스턴스화 및 사용 가능

---

## 📊 **문제 해결 통계**
- **총 해결된 문제**: 6개
- **데이터베이스 관련**: 2개
- **API 관련**: 2개
- **아키텍처 관련**: 2개
- **해결률**: 100% (현재까지 발생한 문제들)

## 🎯 **문제 해결 원칙**
1. **근본 원인 분석**: 증상이 아닌 원인을 찾아 해결
2. **체계적 접근**: 한 번에 하나의 문제를 해결하고 검증
3. **문서화**: 해결 과정과 방법을 상세히 기록
4. **재발 방지**: 유사한 문제가 발생하지 않도록 구조적 개선

---
*마지막 업데이트: 2025-08-21*
*문서 작성자: AI Assistant* 