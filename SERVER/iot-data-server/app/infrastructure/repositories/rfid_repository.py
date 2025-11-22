"""
RFID 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 RFID 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.sensor_repository import IRFIDRepository
from app.infrastructure.models import SensorRawRFID
from app.api.v1.schemas import (
    SensorRawRFIDCreate,
    SensorRawRFIDUpdate,
    SensorRawRFIDResponse
)


class RFIDRepository(IRFIDRepository):
    """RFID 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawRFIDCreate) -> SensorRawRFIDResponse:
        """RFID 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }
        
        db_data = SensorRawRFID(**orm_data)
        print(db_data)
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return SensorRawRFIDResponse.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawRFIDResponse]:
        """특정 시간의 RFID 센서 데이터 조회"""
        query = select(SensorRawRFID).where(
            and_(
                SensorRawRFID.device_id == device_id,
                SensorRawRFID.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawRFIDResponse.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawRFIDResponse]:
        """최신 RFID 센서 데이터 조회"""
        query = (
            select(SensorRawRFID)
            .where(SensorRawRFID.device_id == device_id)
            .order_by(SensorRawRFID.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawRFIDResponse.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawRFIDResponse]:
        """RFID 센서 데이터 목록 조회"""
        query = select(SensorRawRFID)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(SensorRawRFID.device_id == device_id)
        if start_time:
            query = query.where(SensorRawRFID.time >= start_time)
        if end_time:
            query = query.where(SensorRawRFID.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(SensorRawRFID.time.desc()).limit(limit_count)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [SensorRawRFIDResponse.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawRFIDUpdate
    ) -> Optional[SensorRawRFIDResponse]:
        """RFID 센서 데이터 수정"""
        query = select(SensorRawRFID).where(
            and_(
                SensorRawRFID.device_id == device_id,
                SensorRawRFID.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        db_data = result.scalar_one_or_none()
        
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_data, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_data)
        return SensorRawRFIDResponse.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """RFID 센서 데이터 삭제"""
        query = select(SensorRawRFID).where(
            and_(
                SensorRawRFID.device_id == device_id,
                SensorRawRFID.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        db_data = result.scalar_one_or_none()
        
        if not db_data:
            return False
        
        await self.db.delete(db_data)
        await self.db.commit()
        return True
    
    async def get_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서 데이터 기본 통계 조회"""
        return await self.get_card_statistics(device_id, start_time, end_time)
    
    async def get_card_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서의 카드 통계 정보 조회"""
        query = select(SensorRawRFID).where(SensorRawRFID.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawRFID.time >= start_time)
        if end_time:
            query = query.where(SensorRawRFID.time <= end_time)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "card_stats": None,
                "read_success_rate": None
            }
        
        # 카드 타입별 분포
        card_types = {}
        for data in data_list:
            if data.card_type:
                card_types[data.card_type] = card_types.get(data.card_type, 0) + 1
        
        # 읽기 성공률 계산
        total_reads = len(data_list)
        successful_reads = sum(1 for d in data_list if d.read_success)
        read_success_rate = successful_reads / total_reads if total_reads > 0 else 0
        
        # 고유 카드 수 계산
        unique_cards = len(set(d.card_id for d in data_list if d.card_id))
        
        stats = {
            "device_id": device_id,
            "total_records": total_reads,
            "card_stats": {
                "unique_cards": unique_cards,
                "total_reads": total_reads,
                "successful_reads": successful_reads,
                "failed_reads": total_reads - successful_reads
            },
            "read_success_rate": read_success_rate,
            "card_type_distribution": card_types
        }
        
        return stats
    
    async def get_read_history(
        self,
        device_id: str,
        card_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서의 읽기 이력 조회"""
        query = select(SensorRawRFID).where(SensorRawRFID.device_id == device_id)
        
        if card_id:
            query = query.where(SensorRawRFID.card_id == card_id)
        if start_time:
            query = query.where(SensorRawRFID.time >= start_time)
        if end_time:
            query = query.where(SensorRawRFID.time <= end_time)
        
        # 시간 역순으로 정렬
        query = query.order_by(SensorRawRFID.time.desc())
        
        result = await self.db.execute(query)
        history_data = result.scalars().all()
        
        # 카드별 읽기 이력
        card_history = {}
        for data in history_data:
            if data.card_id:
                if data.card_id not in card_history:
                    card_history[data.card_id] = []
                
                card_history[data.card_id].append({
                    "timestamp": data.time,
                    "read_success": data.read_success,
                    "card_type": data.card_type
                })
        
        return {
            "device_id": device_id,
            "total_records": len(history_data),
            "unique_cards": len(card_history),
            "card_history": card_history,
            "filtered_by_card": card_id is not None
        }
