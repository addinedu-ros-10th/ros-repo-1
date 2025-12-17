#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP로 받은 MJPEG 프레임을 재조립 → ArUco 검출 → 핑키 도킹 제어(/cmd_vel)
- 화면 중앙에 사각형(도킹 박스)을 항상 표시
- 마커 중심이 도킹 박스 중앙으로 오도록 회전 제어
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

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# ---------- 인자 파서 ----------

def parse_args():
    p = argparse.ArgumentParser()
    # UDP 수신
    p.add_argument("--ip", default="0.0.0.0", help="수신 바인드 IP")
    p.add_argument("--port", type=int, default=5005, help="수신 UDP 포트")
    p.add_argument("--rcvbuf", type=int, default=4_194_304, help="소켓 수신 버퍼 크기")

    # ArUco
    p.add_argument("--dict", default="4X4_50",
                   choices=["4X4_50", "5X5_100", "6X6_250", "7X7_1000", "ARUCO_ORIGINAL"],
                   help="ArUco 딕셔너리")
    p.add_argument("--marker-cm", type=float, default=3.0, help="마커 한 변(cm)")
    p.add_argument("--calib", type=str, default=None, help="npz(K,D) 보정 파일 경로")
    p.add_argument("--ids", type=int, nargs="*", default=None, help="관심 ID 목록(미지정=모두)")
    p.add_argument("--show-axis", action="store_true", help="좌표축 표시(보정 필요)")
    p.add_argument("--flip-v", action="store_true", help="영상 상하 반전")
    p.add_argument("--window", default="ArUco Docking", help="표시 창 이름")

    # 도킹 제어 파라미터
    p.add_argument("--target-dist", type=float, default=0.6, help="도킹 목표 거리(m)")
    p.add_argument("--kp-lin", type=float, default=0.8, help="직진 P 게인")
    p.add_argument("--kp-ang", type=float, default=1.0, help="회전 P 게인")
    p.add_argument("--max-lin", type=float, default=0.2, help="최대 전진 속도(m/s)")
    p.add_argument("--max-ang", type=float, default=1.0, help="최대 회전 속도(rad/s)")
    p.add_argument("--pixel-deadzone", type=int, default=20, help="중앙에서 px 오차 데드존")
    p.add_argument("--dist-deadzone", type=float, default=0.05, help="거리 데드존(m)")
    p.add_argument("--lost-timeout", type=float, default=0.5,
                   help="마커 분실 후 정지까지 시간(s)")

    return p.parse_args()


# ---------- UDP 재조립기 ----------

class UdpReassembler:
    """프레임 조각 재조립 버퍼"""
    def __init__(self, timeout_s=1.0, max_frames=64):
        self.frames = {}
        self.ts = {}
        self.timeout_s = timeout_s
        self.max_frames = max_frames
        self.lock = threading.Lock()

    def add(self, frame_id, seq, total, payload):
        """조각 추가 → 프레임이 완성되면 jpg bytes 반환, 아니면 None"""
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
        """오래된(타임아웃) 프레임 삭제"""
        while True:
            time.sleep(0.5)
            now = time.time()
            with self.lock:
                stale = [fid for fid, t in self.ts.items() if now - t > self.timeout_s]
                for fid in stale:
                    self.frames.pop(fid, None)
                    self.ts.pop(fid, None)


# ---------- 카메라 보정 로드 ----------

def load_calib(npz_path):
    data = np.load(npz_path)
    K = data["K"].astype(np.float32)
    D = data["D"].astype(np.float32).reshape(-1, 1)
    return K, D


# ---------- ArUco Detector 생성 ----------

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


# ---------- 핑키 도킹 컨트롤러 ----------

class PinkyDockController:
    """마커 위치를 보고 /cmd_vel 로 핑키를 움직이는 간단한 P제어 컨트롤러"""

    def __init__(self, node: Node,
                 target_dist=0.6,
                 kp_lin=0.8,
                 kp_ang=1.0,
                 max_lin=0.2,
                 max_ang=1.0,
                 pixel_deadzone=20,
                 dist_deadzone=0.05,
                 lost_timeout=0.5):
        self.node = node
        self.pub = node.create_publisher(Twist, "/cmd_vel", 10)

        self.target_dist = target_dist
        self.kp_lin = kp_lin
        self.kp_ang = kp_ang
        self.max_lin = max_lin
        self.max_ang = max_ang
        self.pixel_deadzone = pixel_deadzone
        self.dist_deadzone = dist_deadzone

        self.last_seen_time = 0.0
        self.lost_timeout = lost_timeout  # s: 이 시간 동안 마커가 안 보이면 정지

    def stop(self):
        msg = Twist()
        msg.linear.x = float(0.0)
        msg.angular.z = float(0.0)
        self.pub.publish(msg)

    def update_from_marker(self, img, marker_corners, z_m=None):
        """
        img: 현재 BGR 이미지 (사이즈 정보용)
        marker_corners: (4, 2) ndarray (해당 마커의 꼭지점)
        z_m: 카메라-마커 거리(m). 없으면 None (그럼 거리 제어는 생략)
        """
        h, w = img.shape[:2]

        # 도킹 박스 중심(항상 메인 루프에서 그리지만 여기서도 좌표만 사용)
        box_w, box_h = int(w * 0.3), int(h * 0.3)
        cx = w // 2
        cy = h // 2

        # 마커 중심
        mx = float(marker_corners[:, 0].mean())
        my = float(marker_corners[:, 1].mean())

        # 중심 표시
        cv2.circle(img, (int(mx), int(my)), 5, (0, 255, 255), -1)
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)

        # pixel error (x방향)
        err_px = mx - cx
        norm_err_x = err_px / (w / 2.0)  # -1 ~ 1 근처

        # 회전 제어 방향: 마커가 오른쪽이면 +, 왼쪽이면 -
        ang_z = 0.0
        if abs(err_px) > self.pixel_deadzone:
            ang_z = self.kp_ang * norm_err_x
            ang_z = max(-self.max_ang, min(self.max_ang, ang_z))

        # 직진/후진 제어 (거리 정보 있을 때만)
        lin_x = 0.0
        if z_m is not None:
            z_m = float(z_m)
            err_dist = self.target_dist - z_m
            if abs(err_dist) > self.dist_deadzone:
                lin_x = self.kp_lin * err_dist
                lin_x = max(-self.max_lin, min(self.max_lin, lin_x))

        lin_x = float(lin_x)
        ang_z = float(ang_z)

        self.node.get_logger().info(f"cmd_vel lin_x={lin_x:.3f}, ang_z={ang_z:.3f}")

        msg = Twist()
        msg.linear.x = lin_x
        msg.angular.z = ang_z
        self.pub.publish(msg)

        self.last_seen_time = time.time()

        # 디버그 텍스트
        text = f"err_px={err_px:.1f}"
        if z_m is not None:
            text += f", z={z_m:.2f}m"
        cv2.putText(
            img,
            text,
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    def check_lost(self):
        """주기적으로 호출해서, 마커가 안 보일 때 로봇을 정지시키기"""
        if self.last_seen_time <= 0:
            return
        if time.time() - self.last_seen_time > self.lost_timeout:
            self.stop()
            self.last_seen_time = 0.0


# ---------- 중앙 도킹 박스 그리기 ----------

def draw_center_box(img, ratio=0.3):
    """항상 화면 중앙에 파란 도킹 박스를 그림"""
    h, w = img.shape[:2]
    box_w, box_h = int(w * ratio), int(h * ratio)
    cx = w // 2
    cy = h // 2
    x1 = cx - box_w // 2
    y1 = cy - box_h // 2
    x2 = cx + box_w // 2
    y2 = cy + box_h // 2
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
    return cx, cy


# ---------- 메인 루프 ----------

def main():
    args = parse_args()
    rclpy.init()

    node = rclpy.create_node("pinky_aruco_docking")
    dock_ctrl = PinkyDockController(
        node,
        target_dist=args.target_dist,
        kp_lin=args.kp_lin,
        kp_ang=args.kp_ang,
        max_lin=args.max_lin,
        max_ang=args.max_ang,
        pixel_deadzone=args.pixel_deadzone,
        dist_deadzone=args.dist_deadzone,
        lost_timeout=args.lost_timeout,
    )

    # UDP 소켓
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.rcvbuf)
    sock.bind((args.ip, args.port))
    print(f"[Receiver] {args.ip}:{args.port} | SO_RCVBUF={args.rcvbuf}")

    # 재조립기 + 청소 스레드
    reasm = UdpReassembler(timeout_s=1.0)
    threading.Thread(target=reasm.janitor, daemon=True).start()

    # ArUco
    detector, dictionary, params, use_new_api = build_detector(args.dict)
    marker_len_m = args.marker_cm / 100.0

    # 보정
    K, D = (None, None)
    if args.calib:
        K, D = load_calib(args.calib)
        print(f"[Calib] Loaded: {args.calib}")

    # FPS
    tq = deque(maxlen=20)
    last_t = time.time()
    cv2.namedWindow(args.window, cv2.WINDOW_NORMAL)

    # 시작 화면
    dummy = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy, "Waiting for frames...", (60, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
    draw_center_box(dummy)  # 시작화면에도 박스 보이게
    cv2.imshow(args.window, dummy)
    cv2.waitKey(1)
    print("[INFO] OpenCV window created. Waiting for frames...")

    try:
        while True:
            pkt, _ = sock.recvfrom(2048)
            if len(pkt) < 8:
                dock_ctrl.check_lost()
                continue
            frame_id, seq, total = struct.unpack("!IHH", pkt[:8])
            jpg = reasm.add(frame_id, seq, total, pkt[8:])
            if jpg is None:
                dock_ctrl.check_lost()
                continue

            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                dock_ctrl.check_lost()
                continue

            # 상하반전 옵션
            if args.flip_v:
                img = cv2.flip(img, 0)

            # 항상 도킹 박스 먼저 그리기
            draw_center_box(img)

            # 그레이 변환
            try:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except cv2.error as e:
                print("[warn] cvtColor error -> skip:", e)
                dock_ctrl.check_lost()
                continue

            # 마커 검출
            try:
                if use_new_api:
                    corners, ids, _rej = detector.detectMarkers(gray)
                else:
                    corners, ids, _rej = aruco.detectMarkers(
                        gray, dictionary, parameters=params
                    )
            except cv2.error as e:
                print("[warn] detectMarkers error -> skip:", e)
                dock_ctrl.check_lost()
                continue

            if ids is not None and len(ids) > 0:
                ids = ids.flatten()
                keep_idx = list(range(len(ids))) if args.ids is None else [
                    i for i, mid in enumerate(ids) if mid in args.ids
                ]

                if keep_idx:
                    draw_corners = [corners[i] for i in keep_idx]
                    draw_ids = ids[keep_idx]
                    aruco.drawDetectedMarkers(
                        img, draw_corners, draw_ids.reshape(-1, 1)
                    )

                    main_corners = draw_corners[0].reshape(-1, 2)

                    z_m = None
                    if K is not None and D is not None:
                        rvecs, tvecs, _obj = aruco.estimatePoseSingleMarkers(
                            draw_corners, marker_len_m, K, D
                        )
                        rvec = rvecs[0]
                        tvec = tvecs[0]
                        z_m = float(tvec[0][2])

                        R, _ = cv2.Rodrigues(rvec[0])
                        yaw_deg = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
                        cv2.putText(
                            img,
                            f"ID {draw_ids[0]}  z={z_m:.2f}m  yaw={yaw_deg:+.1f}deg",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA,
                        )
                        if args.show_axis:
                            cv2.drawFrameAxes(
                                img, K, D, rvec[0], tvec[0], marker_len_m * 0.5
                            )
                    else:
                        cv2.putText(
                            img,
                            f"Detected IDs: {list(draw_ids)}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA,
                        )

                    # 도킹 제어
                    dock_ctrl.update_from_marker(img, main_corners, z_m=z_m)

                else:
                    cv2.putText(
                        img,
                        "Detected IDs (filtered out)",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 200, 200),
                        2,
                        cv2.LINE_AA,
                    )
                    dock_ctrl.check_lost()
            else:
                cv2.putText(
                    img,
                    "No markers",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (60, 60, 255),
                    2,
                    cv2.LINE_AA,
                )
                dock_ctrl.check_lost()

            # FPS
            now = time.time()
            tq.append(now - last_t)
            last_t = now
            if len(tq) >= 5:
                fps = 1.0 / (sum(tq) / len(tq))
                cv2.putText(
                    img,
                    f"FPS: {fps:.1f}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow(args.window, img)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break

    finally:
        cv2.destroyAllWindows()
        try:
            if rclpy.ok():
                dock_ctrl.stop()
        except Exception:
            pass

        try:
            if rclpy.ok():
                node.destroy_node()
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
