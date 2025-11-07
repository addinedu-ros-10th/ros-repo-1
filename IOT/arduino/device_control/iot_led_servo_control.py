from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint
from typing import Literal, Dict, Optional
import requests
import uvicorn

# ========= 설정 =========
ESP32_HOST = "192.168.0.3"                  # <-- ESP32 IP 주소
DEVICE_ID  = "esp_32"                        # ✅ ESP32 스케치의 DEVICE_ID와 동일
ESP32_BASE = f"http://{ESP32_HOST}"

TIMEOUT = 5  # 초
# =======================

app = FastAPI(
    title="ESP32 제어 테스트 API (Proxy to ESP32)",
    description="HTTP를 통해 ESP32의 LED/서보를 제어하는 프록시 API입니다.",
    version="2.0.0"
)

# 임시 상태(로컬 캐시 용도) — 실제 제어는 ESP32로 프록시
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
@app.get("/health", summary="프록시/ESP32 상태")
def health():
    data = esp32_get("/health")
    return {
        "status": "ok",
        "proxy": "running",
        "esp32_health": data,
        "esp32_host": ESP32_HOST
    }


# ---------- LED ----------
@app.get("/control/{device_id}/led", response_model=DeviceControlResponse, summary="LED 상태 조회(ESP32 프록시)")
def get_led_state(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_get(f"/control/{DEVICE_ID}/led")
    # 로컬 캐시 업데이트
    state = str(data.get("state", "off"))
    DEVICE_STATES.setdefault(device_id, {})["led"] = state

    return DeviceControlResponse(
        message=f"장치 {device_id} LED 상태: '{state}'",
        state=state,
        device=device_id
    )


@app.post("/control/{device_id}/led", response_model=DeviceControlResponse, summary="LED 상태 변경(ESP32 프록시)")
def set_led_state(device_id: str, payload: LedControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_post(f"/control/{DEVICE_ID}/led", {"state": payload.state})
    state = str(data.get("state", payload.state))
    DEVICE_STATES.setdefault(device_id, {})["led"] = state

    return DeviceControlResponse(
        message=f"장치 {device_id} LED를 '{state}'로 변경했습니다.",
        state=state,
        device=device_id
    )


# ---------- SERVO ----------
@app.get("/control/{device_id}/servo", response_model=DeviceControlResponse, summary="서보 각도 조회(ESP32 프록시)")
def get_servo_angle(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_get(f"/control/{DEVICE_ID}/servo")
    angle = int(data.get("angle", DEVICE_STATES.get(device_id, {}).get("servo_angle", 90)))
    DEVICE_STATES.setdefault(device_id, {})["servo_angle"] = angle

    return DeviceControlResponse(
        message=f"장치 {device_id} 서보 각도: {angle}°",
        angle=angle,
        device=device_id
    )


@app.post("/control/{device_id}/servo", response_model=DeviceControlResponse, summary="서보 각도 변경(ESP32 프록시)")
def set_servo_angle(device_id: str, payload: ServoControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    data = esp32_post(f"/control/{DEVICE_ID}/servo", {"angle": int(payload.angle)})
    angle = int(data.get("angle", payload.angle))
    DEVICE_STATES.setdefault(device_id, {})["servo_angle"] = angle

    return DeviceControlResponse(
        message=f"장치 {device_id} 서보 각도를 {angle}°로 변경했습니다.",
        angle=angle,
        device=device_id
    )


# ---------- 로컬 실행 ----------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
