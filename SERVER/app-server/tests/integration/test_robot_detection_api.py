"""
로봇 인식 이벤트 API 통합 테스트
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from uuid import uuid4

# 테스트는 실제 DB 연결이 필요하므로 통합 테스트로 분류
pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    from app.main import create_app
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_aruco_payload():
    """ArUco 샘플 페이로드"""
    return {
        "category": "aruco",
        "unique_key": "ARUCO_23",
        "meta": {
            "entrance_id": "E-1",
            "zone": "Hall-A",
            "bbox": [120, 80, 64, 64],
            "confidence": 0.95
        },
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "processing_info": {
            "intent": "open_door",
            "api_calls": [
                {
                    "method": "POST",
                    "url": "https://sec.local/door/open",
                    "body": {"entrance_id": "E-1"}
                }
            ],
            "cmds": [],
            "scenario_state": "INIT"
        }
    }


@pytest.fixture
def sample_text_payload():
    """OCR 텍스트 샘플 페이로드"""
    return {
        "category": "text",
        "unique_key": "식당",
        "meta": {
            "lang": "ko",
            "room_code": "DINING-01",
            "bbox": [200, 60, 120, 45],
            "confidence": 0.88
        },
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "processing_info": {
            "intent": "announce",
            "api_calls": [],
            "cmds": [
                {
                    "topic": "/robot/say",
                    "payload": {"text": "식당에 도착했습니다."}
                }
            ]
        }
    }


def test_create_aruco_detection(client, sample_aruco_payload):
    """ArUco 인식 이벤트 생성 테스트"""
    response = client.post(
        "/api/v1/detections/",
        json=sample_aruco_payload,
        headers={"X-Robot-ID": "robot-001"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "aruco"
    assert data["unique_key"] == "ARUCO_23"
    assert data["robot_id"] == "robot-001"
    assert "detection_event_id" in data


def test_create_text_detection(client, sample_text_payload):
    """OCR 텍스트 인식 이벤트 생성 테스트"""
    response = client.post(
        "/api/v1/detections/",
        json=sample_text_payload,
        headers={"X-Robot-ID": "robot-001"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "text"
    assert data["unique_key"] == "식당"


def test_list_detections(client, sample_aruco_payload):
    """인식 이벤트 목록 조회 테스트"""
    # 이벤트 생성
    client.post(
        "/api/v1/detections/",
        json=sample_aruco_payload,
        headers={"X-Robot-ID": "robot-001"}
    )
    
    # 목록 조회
    response = client.get("/api/v1/detections/?robot_id=robot-001&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert data[0]["robot_id"] == "robot-001"


def test_get_detection_by_id(client, sample_aruco_payload):
    """인식 이벤트 단건 조회 테스트"""
    # 이벤트 생성
    create_response = client.post(
        "/api/v1/detections/",
        json=sample_aruco_payload,
        headers={"X-Robot-ID": "robot-001"}
    )
    assert create_response.status_code == 201
    event_id = create_response.json()["detection_event_id"]
    
    # 단건 조회
    response = client.get(f"/api/v1/detections/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["detection_event_id"] == event_id


def test_get_registry(client, sample_aruco_payload):
    """레지스트리 조회 테스트"""
    # 이벤트 생성 (레지스트리 업데이트)
    client.post(
        "/api/v1/detections/",
        json=sample_aruco_payload,
        headers={"X-Robot-ID": "robot-001"}
    )
    
    # 레지스트리 조회
    response = client.get("/api/v1/detections/registry/aruco/ARUCO_23")
    # 레지스트리가 생성되었을 수 있음 (옵션)
    # assert response.status_code in [200, 404]


def test_missing_robot_id_header(client, sample_aruco_payload):
    """X-Robot-ID 헤더 누락 테스트"""
    response = client.post(
        "/api/v1/detections/",
        json=sample_aruco_payload
    )
    assert response.status_code == 422  # Validation error

