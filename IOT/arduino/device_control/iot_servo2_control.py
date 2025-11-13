from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint
from typing import Literal, Dict, Optional
import requests
import uvicorn

# ========= 설정 =========
ESP32_HOST = "192.168.0.30"                  # <-- ESP32 IP 주소
DEVICE_ID  = "esp_32"                        # <-- ESP32 스케치의 DEVICE_ID와 동일
ESP32_BASE = f"http://{ESP32_HOST}"

TIMEOUT = 5  # 초
# =======================

app = FastAPI(
    title="ESP32 Dual Servo Control API (Proxy)",
    description="ESP32의 LED 및 2개의 서보모터를 HTTP로 제어하는 프록시 서버입니다.",
    version="3.0.0"
)

# 로컬 캐시
DEVICE_STATES: Dict[str, Dict[str, str | int]] = {}


# ---------- 요청/응답 모델 ----------
class LedControl(BaseModel):
    state: Literal["on", "off"]

class ServoControl(BaseModel):
    angle: conint(ge=0, le=180)

class DeviceControlResponse(BaseModel):
    status: str = "success"
    message: str
    state: Optional[str] = None
    angle: Optional[int] = None
    servo: Optional[str] = None
    device: Optional[str] = None
    proxy: Optional[str] = "fastapi"


# ---------- 내부 유틸 ----------
def esp32_get(path: str):
    try:
        r = requests.get(f"{ESP32_BASE}{path}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="ESP32 timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"ESP32 GET error: {e}")


def esp32_post(path: str, payload: dict):
    try:
        r = requests.post(f"{ESP32_BASE}{path}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="ESP32 timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"ESP32 POST error: {e}")


# ---------- Health ----------
@app.get("/health")
def health():
    data = esp32_get("/health")
    return {
        "status": "ok",
        "proxy": "running",
        "esp32_health": data,
        "esp32_host": ESP32_HOST
    }


# ---------- LED ----------
@app.get("/control/{device_id}/led", response_model=DeviceControlResponse)
def get_led_state(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_get(f"/control/{DEVICE_ID}/led")
    state = data.get("state", "off")
    DEVICE_STATES.setdefault(device_id, {})["led"] = state

    return DeviceControlResponse(
        message=f"LED 상태 조회",
        state=state,
        device=device_id
    )


@app.post("/control/{device_id}/led", response_model=DeviceControlResponse)
def set_led_state(device_id: str, payload: LedControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_post(f"/control/{DEVICE_ID}/led", {"state": payload.state})
    state = data.get("state", payload.state)
    DEVICE_STATES.setdefault(device_id, {})["led"] = state

    return DeviceControlResponse(
        message=f"LED 상태 변경 완료",
        state=state,
        device=device_id
    )


# ============================================================
# =============== SERVO 1 (GPIO 5) ============================
# ============================================================

@app.get("/control/{device_id}/servo1", response_model=DeviceControlResponse)
def get_servo1_angle(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_get(f"/control/{DEVICE_ID}/servo1")
    angle = int(data.get("angle", 90))
    DEVICE_STATES.setdefault(device_id, {})["servo1_angle"] = angle

    return DeviceControlResponse(
        message="서보1 각도 조회",
        angle=angle,
        servo="servo1",
        device=device_id
    )


@app.post("/control/{device_id}/servo1", response_model=DeviceControlResponse)
def set_servo1_angle(device_id: str, payload: ServoControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_post(f"/control/{DEVICE_ID}/servo1", {"angle": payload.angle})
    angle = int(data.get("angle", payload.angle))
    DEVICE_STATES.setdefault(device_id, {})["servo1_angle"] = angle

    return DeviceControlResponse(
        message="서보1 각도 변경 완료",
        angle=angle,
        servo="servo1",
        device=device_id
    )


# ============================================================
# =============== SERVO 2 (GPIO 18) ===========================
# ============================================================

@app.get("/control/{device_id}/servo2", response_model=DeviceControlResponse)
def get_servo2_angle(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_get(f"/control/{DEVICE_ID}/servo2")
    angle = int(data.get("angle", 90))
    DEVICE_STATES.setdefault(device_id, {})["servo2_angle"] = angle

    return DeviceControlResponse(
        message="서보2 각도 조회",
        angle=angle,
        servo="servo2",
        device=device_id
    )


@app.post("/control/{device_id}/servo2", response_model=DeviceControlResponse)
def set_servo2_angle(device_id: str, payload: ServoControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_post(f"/control/{DEVICE_ID}/servo2", {"angle": payload.angle})
    angle = int(data.get("angle", payload.angle))
    DEVICE_STATES.setdefault(device_id, {})["servo2_angle"] = angle

    return DeviceControlResponse(
        message="서보2 각도 변경 완료",
        angle=angle,
        servo="servo2",
        device=device_id
    )


# ---------- 실행 ----------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
