"""
iot-data-server API 클라이언트
"""
import httpx
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IoTDataClient:
    """iot-data-server API 클라이언트"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = 10.0
    
    async def get_resident_info(self, user_id: Optional[str] = None, 
                               nickname: Optional[str] = None) -> Dict[str, Any]:
        """
        어르신 정보 조회
        
        Args:
            user_id: 사용자 ID (UUID)
            nickname: 어르신 애칭
        
        Returns:
            어르신 정보 딕셔너리
        
        Raises:
            ValueError: user_id와 nickname이 모두 None인 경우
            httpx.HTTPStatusError: API 호출 실패
        """
        if not user_id and not nickname:
            raise ValueError("user_id 또는 nickname 중 하나는 필수입니다")
        
        # user_id가 있으면 직접 조회
        if user_id:
            url = f"{self.base_url}/api/residents/{user_id}"
        else:
            # nickname으로 검색: /api/residents/search/{keyword} API 사용
            url = f"{self.base_url}/api/residents/search/{nickname}"
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    residents = response.json()
                    
                    # 검색 API는 리스트를 반환
                    if isinstance(residents, list):
                        if len(residents) == 0:
                            raise ValueError(f"nickname '{nickname}'에 해당하는 어르신을 찾을 수 없습니다")
                        # 첫 번째 결과의 user_id로 상세 정보 조회
                        first_resident = residents[0]
                        resident_user_id = first_resident.get("user_id")
                        if resident_user_id:
                            # 상세 정보 조회
                            return await self.get_resident_info(user_id=resident_user_id)
                        else:
                            # user_id가 없으면 첫 번째 결과 반환
                            return first_resident
                    else:
                        raise ValueError("예상치 못한 API 응답 형식입니다")
            except httpx.HTTPStatusError as e:
                logger.error(f"어르신 검색 실패: {e.response.status_code} - {e.response.text}")
                raise ValueError(f"어르신 정보 조회 실패: {e.response.status_code}")
            except ValueError:
                # 이미 처리된 ValueError는 재발생
                raise
            except Exception as e:
                logger.error(f"어르신 검색 중 오류: {e}")
                raise ValueError(f"어르신 정보 조회 중 오류: {str(e)}")
        
        # user_id로 직접 조회
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"iot-data-server API 호출 실패: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"iot-data-server API 호출 중 오류: {e}")
            raise
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 기본 정보 조회
        
        Args:
            user_id: 사용자 ID (UUID)
        
        Returns:
            사용자 정보 딕셔너리
        """
        url = f"{self.base_url}/api/users/{user_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"사용자 정보 조회 실패: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"사용자 정보 조회 중 오류: {e}")
            raise
    
    async def get_user_relationships(self, user_id: str, as_target: bool = True) -> List[Dict[str, Any]]:
        """
        사용자 관계 정보 조회
        
        Args:
            user_id: 사용자 ID (UUID)
            as_target: True면 target_user_id로, False면 subject_user_id로 조회
        
        Returns:
            관계 정보 리스트
        """
        if as_target:
            url = f"{self.base_url}/api/user-relationships/user/{user_id}/as-target"
        else:
            url = f"{self.base_url}/api/user-relationships/user/{user_id}/as-subject"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"사용자 관계 정보 조회 실패: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"사용자 관계 정보 조회 중 오류: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 프로필 정보 조회
        
        Args:
            user_id: 사용자 ID (UUID)
        
        Returns:
            사용자 프로필 정보 딕셔너리
        """
        url = f"{self.base_url}/api/user-profiles/{user_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"사용자 프로필 정보 조회 실패: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"사용자 프로필 정보 조회 중 오류: {e}")
            raise
    
    async def health_check(self) -> bool:
        """iot-data-server 헬스 체크"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False

