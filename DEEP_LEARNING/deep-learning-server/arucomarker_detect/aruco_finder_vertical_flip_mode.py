#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP로 받은 MJPEG 프레임을 재조립 → ArUco 검출 → (선택) 자세/거리 추정
[최종 개선 사항]
1. 탐지 로직(detectMarkers)에는 현재 잘 작동하는 '상하 반전 전' 이미지를 사용 (detect_img).
2. 화면 표시(imshow)에는 가독성을 위한 '상하 반전 후' 이미지를 사용 (display_img).
3. 기존의 --flip-v 인수는 무시하고 강제 적용됩니다. (필요 시 주석 처리)
"""

import argparse
import socket
import struct
import time
import threading
from collections import deque

import cv2
import cv2.aruco as aruco
import numpy as np


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--ip", default="0.0.0.0", help="수신 바인드 IP")
    p.add_argument("--port", type=int, default=5005, help="수신 UDP 포트")
    p.add_argument("--rcvbuf", type=int, default=4_194_304, help="소켓 수신 버퍼")
    p.add_argument("--dict", default="4X4_50",
                   choices=["4X4_50","5X5_100","6X6_250","7X7_1000","ARUCO_ORIGINAL"],
                   help="ArUco 딕셔너리")
    p.add_argument("--marker-cm", type=float, default=3.0, help="마커 한 변(cm)")
    p.add_argument("--calib", type=str, default=None, help="캘리브 npz(K,D)")
    p.add_argument("--ids", type=int, nargs="*", default=None, help="관심 ID 목록 (미지정=모두)")
    p.add_argument("--show-axis", action="store_true", help="좌표축 렌더링(캘리브 필요)")
    p.add_argument("--flip-v", action="store_true", help="수신 이미지 상하 반전 (카메라 거꾸로일 때)")
    p.add_argument("--window", default="ArUco", help="표시 창 이름")
    return p.parse_args()


class UdpReassembler:
    """프레임 조각 재조립 버퍼"""
    def __init__(self, timeout_s=1.0, max_frames=64):
        self.frames = {}
        self.ts = {}
        self.timeout_s = timeout_s
        self.max_frames = max_frames
        self.lock = threading.Lock()

    def add(self, frame_id, seq, total, payload):
        with self.lock:
            if frame_id not in self.frames:
                if len(self.frames) >= self.max_frames:
                    oldest = min(self.ts, key=self.ts.get)
                    self.frames.pop(oldest, None)
                    self.ts.pop(oldest, None)
                self.frames[frame_id] = {"total": total, "parts": {}}
            self.frames[frame_id]["parts"][seq] = payload
            self.ts[frame_id] = time.time()

            f = self.frames[frame_id]
            if len(f["parts"]) == f["total"]:
                ordered = [f["parts"][i] for i in range(f["total"]) if i in f["parts"]]
                jpg = b"".join(ordered)
                del self.frames[frame_id]
                del self.ts[frame_id]
                return jpg
        return None

    def janitor(self):
        while True:
            time.sleep(0.5)
            now = time.time()
            with self.lock:
                stale = [fid for fid, t in self.ts.items() if now - t > self.timeout_s]
                for fid in stale:
                    self.frames.pop(fid, None)
                    self.ts.pop(fid, None)


def load_calib(npz_path):
    data = np.load(npz_path)
    K = data["K"].astype(np.float32)
    D = data["D"].astype(np.float32).reshape(-1, 1)
    return K, D


def build_detector(dict_name: str):
    dict_map = {
        "4X4_50": aruco.DICT_4X4_50,
        "5X5_100": aruco.DICT_5X5_100,
        "6X6_250": aruco.DICT_6X6_250,
        "7X7_1000": aruco.DICT_7X7_1000,
        "ARUCO_ORIGINAL": aruco.DICT_ARUCO_ORIGINAL
    }
    dictionary = aruco.getPredefinedDictionary(dict_map[dict_name])

    params = aruco.DetectorParameters()
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 23
    params.adaptiveThreshWinSizeStep = 10
    params.adaptiveThreshConstant = 7
    params.minMarkerPerimeterRate = 0.02
    params.maxMarkerPerimeterRate = 4.0
    params.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR 
    params.cornerRefinementWinSize = 5
    params.cornerRefinementMaxIterations = 50
    params.cornerRefinementMinAccuracy = 0.01
    params.markerBorderBits = 1
    params.detectInvertedMarker = True

    use_new_api = hasattr(aruco, "ArucoDetector")
    detector = aruco.ArucoDetector(dictionary, params) if use_new_api else (dictionary, params)
    return detector, dictionary, params, use_new_api


def main():
    args = parse_args()

    # UDP 소켓
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.rcvbuf)
    sock.bind((args.ip, args.port))
    print(f"[Receiver] {args.ip}:{args.port} | SO_RCVBUF={args.rcvbuf}")

    # 재조립기 + 청소 스레드
    reasm = UdpReassembler(timeout_s=1.0)
    threading.Thread(target=reasm.janitor, daemon=True).start()

    # ArUco detector
    detector, dictionary, params, use_new_api = build_detector(args.dict)
    marker_len_m = args.marker_cm / 100.0

    # 캘리브
    K, D = (None, None)
    if args.calib:
        K, D = load_calib(args.calib)
        print(f"[Calib] Loaded: {args.calib}")

    tq = deque(maxlen=20)
    last_t = time.time()
    cv2.namedWindow(args.window, cv2.WINDOW_NORMAL)

    try:
        while True:
            pkt, _ = sock.recvfrom(2048)
            if len(pkt) < 8:
                continue
            frame_id, seq, total = struct.unpack("!IHH", pkt[:8])
            jpg = reasm.add(frame_id, seq, total, pkt[8:])
            
            if jpg is None:
                continue

            # JPEG → BGR (img는 현재 뒤집힌 상태의 원본 이미지)
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if img is None:
                continue
                
            # -------------------------------------------------------------
            # 🚨 화면 표시와 탐지 이미지 분리 로직 (핵심 수정)
            
            # 1. 탐지용 이미지: 현재 탐지가 잘 되는 상태인 원본 img를 사용
            detect_img = img.copy() 
            
            # 2. 표시용 이미지: 사용자 화면에 제대로 보이기 위해 상하 반전 적용
            display_img = cv2.flip(img, 0)
            
            # -------------------------------------------------------------

            # 전처리: 그레이스케일 변환은 탐지용 이미지(detect_img)에 적용
            gray = cv2.cvtColor(detect_img, cv2.COLOR_BGR2GRAY)

            # 검출
            # 🚨 탐지에는 detect_img 기반의 gray를 사용
            try:
                if use_new_api:
                    corners, ids, _rej = detector.detectMarkers(gray)
                else:
                    corners, ids, _rej = aruco.detectMarkers(gray, dictionary, parameters=params)
            except cv2.error as e:
                print(f"⚠️ ArUco detect failed (Skipping frame due to OpenCV error): {e}")
                continue
                
            
            if ids is not None and len(ids) > 0:
                ids = ids.flatten()

                # 관심 ID 필터
                keep_idx = list(range(len(ids))) if args.ids is None else [
                    i for i, mid in enumerate(ids) if mid in args.ids
                ]

                if keep_idx:
                    draw_corners = [corners[i] for i in keep_idx]
                    draw_ids = ids[keep_idx]
                    
                    # 🚨 3. 탐지 결과는 표시용 이미지(display_img)에 그립니다.
                    aruco.drawDetectedMarkers(display_img, draw_corners, draw_ids.reshape(-1, 1))

                    # 포즈 추정
                    if K is not None and D is not None:
                        rvecs, tvecs, _obj = aruco.estimatePoseSingleMarkers(
                            draw_corners, marker_len_m, K, D
                        )
                        for (rvec, tvec, mid) in zip(rvecs, tvecs, draw_ids):
                            R, _ = cv2.Rodrigues(rvec[0])
                            yaw_deg = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
                            z = float(tvec[0][2])
                            
                            # 🚨 4. 텍스트/축도 표시용 이미지(display_img)에 그립니다.
                            cv2.putText(
                                display_img, f"ID {mid}  z={z:.2f}m  yaw={yaw_deg:+.1f}deg",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
                            )
                            # 좌표축 표시
                            if args.show_axis:
                                cv2.drawFrameAxes(display_img, K, D, rvec[0], tvec[0], marker_len_m * 0.5)
                    else:
                        cv2.putText(
                            display_img, f"Detected IDs: {list(draw_ids)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
                        )
                else:
                    cv2.putText(
                        display_img, "Detected IDs (filtered out)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2, cv2.LINE_AA
                    )
            else:
                cv2.putText(
                    display_img, "No markers",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 255), 2, cv2.LINE_AA
                )

            # FPS
            now = time.time()
            tq.append(now - last_t)
            last_t = now
            if len(tq) >= 5:
                fps = 1.0 / (sum(tq) / len(tq))
                cv2.putText(
                    display_img, f"FPS: {fps:.1f}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA
                )

            # 🚨 5. 화면 표시: display_img (상하 반전이 보정되어 가독성이 좋은 이미지)를 사용
            cv2.imshow(args.window, display_img)
            if cv2.waitKey(1) & 0xFF in (27, ord('q')):
                break

    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()