#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP로 받은 MJPEG 프레임을 재조립 → ArUco 검출 → (선택) 자세/거리 추정
[V2 개선 사항]
1. 상하 반전(cv2.flip(img, 0))을 `--flip-v` 인수로 분리
2. 코너 정밀화 방법을 'SUBPIX'에서 'CONTOUR' (기본값)으로 변경하여 안정성 향상
3. 전처리 블러(GaussianBlur) 제거
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
                    # 가장 오래된 프레임 제거 (Cleanup)
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
                # 시간 초과된 프레임 제거
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
    # 파라미터 유지 (작은 마커/불균일 조명에 강하게)
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 23
    params.adaptiveThreshWinSizeStep = 10
    params.adaptiveThreshConstant = 7

    params.minMarkerPerimeterRate = 0.02
    params.maxMarkerPerimeterRate = 4.0

    # 코너 정밀화 기본값 (CONTOUR)으로 변경하여 안정성 향상
    params.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR 
    params.cornerRefinementWinSize = 5
    params.cornerRefinementMaxIterations = 50
    params.cornerRefinementMinAccuracy = 0.01

    params.markerBorderBits = 1
    params.detectInvertedMarker = True

    # OpenCV 4.7+ 전용 API 여부 감지
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
            
            # 재조립이 아직 완료되지 않았으면 대기
            if jpg is None:
                continue

            # JPEG → BGR
            # UDP 손실로 인한 잘못된 데이터일 경우 디코딩 실패 가능성이 있음
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if img is None:
                # 디코딩 실패 (패킷 손실 등으로 JPEG 데이터가 유효하지 않음)
                # print(f"⚠️ Warning: Failed to decode JPEG for frame ID {frame_id}")
                continue

            # 상하 반전 (옵션으로 제어)
            if args.flip_v:
                img = cv2.flip(img, 0)

            # 전처리: 그레이스케일만 사용 (블러 제거)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # gray = cv2.GaussianBlur(gray, (3, 3), 0) # 블러 제거

            # 검출
            if use_new_api:
                corners, ids, _rej = detector.detectMarkers(gray)
            else:
                corners, ids, _rej = aruco.detectMarkers(gray, dictionary, parameters=params)

            if ids is not None and len(ids) > 0:
                ids = ids.flatten()

                # 관심 ID 필터
                keep_idx = list(range(len(ids))) if args.ids is None else [
                    i for i, mid in enumerate(ids) if mid in args.ids
                ]

                if keep_idx:
                    draw_corners = [corners[i] for i in keep_idx]
                    draw_ids = ids[keep_idx]
                    aruco.drawDetectedMarkers(img, draw_corners, draw_ids.reshape(-1, 1))

                    # 포즈 추정
                    if K is not None and D is not None:
                        rvecs, tvecs, _obj = aruco.estimatePoseSingleMarkers(
                            draw_corners, marker_len_m, K, D
                        )
                        for (rvec, tvec, mid) in zip(rvecs, tvecs, draw_ids):
                            R, _ = cv2.Rodrigues(rvec[0])
                            # Z축(깊이) 및 Yaw(회전) 계산
                            yaw_deg = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
                            z = float(tvec[0][2])
                            
                            # ID / 거리 / Yaw 표시
                            cv2.putText(
                                img, f"ID {mid}  z={z:.2f}m  yaw={yaw_deg:+.1f}deg",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
                            )
                            # 좌표축 표시
                            if args.show_axis:
                                cv2.drawFrameAxes(img, K, D, rvec[0], tvec[0], marker_len_m * 0.5)
                    else:
                        cv2.putText(
                            img, f"Detected IDs: {list(draw_ids)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
                        )
                else:
                    cv2.putText(
                        img, "Detected IDs (filtered out)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2, cv2.LINE_AA
                    )
            else:
                cv2.putText(
                    img, "No markers",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 255), 2, cv2.LINE_AA
                )

            # FPS
            now = time.time()
            tq.append(now - last_t)
            last_t = now
            if len(tq) >= 5:
                fps = 1.0 / (sum(tq) / len(tq))
                cv2.putText(
                    img, f"FPS: {fps:.1f}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA
                )

            cv2.imshow(args.window, img)
            if cv2.waitKey(1) & 0xFF in (27, ord('q')):
                break

    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()