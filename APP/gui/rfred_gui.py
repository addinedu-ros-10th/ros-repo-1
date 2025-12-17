#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import socket
import struct
import time
import datetime

import requests
import cv2
import numpy as np

DEVICE_ID = "esp_32"
UDP_PORT = 5005
DEBUG_UDP = False  # True 로 하면 터미널에 수신 로그가 찍힘

# ==== PyQt6 우선, 없으면 PyQt5 ====
try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QTextEdit, QLabel
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QThread
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6 import uic

    PYQT_VERSION = 6
    QIMAGE_FORMAT_RGB = QImage.Format.Format_RGB888
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QTextEdit, QLabel
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QThread
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5 import uic

    PYQT_VERSION = 5
    QIMAGE_FORMAT_RGB = QImage.Format_RGB888


PASTEL_STYLE = """
QWidget {
    background-color: #F8EDE2;          /* 전체 배경 – 크림색 */
    color: #374049;
    font-family: "Noto Sans CJK KR", "Malgun Gothic", sans-serif;
    font-size: 11pt;
}

/* 그룹 박스 카드 느낌 */
QGroupBox {
    background-color: #FFF9F1;
    border: 2px solid #E0D2BC;
    border-radius: 18px;
    margin-top: 14px;
    padding: 10px 12px 14px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #8A7A5A;
}

/* 버튼 – 민트색 */
QPushButton {
    background-color: #7BC4C4;
    color: #ffffff;
    border: none;
    border-radius: 20px;
    padding: 6px 16px;
    font-weight: 600;
    font-size: 9pt;
}
QPushButton:hover {
    background-color: #66B3B8;
}
QPushButton:pressed {
    background-color: #4D97A1;
}

/* 텍스트 입력 / 로그 박스 */
QLineEdit, QTextEdit {
    background-color: #FFFDF8;
    border: 1px solid #D8C8B0;
    border-radius: 10px;
    padding: 4px 8px;
}

/* 슬라이더 */
QSlider::groove:horizontal {
    height: 6px;
    background: #E4D4C0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    background: #FFFFFF;
    border-radius: 7px;
    border: 2px solid #7BC4C4;
    margin: -5px 0;
}

/* 비디오 영역 박스 */
QLabel#video_label,
QLabel#video_label2,
QLabel#video_label3 {
    background-color: #FFF9F1;
    border: 2px solid #E0D2BC;
    border-radius: 18px;
}
"""









# =========================================
#            UDP 영상 수신 스레드
# =========================================
class UdpVideoThread(QThread):
    """
    libcamera-vid 로 MJPEG 를 UDP로 쏘는 핑키들의 영상을 받는 스레드.
    포트는 동일(5005)이고, src_ip 로 어느 로봇인지 구분한다.
    new_frame(frame, frame_bgr, src_ip)
    """
    new_frame = pyqtSignal(object, object, str)

    def __init__(self, port=UDP_PORT, parent=None):
        super().__init__(parent)
        self.port = port
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 * 1024 * 1024)
        sock.bind(("0.0.0.0", self.port))
        sock.settimeout(0.5)

        if DEBUG_UDP:
            print(f"[UdpVideoThread] listening on UDP {self.port}")

        GC_SEC = 0.7
        frames = {}  # (src_ip, frame_id) -> {chunks, total, t0}

        last_gc = time.time()
        SOI = b"\xff\xd8"
        EOI = b"\xff\xd9"

        try:
            while self._running:
                now = time.time()
                # 오래된 프레임 정리
                if now - last_gc > 0.2:
                    stale_keys = [
                        k for k, v in frames.items()
                        if now - v["t0"] > GC_SEC
                    ]
                    for k in stale_keys:
                        del frames[k]
                    last_gc = now

                try:
                    data, addr = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError:
                    break  # 소켓 닫힌 경우

                if len(data) < 8:
                    continue

                src_ip = addr[0]
                frame_id, seq, total = struct.unpack("!IHH", data[:8])
                payload = data[8:]

                key = (src_ip, frame_id)

                if key not in frames:
                    frames[key] = {
                        "chunks": {},
                        "total": total,
                        "t0": time.time(),
                    }
                entry = frames[key]
                entry["chunks"][seq] = payload
                entry["total"] = total

                # 완성되었는지 확인
                if len(entry["chunks"]) == entry["total"]:
                    jpg = b"".join(
                        entry["chunks"][i] for i in range(entry["total"])
                    )
                    del frames[key]

                    img = cv2.imdecode(
                        np.frombuffer(jpg, np.uint8),
                        cv2.IMREAD_COLOR
                    )
                    if img is None:
                        continue

                    # 필요하면 회전
                    img = cv2.rotate(img, cv2.ROTATE_180)

                    if DEBUG_UDP:
                        print(f"[UdpVideoThread] frame from {src_ip}")

                    # GUI 로 넘김
                    self.new_frame.emit(img, img, src_ip)
        finally:
            sock.close()
            if DEBUG_UDP:
                print("[UdpVideoThread] stopped")


# =========================================
#               메인 GUI
# =========================================
class Esp32ControlGui(QWidget):
    def __init__(self):
        super().__init__()

        # .ui 로 레이아웃 로드
        uic.loadUi("rfred_gui.ui", self)
        self.setWindowTitle("Rfred GUI")

        # 로그 창은 읽기 전용
        if hasattr(self, "log_edit") and isinstance(self.log_edit, QTextEdit):
            self.log_edit.setReadOnly(True)

        # ====== LED / Servo 영역 시그널 연결 ======
        # 상태 새로고침 (ESP32)
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)

        # Servo1
        self.servo1_slider.valueChanged.connect(
            lambda val: self.servo1_value_label.setText(str(val))
        )
        self.servo1_slider.sliderReleased.connect(
            lambda: self.set_servo(1, self.servo1_slider.value())
        )

        # Servo2
        self.servo2_slider.valueChanged.connect(
            lambda val: self.servo2_value_label.setText(str(val))
        )
        self.servo2_slider.sliderReleased.connect(
            lambda: self.set_servo(2, self.servo2_slider.value())
        )

        # LED 개별
        self.led_red_on.clicked.connect(lambda: self.set_led("red", 1))
        self.led_red_off.clicked.connect(lambda: self.set_led("red", 0))
        self.led_yellow_on.clicked.connect(lambda: self.set_led("yellow", 1))
        self.led_yellow_off.clicked.connect(lambda: self.set_led("yellow", 0))
        self.led_blue_on.clicked.connect(lambda: self.set_led("blue", 1))
        self.led_blue_off.clicked.connect(lambda: self.set_led("blue", 0))
        self.led_green_on.clicked.connect(lambda: self.set_led("green", 1))
        self.led_green_off.clicked.connect(lambda: self.set_led("green", 0))

        # 모두 켜기/끄기
        self.all_on_btn.clicked.connect(lambda: self.set_all_leds(1))
        self.all_off_btn.clicked.connect(lambda: self.set_all_leds(0))

        # ====== API2 영역 시그널 ======
        self.refresh_btn_2.clicked.connect(self.on_api2_refresh)
        self.api2_run.clicked.connect(self.on_api2_run)
        self.api2_stop.clicked.connect(self.on_api2_stop)
        self.api2_yolo.clicked.connect(self.on_api2_yolo)
        self.api2_tracking.clicked.connect(self.on_api2_tracking)
        self.api2_aruco.clicked.connect(self.on_api2_aruco)

        # ====== 스타일 적용 ======
        self.setup_style()

        # ====== UDP 비디오 스레드 시작 ======
        self.video_thread = UdpVideoThread(port=UDP_PORT, parent=self)
        self.video_thread.new_frame.connect(self.on_new_frame)
        self.video_thread.start()

        # 시작할 때 한 번 상태 조회
        self.on_refresh_clicked()

    # ------------- 스타일 ----------------
        # ------------- 스타일 ----------------
    def setup_style(self):
        # 윈도우 전체에 파스텔 스타일 적용
        self.setStyleSheet(PASTEL_STYLE)

        # 영상 라벨 기본 설정 (정렬만 유지)
        for name in ["video_label", "video_label2", "video_label3"]:
            lbl = getattr(self, name, None)
            if isinstance(lbl, QLabel):
                lbl.setText("")
                if PYQT_VERSION == 6:
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    lbl.setAlignment(Qt.AlignCenter)


        # 영상 라벨 기본 설정
        for name in ["video_label", "video_label2", "video_label3"]:
            lbl = getattr(self, name, None)
            if isinstance(lbl, QLabel):
                lbl.setText("")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter
                                 if PYQT_VERSION == 6 else Qt.AlignCenter)

    # ------------- 공통 유틸 ----------------
    def api_base(self) -> str:
        text = self.api_base_edit.text().strip()
        if text.endswith("/"):
            text = text[:-1]
        return text

    def api2_base(self) -> str:
        text = self.api_base_edit_2.text().strip()
        if text.endswith("/"):
            text = text[:-1]
        return text

    def time_str(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def log(self, text: str, obj=None):
        if not hasattr(self, "log_edit") or not isinstance(self.log_edit, QTextEdit):
            return

        if obj is not None:
            try:
                js = json.dumps(obj, ensure_ascii=False, indent=2)
            except Exception:
                js = str(obj)
            msg = f"[{self.time_str()}] {text}\n{js}\n"
        else:
            msg = f"[{self.time_str()}] {text}\n"

        self.log_edit.append(msg)

    def handle_request_error(self, e: Exception, context: str):
        self.log(f"{context} 실패: {e}")

    # ------------- LED 제어 ----------------
    def set_led(self, color: str, value: int):
        url = f"{self.api_base()}/control/{DEVICE_ID}/leds"
        payload = {color: value}
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.log(f"LED {color.upper()} = {value}", data)
        except Exception as e:
            self.handle_request_error(e, f"LED {color.upper()} 제어")

    def set_all_leds(self, value: int):
        url = f"{self.api_base()}/control/{DEVICE_ID}/leds"
        payload = {
            "red": value,
            "yellow": value,
            "blue": value,
            "green": value,
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.log(f"모든 LED = {value}", data)
        except Exception as e:
            self.handle_request_error(e, "모든 LED 제어")

    # ------------- Servo 제어 ----------------
    def set_servo(self, idx: int, angle: int):
        url = f"{self.api_base()}/control/{DEVICE_ID}/servo{idx}"
        payload = {"angle": int(angle)}
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.log(f"Servo{idx} 각도 = {angle}", data)
        except Exception as e:
            self.handle_request_error(e, f"Servo{idx} 제어")

    # ------------- 상태 새로고침 (ESP32) -------------
    def on_refresh_clicked(self):
        try:
            base = self.api_base()
            leds_url = f"{base}/control/{DEVICE_ID}/leds"
            s1_url = f"{base}/control/{DEVICE_ID}/servo1"
            s2_url = f"{base}/control/{DEVICE_ID}/servo2"

            leds_resp = requests.get(leds_url, timeout=5)
            leds_resp.raise_for_status()
            leds_data = leds_resp.json()

            s1_resp = requests.get(s1_url, timeout=5)
            s1_resp.raise_for_status()
            s1_data = s1_resp.json()

            s2_resp = requests.get(s2_url, timeout=5)
            s2_resp.raise_for_status()
            s2_data = s2_resp.json()

            s1_angle = int(s1_data.get("angle", 90))
            s2_angle = int(s2_data.get("angle", 90))

            self.servo1_slider.setValue(s1_angle)
            self.servo1_value_label.setText(str(s1_angle))

            self.servo2_slider.setValue(s2_angle)
            self.servo2_value_label.setText(str(s2_angle))

            self.log("상태 조회 완료", {
                "leds": leds_data.get("leds"),
                "servo1": s1_angle,
                "servo2": s2_angle,
            })

        except Exception as e:
            self.handle_request_error(e, "상태 조회")

    # ------------- API2 호출 ----------------
    def call_api2(self, path: str, label: str):
        base = self.api2_base()
        url = f"{base}{path}"
        try:
            resp = requests.post(url, timeout=5)
            resp.raise_for_status()
            # JSON 이면 JSON, 아니면 텍스트
            if "application/json" in resp.headers.get("content-type", ""):
                data = resp.json()
            else:
                data = resp.text
            self.log(f"[API2] {label} 호출 성공", data)
        except Exception as e:
            self.log(f"[API2] {label} 호출 실패: {e}")

    def on_api2_refresh(self):
        # 필요하면 /health 같은 엔드포인트를 호출하도록 바꾸면 됨
        self.log("[API2] 상태 새로고침 버튼 눌림 (엔드포인트는 아직 미구현)")

    def on_api2_run(self):
        self.call_api2("/send-signal_run_dl_program", "RUN")

    def on_api2_stop(self):
        self.call_api2("/send-signal_stop_dl_program_integrated", "STOP")

    def on_api2_yolo(self):
        # 실제 엔드포인트 이름에 맞게 수정
        self.call_api2("/send-signal_run_yolo", "YOLO")

    def on_api2_tracking(self):
        self.call_api2("/send-signal_run_tracking", "TRACKING")

    def on_api2_aruco(self):
        self.call_api2("/send-signal_run_aruco", "ARUCO")

    # ------------- 새 프레임 수신 시 ----------------
    def on_new_frame(self, frame, frame_bgr, src_ip: str):
        """
        src_ip 에 따라 어느 QLabel 에 뿌릴지 결정한다.
        - 192.168.10.10 -> video_label
        - 192.168.10.27 -> video_label2
        - 192.168.10.3  -> video_label3
        """
        mapping = {
            "192.168.10.10": getattr(self, "video_label", None),
            "192.168.10.27": getattr(self, "video_label2", None),
            "192.168.10.3": getattr(self, "video_label3", None),
        }
        target = mapping.get(src_ip)
        if target is None or not isinstance(target, QLabel):
            return

        img = frame_bgr
        h, w, ch = img.shape
        bpl = ch * w
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, bpl, QIMAGE_FORMAT_RGB)

        if PYQT_VERSION == 6:
            aspect = Qt.AspectRatioMode.KeepAspectRatio
            transform = Qt.TransformationMode.SmoothTransformation
        else:
            aspect = Qt.KeepAspectRatio
            transform = Qt.SmoothTransformation

        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(target.width(), target.height(), aspect, transform)
        target.setPixmap(pix)

    # ------------- 창 닫을 때 스레드 정리 -------------
    def closeEvent(self, event):
        if hasattr(self, "video_thread") and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait(500)
        super().closeEvent(event)


# =========================================
#                  MAIN
# =========================================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(PASTEL_STYLE)
    win = Esp32ControlGui()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
