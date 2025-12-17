"""
Edge Reed 센서 데이터 서비스 구현체

Reed 스위치 센서의 Edge 처리된 데이터에 대한 비즈니스 로직을 관리합니다.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.interfaces.services.sensor_service_interface import IEdgeReedService
from app.interfaces.repositories.sensor_repository import IEdgeReedRepository
from app.api.v1.schemas import EdgeReedDataCreate, EdgeReedDataUpdate, EdgeReedDataResponse


class EdgeReedService(IEdgeReedService):
    """Edge Reed 센서 데이터 서비스 구현체"""

    def __init__(self, edge_reed_repository: IEdgeReedRepository):
        self.edge_reed_repository = edge_reed_repository

    async def create_sensor_data(self, data: EdgeReedDataCreate) -> EdgeReedDataResponse:
        """Edge Reed 센서 데이터 생성"""
        # 비즈니스 규칙 검증
        if data.confidence is not None and (data.confidence < 0 or data.confidence > 1):
            raise HTTPException(
                status_code=400,
                detail="신뢰도는 0과 1 사이의 값이어야 합니다."
            )
        
        if data.processing_time is not None and data.processing_time < 0:
            raise HTTPException(
                status_code=400,
                detail="처리 시간은 0 이상이어야 합니다."
            )
        
        try:
            return await self.edge_reed_repository.create(data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 생성 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_sensor_data(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[EdgeReedDataResponse]:
        """특정 시간의 Edge Reed 센서 데이터 조회"""
        try:
            return await self.edge_reed_repository.get_by_id(device_id, timestamp)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_latest_sensor_data(self, device_id: str) -> Optional[EdgeReedDataResponse]:
        """최신 Edge Reed 센서 데이터 조회"""
        try:
            return await self.edge_reed_repository.get_latest(device_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"최신 Edge Reed 센서 데이터 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_sensor_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EdgeReedDataResponse]:
        """Edge Reed 센서 데이터 목록 조회"""
        # 비즈니스 규칙 검증
        if limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="조회 제한은 1에서 1000 사이의 값이어야 합니다."
            )
        
        if start_time and end_time and start_time >= end_time:
            raise HTTPException(
                status_code=400,
                detail="시작 시간은 종료 시간보다 이전이어야 합니다."
            )
        
        try:
            return await self.edge_reed_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def update_sensor_data(
        self,
        device_id: str,
        timestamp: datetime,
        data: EdgeReedDataUpdate
    ) -> Optional[EdgeReedDataResponse]:
        """Edge Reed 센서 데이터 수정"""
        # 비즈니스 규칙 검증
        if data.confidence is not None and (data.confidence < 0 or data.confidence > 1):
            raise HTTPException(
                status_code=400,
                detail="신뢰도는 0과 1 사이의 값이어야 합니다."
            )
        
        if data.processing_time is not None and data.processing_time < 0:
            raise HTTPException(
                status_code=400,
                detail="처리 시간은 0 이상이어야 합니다."
            )
        
        try:
            result = await self.edge_reed_repository.update(device_id, timestamp, data)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="해당 시간의 Edge Reed 센서 데이터를 찾을 수 없습니다."
                )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 수정 중 오류가 발생했습니다: {str(e)}"
            )

    async def delete_sensor_data(self, device_id: str, timestamp: datetime) -> bool:
        """Edge Reed 센서 데이터 삭제"""
        try:
            result = await self.edge_reed_repository.delete(device_id, timestamp)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="해당 시간의 Edge Reed 센서 데이터를 찾을 수 없습니다."
                )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 삭제 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_sensor_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Edge Reed 센서 데이터 통계 조회"""
        try:
            return await self.edge_reed_repository.get_statistics(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Edge Reed 센서 데이터 통계 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_switch_activation_history(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """스위치 활성화 이력 조회"""
        try:
            return await self.edge_reed_repository.get_switch_activation_history(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"스위치 활성화 이력 조회 중 오류가 발생했습니다: {str(e)}"
            )
