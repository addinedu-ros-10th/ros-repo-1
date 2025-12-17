from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, field_validator
from typing import Literal, Dict, Optional
import requests
import uvicorn

# ========= 설정 =========
ESP32_HOST = "192.168.0.4"                  # <-- ESP32 IP 주소
DEVICE_ID  = "esp_32"                        # <-- ESP32 스케치의 DEVICE_ID와 동일
ESP32_BASE = f"http://{ESP32_HOST}"

TIMEOUT = 5  # 초
# =======================

app = FastAPI(
    title="ESP32 Dual Servo + 4 LEDs Control API (Proxy)",
    description="ESP32의 LED 4개 및 2개의 서보모터를 HTTP로 제어하는 프록시 서버입니다.",
    version="4.0.0"
)

# 로컬 캐시
DEVICE_STATES: Dict[str, Dict[str, object]] = {}


# ---------- 요청/응답 모델 ----------
class LedControl(BaseModel):
    """4색 LED를 제어하는 요청 바디 (보낸 항목만 변경됨)"""
    red: Optional[int] = None    # 0 or 1
    yellow: Optional[int] = None
    blue: Optional[int] = None
    green: Optional[int] = None

    @field_validator("red", "yellow", "blue", "green")
    @classmethod
    def check_0_or_1(cls, v):
        if v is None:
            return v
        if v not in (0, 1):
            raise ValueError("LED 값은 0 또는 1이어야 합니다.")
        return v


class ServoControl(BaseModel):
    angle: conint(ge=0, le=180)


class DeviceControlResponse(BaseModel):
    status: str = "success"
    message: str
    state: Optional[str] = None          # (이전 단일 LED용, 지금은 안 써도 됨)
    angle: Optional[int] = None
    servo: Optional[str] = None
    device: Optional[str] = None
    leds: Optional[Dict[str, int]] = None
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
    # esp32 /health 그대로 리턴 + proxy 정보 추가
    return {
        "status": "ok",
        "proxy": "running",
        "esp32_health": data,
        "esp32_host": ESP32_HOST
    }


# ============================================================
# ==================== 4채널 LED =============================
# ============================================================

@app.get("/control/{device_id}/leds", response_model=DeviceControlResponse)
def get_leds_state(device_id: str):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    # ESP32의 /control/esp_32/leds 호출
    data = esp32_get(f"/control/{DEVICE_ID}/leds")
    leds = data.get("leds", {})

    # 로컬 캐시에 저장
    DEVICE_STATES.setdefault(device_id, {})["leds"] = leds

    return DeviceControlResponse(
        message="LED 상태 조회",
        device=device_id,
        leds=leds
    )


@app.post("/control/{device_id}/leds", response_model=DeviceControlResponse)
def set_leds_state(device_id: str, payload: LedControl):
    if device_id != DEVICE_ID:
        raise HTTPException(status_code=404, detail="Unknown device_id")

    # 요청 바디에서 None이 아닌 값만 추출 → 그 색상만 변경
    led_payload: Dict[str, int] = {}
    if payload.red is not None:
        led_payload["red"] = payload.red
    if payload.yellow is not None:
        led_payload["yellow"] = payload.yellow
    if payload.blue is not None:
        led_payload["blue"] = payload.blue
    if payload.green is not None:
        led_payload["green"] = payload.green

    if not led_payload:
        raise HTTPException(status_code=400, detail="변경할 LED 값이 없습니다. (red/yellow/blue/green 중 최소 1개 필요)")

    data = esp32_post(f"/control/{DEVICE_ID}/leds", led_payload)
    leds = data.get("leds", led_payload)

    DEVICE_STATES.setdefault(device_id, {})["leds"] = leds

    return DeviceControlResponse(
        message="LED 상태 변경 완료",
        device=device_id,
        leds=leds
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
