# YOLO 객체 인식 모델 추가 개발 계획

**작성일**: 2025-11-10  
**목적**: 장애물 회피 및 사물 인식을 위한 YOLO 객체 인식 모델 추가

## 개요

YOLO (You Only Look Once) 객체 인식 모델을 기존 로봇 인식 시스템에 추가합니다.  
기존 4개 카테고리(ArUco, OCR, Face, Person)와 동일한 인터페이스로 통합됩니다.

### 주요 목적

1. **장애물 회피**: 실시간 장애물 감지 및 회피 명령 생성
2. **사물 인식**: 환경 내 사물 식별 및 상호작용

---

## 개발 작업 목록

### 1. 데이터베이스 스키마 업데이트

#### 1.1 ENUM 타입 업데이트
- `detection_category` ENUM에 `'object'` 추가
- 기존: `('aruco', 'text', 'face', 'person')`
- 변경: `('aruco', 'text', 'face', 'person', 'object')`

#### 1.2 object_registry 테이블 생성
```sql
CREATE TABLE object_registry (
    object_key TEXT PRIMARY KEY,
    object_class TEXT NOT NULL,  -- 'person', 'chair', 'door', 'obstacle' 등
    object_type TEXT,  -- 'static', 'dynamic', 'obstacle', 'interactive'
    pose JSONB,  -- 위치/자세 정보
    size JSONB,  -- 크기 정보 {width, height, depth}
    properties JSONB,  -- 추가 속성 (색상, 재질 등)
    action_plan JSONB,  -- 기본 처리 계획
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 1.3 마이그레이션 파일
- 파일: `app/infrastructure/db/migrations/versions/20251110_add_object_detection.py`
- 작업:
  - ENUM 타입 업데이트 (ALTER TYPE)
  - object_registry 테이블 생성
  - 인덱스 생성 (object_class, object_type)

---

### 2. 도메인 레이어 업데이트

#### 2.1 엔티티 검증 업데이트
**파일**: `app/domain/entities/robot_detection_event.py`

```python
# 변경 전
if not self.category or self.category not in ["aruco", "text", "face", "person"]:
    return False

# 변경 후
if not self.category or self.category not in ["aruco", "text", "face", "person", "object"]:
    return False

# _validate_meta 메서드에 object 검증 추가
def _validate_meta(self) -> bool:
    # ... 기존 검증 ...
    elif self.category == "object":
        # YOLO: object_class, bbox, confidence, pose 등
        return True
    return True
```

#### 2.2 DetectionCategory 타입 업데이트
**파일**: `app/domain/entities/robot_detection_event.py`

```python
# 변경 전
DetectionCategory = Literal["aruco", "text", "face", "person"]

# 변경 후
DetectionCategory = Literal["aruco", "text", "face", "person", "object"]
```

---

### 3. 인프라 레이어 업데이트

#### 3.1 SQLAlchemy 모델 추가
**파일**: `app/infrastructure/db/models/robot_detection_models.py`

```python
class ObjectRegistryModel(Base):
    """YOLO 객체 레지스트리 모델"""
    __tablename__ = "object_registry"
    __table_args__ = (
        {'comment': 'YOLO 객체 레지스트리 (장애물/사물 인식)'}
    )

    object_key: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        nullable=False,
        comment="객체 키 (예: OBJ_chair_001, OBJ_door_002)"
    )
    object_class: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="객체 클래스 (person, chair, door, obstacle 등)"
    )
    object_type: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="객체 타입 (static, dynamic, obstacle, interactive)"
    )
    pose: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="위치/자세 정보"
    )
    size: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="크기 정보 {width, height, depth}"
    )
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="추가 속성 (색상, 재질 등)"
    )
    action_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="기본 처리 계획"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="수정 시간"
    )
```

#### 3.2 모델 __init__.py 업데이트
**파일**: `app/infrastructure/db/models/__init__.py`

```python
from .robot_detection_models import (
    RobotDetectionEventModel,
    MarkerRegistryModel,
    TextRegistryModel,
    FaceRegistryModel,
    PersonRegistryModel,
    ObjectRegistryModel,  # 추가
)

__all__ = [
    # ... 기존 ...
    "ObjectRegistryModel",  # 추가
]
```

---

### 4. 도메인 포트 업데이트

#### 4.1 ObjectRegistryRepository 인터페이스 추가
**파일**: `app/domain/ports/robot_detection_repository.py`

```python
class ObjectRegistryRepository(ABC):
    """YOLO 객체 레지스트리 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_by_key(self, object_key: str) -> Optional[Dict[str, Any]]:
        """객체 레지스트리 조회"""
        pass
    
    @abstractmethod
    async def save(self, object_key: str, data: Dict[str, Any]) -> None:
        """객체 레지스트리 저장"""
        pass
    
    @abstractmethod
    async def update(self, object_key: str, data: Dict[str, Any]) -> None:
        """객체 레지스트리 업데이트"""
        pass
```

---

### 5. 리포지토리 구현 추가

#### 5.1 ObjectRegistryRepositoryImpl 구현
**파일**: `app/adapters/repositories/robot_detection_repository_impl.py`

```python
class ObjectRegistryRepositoryImpl(ObjectRegistryRepository):
    """YOLO 객체 레지스트리 리포지토리 구현"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_key(self, object_key: str) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(ObjectRegistryModel).where(
                ObjectRegistryModel.object_key == object_key
            )
        )
        model = result.scalar_one_or_none()
        if model:
            return self._to_dict(model)
        return None
    
    async def save(self, object_key: str, data: Dict[str, Any]) -> None:
        model = ObjectRegistryModel(
            object_key=object_key,
            object_class=data.get("object_class", ""),
            object_type=data.get("object_type"),
            pose=data.get("pose"),
            size=data.get("size"),
            properties=data.get("properties"),
            action_plan=data.get("action_plan"),
        )
        self.session.add(model)
        await self.session.commit()
    
    async def update(self, object_key: str, data: Dict[str, Any]) -> None:
        result = await self.session.execute(
            select(ObjectRegistryModel).where(
                ObjectRegistryModel.object_key == object_key
            )
        )
        model = result.scalar_one_or_none()
        if model:
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            model.updated_at = datetime.utcnow()
            await self.session.commit()
    
    def _to_dict(self, model: ObjectRegistryModel) -> Dict[str, Any]:
        return {
            "object_key": model.object_key,
            "object_class": model.object_class,
            "object_type": model.object_type,
            "pose": model.pose,
            "size": model.size,
            "properties": model.properties,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }
```

---

### 6. 애플리케이션 레이어 업데이트

#### 6.1 유즈케이스 업데이트
**파일**: `app/application/use_cases/robot_detection_use_cases.py`

```python
class CreateRobotDetectionUseCase:
    def __init__(
        self,
        repository: RobotDetectionRepository,
        marker_registry: Optional[MarkerRegistryRepository] = None,
        text_registry: Optional[TextRegistryRepository] = None,
        face_registry: Optional[FaceRegistryRepository] = None,
        person_registry: Optional[PersonRegistryRepository] = None,
        object_registry: Optional[ObjectRegistryRepository] = None,  # 추가
    ):
        # ... 기존 ...
        self.object_registry = object_registry
    
    async def _update_registry(self, entity: RobotDetectionEvent):
        # ... 기존 카테고리 처리 ...
        elif entity.category == "object" and self.object_registry:
            # YOLO 객체 레지스트리 업데이트
            await self.object_registry.upsert(
                entity.unique_key,
                {
                    "object_class": entity.meta.get("object_class"),
                    "object_type": entity.meta.get("object_type"),
                    "pose": entity.meta.get("pose"),
                    "size": entity.meta.get("size"),
                    "properties": entity.meta.get("properties"),
                    "action_plan": entity.processing_info.to_dict(),
                },
            )
```

#### 6.2 GetRegistryUseCase 업데이트
**파일**: `app/application/use_cases/robot_detection_use_cases.py`

```python
class GetRegistryUseCase:
    def __init__(
        self,
        marker_registry: Optional[MarkerRegistryRepository] = None,
        text_registry: Optional[TextRegistryRepository] = None,
        face_registry: Optional[FaceRegistryRepository] = None,
        person_registry: Optional[PersonRegistryRepository] = None,
        object_registry: Optional[ObjectRegistryRepository] = None,  # 추가
    ):
        # ... 기존 ...
        self.object_registry = object_registry
    
    async def execute(self, category: str, unique_key: str) -> Optional[Dict[str, Any]]:
        # ... 기존 카테고리 처리 ...
        elif category == "object" and self.object_registry:
            return await self.object_registry.get_by_key(unique_key)
        return None
```

---

### 7. HTTP 레이어 업데이트

#### 7.1 라우터 업데이트
**파일**: `app/adapters/http/robot_detection_router.py`

```python
def get_object_registry(session: AsyncSession = Depends(get_app_session)) -> ObjectRegistryRepositoryImpl:
    return ObjectRegistryRepositoryImpl(session)

@router.post("/", response_model=RobotDetectionResponse, status_code=status.HTTP_201_CREATED)
async def create_detection(
    request: RobotDetectionCreateRequest,
    x_robot_id: str = Header(..., alias="X-Robot-ID"),
    repository: RobotDetectionRepositoryImpl = Depends(get_repository),
    marker_registry: MarkerRegistryRepositoryImpl = Depends(get_marker_registry),
    text_registry: TextRegistryRepositoryImpl = Depends(get_text_registry),
    face_registry: FaceRegistryRepositoryImpl = Depends(get_face_registry),
    person_registry: PersonRegistryRepositoryImpl = Depends(get_person_registry),
    object_registry: ObjectRegistryRepositoryImpl = Depends(get_object_registry),  # 추가
):
    use_case = CreateRobotDetectionUseCase(
        repository=repository,
        marker_registry=marker_registry,
        text_registry=text_registry,
        face_registry=face_registry,
        person_registry=person_registry,
        object_registry=object_registry,  # 추가
    )
    # ... 나머지 코드 ...

@router.get("/registry/{category}/{unique_key}", response_model=RegistryResponse)
async def get_registry(
    category: str,
    unique_key: str,
    marker_registry: MarkerRegistryRepositoryImpl = Depends(get_marker_registry),
    text_registry: TextRegistryRepositoryImpl = Depends(get_text_registry),
    face_registry: FaceRegistryRepositoryImpl = Depends(get_face_registry),
    person_registry: PersonRegistryRepositoryImpl = Depends(get_person_registry),
    object_registry: ObjectRegistryRepositoryImpl = Depends(get_object_registry),  # 추가
):
    use_case = GetRegistryUseCase(
        marker_registry=marker_registry,
        text_registry=text_registry,
        face_registry=face_registry,
        person_registry=person_registry,
        object_registry=object_registry,  # 추가
    )
    # ... 나머지 코드 ...
```

---

### 8. 문서 업데이트

#### 8.1 Interface Specification 업데이트
**파일**: `docs/interfaces/INTERFACE_SPECIFICATION.md`

- IF-RC-05 추가: YOLO 객체 인식 이벤트 수집
- IF-RC-07 업데이트: category에 'object' 추가

#### 8.2 API 문서 업데이트
**파일**: `docs/apis/robot_detections_api.md`

- YOLO 객체 인식 샘플 페이로드 추가
- 사용 예제 추가

---

## 마이그레이션 스크립트

### 파일: `app/infrastructure/db/migrations/versions/20251110_add_object_detection.py`

```python
"""add_object_detection

Revision ID: add_object_detection_001
Revises: 20251110_robot_detection
Create Date: 2025-11-10 15:00:00.000000+09:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'add_object_detection_001'
down_revision: Union[str, Sequence[str], None] = '20251110_robot_detection'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ENUM 타입에 'object' 추가
    op.execute("""
        ALTER TYPE detection_category ADD VALUE IF NOT EXISTS 'object';
    """)
    
    # object_registry 테이블 생성
    op.create_table('object_registry',
        sa.Column('object_key', sa.Text(), primary_key=True, nullable=False, comment='객체 키'),
        sa.Column('object_class', sa.Text(), nullable=False, comment='객체 클래스'),
        sa.Column('object_type', sa.Text(), nullable=True, comment='객체 타입'),
        sa.Column('pose', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='위치/자세 정보'),
        sa.Column('size', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='크기 정보'),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='추가 속성'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='기본 처리 계획'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        comment='YOLO 객체 레지스트리 (장애물/사물 인식)'
    )
    
    # 인덱스 생성
    op.create_index('idx_object_registry_class', 'object_registry', ['object_class'], unique=False)
    op.create_index('idx_object_registry_type', 'object_registry', ['object_type'], unique=False)

def downgrade() -> None:
    # 테이블 삭제
    op.drop_table('object_registry')
    
    # ENUM 타입에서 'object' 제거는 불가능 (PostgreSQL 제약)
    # 필요시 전체 ENUM 재생성 필요
    pass
```

---

## 개발 피드백 요청 사항

### 1. 데이터 모델 설계

**질문**: `object_registry` 테이블 구조가 적절한가요?

**제안된 구조**:
- `object_key`: 객체 고유 키 (예: `OBJ_chair_001`, `OBJ_door_002`)
- `object_class`: YOLO 클래스 (person, chair, door, obstacle 등)
- `object_type`: 객체 타입 (static, dynamic, obstacle, interactive)
- `pose`: 위치/자세 정보
- `size`: 크기 정보
- `properties`: 추가 속성

**검토 필요**:
- `object_key` 형식이 적절한가요? (예: `OBJ_{class}_{id}`)
- `object_type` 분류가 충분한가요?
- 추가로 필요한 필드가 있나요?

### 2. Intent 타입 확장

**질문**: YOLO 객체 인식을 위한 새로운 intent가 필요한가요?

**현재 intent**: `open_door`, `start_follow`, `stop_follow`, `announce`, `none`

**제안**:
- `avoid_obstacle`: 장애물 회피
- `approach_object`: 사물 접근
- `interact_object`: 사물 상호작용

**검토 필요**:
- 새로운 intent 타입을 추가할까요?
- 기존 intent로 충분한가요?

### 3. Meta 필드 구조

**질문**: YOLO 객체 인식의 `meta` 필드 구조가 적절한가요?

**제안된 구조**:
```json
{
  "object_class": "chair",
  "object_type": "static",
  "bbox": [120, 80, 64, 64],
  "confidence": 0.95,
  "pose": {
    "x": 2.5,
    "y": -0.5,
    "z": 0.0,
    "yaw": 0.0
  },
  "size": {
    "width": 0.5,
    "height": 1.0,
    "depth": 0.5
  },
  "properties": {
    "color": "brown",
    "material": "wood"
  }
}
```

**검토 필요**:
- 필수 필드와 선택 필드 구분이 적절한가요?
- 추가로 필요한 필드가 있나요?

### 4. 처리 흐름

**질문**: 장애물 회피와 사물 인식의 처리 흐름이 적절한가요?

**제안된 흐름**:
1. YOLO 모델이 객체 감지
2. `category: "object"`로 이벤트 전송
3. 레지스트리 조회/업데이트
4. `intent`에 따라 액션 실행:
   - `avoid_obstacle`: 회피 명령 생성
   - `approach_object`: 접근 명령 생성
   - `interact_object`: 상호작용 명령 생성

**검토 필요**:
- 처리 흐름이 적절한가요?
- 추가 로직이 필요한가요?

---

## 다음 단계

1. **피드백 수집**: 위의 질문들에 대한 피드백 수집
2. **코드 구현**: 피드백 반영 후 코드 구현
3. **테스트**: 단위 테스트 및 통합 테스트 작성
4. **문서 업데이트**: 인터페이스 및 API 문서 업데이트
5. **마이그레이션 실행**: 데이터베이스 마이그레이션 실행

---

## 참고 사항

- 기존 4개 카테고리와 동일한 인터페이스 사용
- 레지스트리 패턴 유지
- 비동기 액션 실행 지원
- Redis Streams 기반 처리 지원

