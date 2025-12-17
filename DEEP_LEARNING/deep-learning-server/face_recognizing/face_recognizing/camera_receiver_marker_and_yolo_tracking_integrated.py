#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP로 받은 MJPEG 프레임을 재조립 → ArUco 검출 → 핑키 도킹 제어(/cmd_vel)
- 화면 중앙에 사각형(도킹 박스)을 항상 표시
- 마커 중심이 도킹 박스 중앙으로 오도록 회전 제어
"""

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

"""=== yolo 파트 모듈 및 전역 변수 ==="""
import socket
import struct
import time

import cv2
import numpy as np
import math

from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Float32MultiArray
from geometry_msgs.msg import Twist  # 추가된 부분

tracking_switch = False
process_basic_flag = False
process_stop_flag = False
process_yolo_flag = False
process_marker_flag = False

recognized_name = None
recognized_cls_id = None
recognized_cls_type = {"Resident": [0, 3, 7, 17], "Worker": [8, 11, 14, 15], "Visitor": [2, 5, 12, 16]}
recognized_group = None

call_information_time = 0

yolo_switch = True
marker_switch = False

def process_stop2():
    global process_stop_flag
    process_stop_flag = True

def basic_mode():
    global process_basic_flag

    process_basic_flag = True

def yolo_mode2():
    global process_yolo_flag
    
    process_yolo_flag = True

def marker_mode2():
    global process_marker_flag

    process_marker_flag = True


"""=== 아루코마커 파트 함수 ==="""

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

class PinkyDockController_Marker:
    """마커 위치를 보고 /cmd_vel 로 핑키를 움직이는 간단한 P제어 컨트롤러"""

    def __init__(self, node: Node,
                 target_dist=0.6,
                 kp_lin=0.2,
                 kp_ang=0.3,
                 max_lin=0.1,
                 max_ang=0.7,
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
            
            if abs(ang_z) > abs(self.max_ang):
                ang_z = self.max_ang
            else:
                ang_z = self.kp_ang * norm_err_x

        # 직진/후진 제어
        lin_x = 0.0
        # if z_m is not None:
        #     z_m = float(z_m)
        #     err_dist = self.target_dist - z_m
        #     if abs(err_dist) > self.dist_deadzone:
        #         lin_x = self.kp_lin * err_dist
        #         lin_x = max(-self.max_lin, min(self.max_lin, lin_x))

        h, w = img.shape[:2]
        ratio = 0.3
        box_w, box_h = int(w * ratio), int(h * ratio)
        cx = w // 2
        cy = h // 2
        x1 = cx - box_w // 2
        x2 = cx + box_w // 2
        marker_x1 = marker_corners[0, 0]
        marker_x2 = marker_corners[1, 0]

        err_marker_x = marker_x1 - marker_x2

        if abs( abs(err_marker_x) - ( abs(x1 - x2) * 0.5) ) < 20:
            lin_x = 0
        elif abs(err_marker_x) > abs(x1 - x2) * 0.5:
            lin_x = -1 * self.kp_lin * abs(err_marker_x)
        elif abs(err_marker_x) < abs(x1 - x2) * 0.5:
            lin_x = self.kp_lin * abs(err_marker_x)

        if lin_x > self.max_lin:
            lin_x = self.max_lin
        elif lin_x < -self.max_lin:
            lin_x = -self.max_lin

        lin_x = float(lin_x)
        ang_z = -float(ang_z)

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

"""=== YOLO 파트 함수 목록 ==="""
# 코드 A에서 사용한 PinkyDockController 클래스
class PinkyDockController_YOLO:
    """마커 위치를 보고 /cmd_vel 로 핑키를 움직이는 간단한 P제어 컨트롤러"""

    def __init__(self, node: Node,
                 target_dist=0.6,
                 kp_lin=0.2,
                 kp_ang=0.6,
                 max_lin=0.1,
                 max_ang=2.0,
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
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pub.publish(msg)

    def update_from_marker(self, img, x1, x2, z_m=None):
        """
        img: 현재 BGR 이미지 (사이즈 정보용)
        marker_corners: (4, 2) ndarray (해당 마커의 꼭지점)
        z_m: 카메라-마커 거리(m). 없으면 None (그럼 거리 제어는 생략)
        """
        h, w = img.shape[:2]
        cx = w / 2
        cy = h / 2

        mx = int((x1 + x2) / 2)
        # pixel error (x방향)
        err_px = mx - cx
        norm_err_x = err_px / (w * 0.5)  # -1 ~ 1 근처

        # 회전 제어 방향: 마커가 오른쪽이면 +, 왼쪽이면 -
        ang_z = 0.0
        if err_px > 0:
            ang_z = self.kp_ang * norm_err_x
        elif abs(err_px) <= 20:
            ang_z = 0
        elif err_px < 0:
            ang_z = self.kp_ang * norm_err_x

        if ang_z > self.max_ang:
            ang_z = self.max_ang
        elif ang_z < -self.max_ang:
            ang_z = -self.max_ang


        # 직진/후진 제어
        lin_x = 0.0

        err_marker_x = abs(x1 - x2)

        print("x: ", err_marker_x, "w: ", w)

        if err_marker_x > w * 0.6:
            lin_x = self.kp_lin * err_marker_x
        elif abs(err_marker_x - (w * 0.6)) <= 40:
            lin_x = 0
        else:
            lin_x = - self.kp_lin * err_marker_x

        if lin_x > self.max_lin:
            lin_x = self.max_lin
        elif lin_x < -self.max_lin:
            lin_x = -self.max_lin

        lin_x = -float(lin_x)
        ang_z = -float(ang_z)

        self.node.get_logger().info(f"cmd_vel lin_x={lin_x:.3f}, ang_z={ang_z:.3f}")

        msg = Twist()
        msg.linear.x = lin_x
        msg.angular.z = ang_z
        self.pub.publish(msg)

    def check_lost(self):
        """주기적으로 호출해서, 마커가 안 보일 때 로봇을 정지시키기"""
        if self.last_seen_time <= 0:
            return
        if time.time() - self.last_seen_time > self.lost_timeout:
            self.stop()
            self.last_seen_time = 0.0
        else:
            return

"""====== 일반 함수 영역 ======"""
def computeIoU(box_current_coordinate, box_previous_coordinate):
    ax1, ay1, ax2, ay2 = box_current_coordinate
    bx1, by1, bx2, by2 = box_previous_coordinate

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = abs(inter_x2 - inter_x1)
    inter_height = abs(inter_y2 - inter_y1)
    inter_area = inter_width * inter_height

    area_a = abs(ax2 - ax1) * abs(ay2 - ay1)
    area_b = abs(bx2 - bx1) * abs(by2 - by1)

    union = area_a + area_b - inter_area

    iou = inter_area / union if union != 0 else 0

    return iou

def computeCenter(box_current_coordinate, box_previous_coordinate):
    ax1, ay1, ax2, ay2 = box_current_coordinate

    if len(box_previous_coordinate) == 4:
        bx1, by1, bx2, by2 = box_previous_coordinate
    else:
        bx1, by1 = box_previous_coordinate
        bx2, by2 = bx1, by1
    
    center_ax = (ax1 + ax2) / 2
    center_ay = (ay1 + ay2) / 2

    center_bx = (bx1 + bx2) / 2
    center_by = (by1 + by2) / 2

    center_dist_x = center_ax - center_bx
    center_dist_y = center_ay - center_by

    center_dist = math.sqrt(center_dist_x**2 + center_dist_y**2)

    return center_dist

def changeTrackingSwitch():
    if tracking_switch is True:
        tracking_switch = False
    else:
        tracking_switch = True

def main_yolo_marker():
    rclpy.init()
    global process_stop_flag
    global process_yolo_flag
    global process_basic_flag

    global yolo_switch
    global marker_switch 

    start_flag = True
    call_information_flag = False
    time_gap = 0

    node_marker = rclpy.create_node("pinky_aruco_docking")

    dock_ctrl_marker = PinkyDockController_Marker(
        node_marker,
        target_dist=0.6, # 도킹 목표 거리 (m)
        kp_lin=0.8, # 직진 P 게인
        kp_ang=1.0, # 회전 P 게인
        max_lin=0.2, # 최대 전진 속도(m/s)
        max_ang=1.0, # 최대 회전 속도(rad/s)
        pixel_deadzone=20, # 중앙에서 px 오차 데드존
        dist_deadzone=0.05, # 거리 데드존(m)
        lost_timeout=0.5, # 마커 분실 후 정지까지 시간(s)
    )

    """====== YOLO 초기 변수 ======"""
    switch_time = None

    global yolo_switch              # yolo 모드 실행
    global marker_switch            # marker 모드 실행
    global process_stop_flag        # 프로세스 정지(API용)
    global process_marker_flag      # marker 모드 실행(API용)   

    global tracking_switch

    global recognized_name
    global recognized_cls_id
    global recognized_cls_type
    global recognized_group

    call_information_flag = False
    global call_information_time
    
    time_gap = 0

    start_flag = True

    frame_count = 0
    bbox_previous_coordinate = None

    central_coordinate = [320, 240]
    screen_width = 640
    screen_height = 480
    max_distance = math.sqrt(central_coordinate[0]**2 + central_coordinate[1]**2)

    target_coord_x1 = None
    target_coord_y1 = None
    target_coord_x2 = None
    target_coord_y2 = None

    node_yolo = rclpy.create_node("pinky_recognize_and_tracking")

    dock_ctrl_yolo = PinkyDockController_YOLO(node_yolo)

    """====== 메인 코드 ======"""

    marker_cm = 3.0 # 마커 한 변(cm)
    calib = None # npz(K,D) 보정 파일 경로
    aruco_ids = None # 관심 ID 목록(미지정=모두)
    aruco_dict = """4X4_50""" # aruco 딕셔너리 옵션. ["4X4_50", "5X5_100", "6X6_250", "7X7_1000", "ARUCO_ORIGINAL"] 중에서 선택 사용
    show_axis = False # 좌표축 표시(보정 필요)
    flip_v = False # 영상 상하 반전
    window = "ArUco Docking" # 표시 창 이름

    # UDP 소켓
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 194 * 304)
    sock.bind(("0.0.0.0", 5005))
    sock.settimeout(0.5)

    # 재조립기 + 청소 스레드
    reasm = UdpReassembler(timeout_s=1.0)
    threading.Thread(target=reasm.janitor, daemon=True).start()

    # ArUco
    detector, dictionary, params, use_new_api = build_detector(aruco_dict)
    marker_len_m = marker_cm / 100.0

    # 보정
    K, D = (None, None)
    if calib:
        K, D = load_calib(calib)
        print(f"[Calib] Loaded: {calib}")

    # FPS
    tq = deque(maxlen=20)
    last_t = time.time()
    # cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    # 시작 화면
    dummy = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy, "Waiting for frames...", (60, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
    draw_center_box(dummy)  # 시작화면에도 박스 보이게
    cv2.imshow("UDP MJPEG", dummy)
    cv2.waitKey(1)
    print("[INFO] OpenCV window created. Waiting for frames...")

    try:
        while True:

            current_time = time.time()

            pkt, _ = sock.recvfrom(65535)
            if len(pkt) < 8:
                dock_ctrl_marker.check_lost()
                continue
            frame_id, seq, total = struct.unpack("!IHH", pkt[:8])
            jpg = reasm.add(frame_id, seq, total, pkt[8:])
            if jpg is None:
                dock_ctrl_marker.check_lost()
                continue

            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            img = cv2.rotate(img, cv2.ROTATE_180) # 180도 회전
            img_yolo = img
            if img is None:
                dock_ctrl_marker.check_lost()
                continue

            # 상하반전 옵션
            if flip_v:
                img = cv2.flip(img, 0)

            # 항상 도킹 박스 먼저 그리기
            draw_center_box(img)

            # 그레이 변환
            try:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except cv2.error as e:
                print("[warn] cvtColor error -> skip:", e)
                dock_ctrl_marker.check_lost()
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
                dock_ctrl_marker.check_lost()
                continue

            if ids is not None and len(ids) > 0:
                ids = ids.flatten()
                keep_idx = list(range(len(ids))) if aruco_ids is None else [
                    i for i, mid in enumerate(ids) if mid in aruco_ids
                ]

                if keep_idx:
                    draw_corners = [corners[i] for i in keep_idx]
                    draw_ids = ids[keep_idx]
                    aruco.drawDetectedMarkers(
                        img, draw_corners, draw_ids.reshape(-1, 1)
                    )

                    main_corners = draw_corners[0].reshape(-1, 2)

                    # print("corners (px):")
                    # print(main_corners)

                    
                    # for i, (x, y) in enumerate(main_corners):
                    #     print(f"  corner (px): mx={x:.1f}")

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
                        if show_axis:
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
                        
                    time_gap = current_time - call_information_time

                    if call_information_flag is True and marker_switch is True and yolo_switch is False:
                        if time_gap > 30 or start_flag is True:
                            print("recognized_marker_ID: ", draw_ids[0])
                            call_information_time = time.time()
                            
                            start_flag = False
                        else:
                            print(f"이미 {int(time_gap)}초 전에 정보를 호출했습니다. {int(30 - time_gap)}초 후에 다시 시도해 주세요.")
                        call_information_flag = False
                            

                    # 도킹 제어
                    if marker_switch is True and yolo_switch is False:
                        dock_ctrl_marker.update_from_marker(img, main_corners, z_m=z_m)

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
                    dock_ctrl_marker.check_lost()
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
                dock_ctrl_marker.check_lost()

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

            """====== YOLO 파트 ======"""

            if switch_time is None:
                switch_time = time.time()

            current_time = time.time()

            if current_time - switch_time > 0.1:
                # YOLO 얼굴 인식 코드
                model = YOLO("best_demon_slayer_v8n_parameter_tuning.pt")
                results = model(img_yolo)

                class_names = model.names

                bbox_all_cls_id = []
                bbox_all_coodinate = []
                bbox_all_iou = []
                bbox_all_center_distance = []

                bbox_all_cost = []

                control_input_x1 = None
                control_input_x2 = None

                idx = None

                for result in results:
                    if len(result.boxes) > 0:
                        dock_ctrl_yolo.last_seen_time = current_time
                        for box in result.boxes:
                            cls_id = int(box.cls[0])
                            x1, y1, x2, y2 = box.xyxy[0]

                            x1 = int(x1)
                            x2 = int(x2)
                            y1 = int(y1)
                            y2 = int(y2)

                            box_coordinate = [x1, y1, x2, y2]
                            bbox_all_coodinate.append(box_coordinate)
                            bbox_all_cls_id.append(cls_id)

                            if bbox_previous_coordinate is not None:
                                iou = computeIoU(box_coordinate, bbox_previous_coordinate)
                                bbox_all_iou.append(iou)
                                center_distance = computeCenter(box_coordinate, bbox_previous_coordinate)
                                bbox_all_center_distance.append(center_distance)
                            elif bbox_all_coodinate is not []:
                                iou = 0
                                bbox_all_iou.append(iou)
                                center_distance = computeCenter(box_coordinate, central_coordinate) 
                                bbox_all_center_distance.append(center_distance)

                        if len(bbox_all_iou) > 0 and len(bbox_all_center_distance) > 0:
                            for i in range(0, len(bbox_all_iou)):
                                cost = (1 - bbox_all_iou[i]) + (bbox_all_center_distance[i] / max_distance)
                                bbox_all_cost.append(cost)
                                # print("cost: ", cost)

                            min_cost = min(bbox_all_cost)
                            # print("minimum cost: ", min_cost)

                        for i in range(0, len(bbox_all_cost)):
                            if bbox_all_cost[i] == min_cost:
                                idx = i
                                # print("idx: ", idx)
                                break

                        control_input_x1 = bbox_all_coodinate[idx][0]
                        control_input_x2 = bbox_all_coodinate[idx][2]

                        cls_id_input = bbox_all_cls_id[idx]

                        # print("cls_id_input: ", cls_id_input)
                        # print("control_input: ", control_input_x1, control_input_x2)

                        recognized_name = class_names[cls_id_input]
                        recognized_cls_id = cls_id_input

                        for key, value in recognized_cls_type.items():
                            if cls_id_input in value:
                                recognized_group = key
                                break

                        time_gap = current_time - call_information_time

                        if call_information_flag is True and yolo_switch is True and marker_switch is False:
                            if time_gap > 30 or start_flag is True:
                                print("recognized_name    : ", recognized_name)
                                print("recognized_cls_type: ", recognized_group)
                                print("recognized_cls_id  : ", f"{recognized_cls_id}")
                                call_information_time = time.time()
                        
                                start_flag = False
                            else:
                                print(f"이미 {int(time_gap)}초 전에 정보를 호출했습니다. {int(30 - time_gap)}초 후에 다시 시도해 주세요.")
                                call_information_flag = False

                        bbox_previous_coordinate = bbox_all_coodinate[idx]

                        if yolo_switch is True and marker_switch is False:
                            if tracking_switch is True:
                                dock_ctrl_yolo.update_from_marker(img_yolo, control_input_x1, control_input_x2)
                            else:
                                bbox_previous_coordinate = None
                                dock_ctrl_yolo.stop()
                    
                    elif yolo_switch is True and marker_switch is False:
                        dock_ctrl_yolo.stop()

                    # print(tracking_switch)

                # show_image = results[0].plot()

                if idx is not None:
                    target_coord_x1 = bbox_all_coodinate[idx][0]
                    target_coord_y1 = bbox_all_coodinate[idx][1]
                    target_coord_x2 = bbox_all_coodinate[idx][2]
                    target_coord_y2 = bbox_all_coodinate[idx][3]

                    cv2.rectangle(img, (target_coord_x1, target_coord_y1),
                                    (target_coord_x2, target_coord_y2),
                                    (0, 255, 255), 2)
                    
                    cv2.putText(img, f"Name:  {recognized_name}", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: {recognized_group}", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    {recognized_cls_id}", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                elif current_time - dock_ctrl_yolo.last_seen_time < 1.0:
                    cv2.putText(img, f"Name:  {recognized_name}", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: {recognized_group}", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    {recognized_cls_id}", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, f"Name:  None", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: None", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    None", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                switch_time = current_time
                # print(frame_count)
                frame_count = 0

            else:
                if tracking_switch is True:
                    cv2.rectangle(img, (target_coord_x1, target_coord_y1),
                                (target_coord_x2, target_coord_y2),
                                (0, 255, 255), 2)
                    cv2.putText(img, f"Name:  {recognized_name}", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: {recognized_group}", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    {recognized_cls_id}", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                elif current_time - dock_ctrl_yolo.last_seen_time < 1.0:
                    cv2.putText(img, f"Name:  {recognized_name}", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: {recognized_group}", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    {recognized_cls_id}", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                else:
                    cv2.putText(img, f"Name:  None", (320, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"Group: None", (320, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                    cv2.putText(img, f"ID:    None", (320, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 0), 2, cv2.LINE_AA)
                        
                    
            frame_count += 1

            cv2.imshow("UDP MJPEG", img)

            key_input = cv2.waitKey(1)
            if key_input == ord('q') or process_stop_flag is True:
                process_stop_flag = False
                break
            elif key_input == ord('w'):
                print("Tracking activated")
                tracking_switch = True
            elif key_input == ord('e'):
                print("Tracking deactivated")
                tracking_switch = False
            elif key_input == ord('r'):
                call_information_flag = True
            elif key_input == ord('i') or process_yolo_flag is True:
                process_yolo_flag = False
                yolo_switch = True
                marker_switch = False
            elif key_input == ord('o') or process_marker_flag is True:
                process_marker_flag = False
                yolo_switch = False
                marker_switch = True

    finally:
        try:
            if rclpy.ok():
                dock_ctrl_marker.stop()
                dock_ctrl_yolo.stop()
        except Exception:
            pass

        try:
            if rclpy.ok():
                node_marker.destroy_node()
                node_yolo.destroy_node()
                rclpy.shutdown()
        except Exception:
            pass

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main_yolo_marker()
