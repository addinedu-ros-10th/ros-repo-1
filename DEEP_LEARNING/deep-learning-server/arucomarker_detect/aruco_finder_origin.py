#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP로 받은 MJPEG 프레임을 재조립 → ArUco 검출 → (선택) 자세/거리 추정
[V5]
- SSH 명령어 따옴표 처리 개선: bash -lc "..." 내부의 명령어를 안전하게 전달
- 서비스 존재 프리체크 로직 유지
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
import pexpect

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

time_count = 0.0

# --------- 퍼블리시 ------------

class Talker(Node):

    def __init__(self, marker_num):
        super().__init__("lcd_aruco")

        self.publisher_ = self.create_publisher(String, "/lcd/status", 5)
        self.timer = self.create_timer(0.02, self.timer_callback)

        self.marker_num = marker_num

    def timer_callback(self):
        msg = String()
        msg.data = f"{self.marker_num}"
        self.publisher_.publish(msg)
        self.get_logger().info(f'publishing: "{msg.data}"')

# ---------- SSH 유틸 ----------

def remote_has_service(ip, user, password, ros_distro, ws_setup, service_name="/set_emotion",
                       timeout_connect=15, timeout_exec=15) -> bool:
    """원격에서 서비스 존재 여부 확인"""
    # 따옴표를 안전하게 처리한 명령어 구성
    remote_cmd = (
        f"bash -lc \"source /opt/ros/{ros_distro}/setup.bash && "
        f"source {ws_setup} && "
        f"ros2 service list | grep -w {service_name} || true\""
    )
    # ssh user@host 'remote_cmd' 대신 ssh user@host remote_cmd 를 사용하고 pexpect가 따옴표를 처리하도록 합니다.
    # pexpect.spawn()에 인자로 전달하기 위해 공백으로 분리된 리스트 사용
    ssh_args = ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{ip}", remote_cmd]

    try:
        child = pexpect.spawn(ssh_args[0], ssh_args[1:], encoding="utf-8", timeout=timeout_connect)
        i = child.expect([r'password:', pexpect.EOF, pexpect.TIMEOUT])
        if i == 0:
            child.sendline(password)
            child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=timeout_exec)
        output = child.before or ""
        return service_name in output
    except Exception as e:
        print(f"[warn] remote_has_service 예외: {e}")
        return False


def call_ros2_service_with_ssh(
    ip: str,
    user: str,
    password: str,
    service: str,
    srv_type: str,
    yaml_body: str,
    ros_distro: str = "jazzy",
    ros_ws_setup: str = "~/pinky_pro/install/setup.bash",
    timeout_connect: int = 20,
    timeout_exec: int = 30,
) -> bool:
    """
    pexpect로 SSH 접속 → bash -lc → source → ros2 service call <service> <srv_type> "<yaml_body>"
    """
    # 1. 원격에서 실행될 명령어 (YAML 바디는 이중 따옴표로 감쌈)
    ros_cmd = f'ros2 service call {service} {srv_type} "{yaml_body}"'

    # 2. bash -lc 내부 명령어 구성 (source 실패 시 다음 명령 실행 방지를 위해 && 사용)
    remote_cmd = (
        f"bash -lc \"source /opt/ros/{ros_distro}/setup.bash && "
        f"source {ros_ws_setup} && "
        f"{ros_cmd}\""
    )
    
    # 3. pexpect.spawn()에 전달할 명령어 리스트 구성
    ssh_args = ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{ip}", remote_cmd]
    
    # *디버깅을 위해 문자열로 출력*
    # (실제 pexpect.spawn()은 리스트를 사용하여 셸 파싱 오류를 최소화하는 것이 좋습니다.
    # 하지만 pexpect가 단일 문자열을 받을 때 bash가 제대로 해석하도록 remote_cmd를 구성했습니다.)
    print(f"\n[SSH Call] Executing: ssh -o StrictHostKeyChecking=no {user}@{ip} {remote_cmd}")

    try:
        # pexpect.spawn(명령어 문자열, 인자 리스트) 형태를 사용하거나,
        # 단순화를 위해 pexpect.spawn(전체 명령 문자열)을 사용합니다.
        # 여기서는 단일 문자열을 사용하되, bash 내부 따옴표를 안전하게 처리했습니다.
        child = pexpect.spawn(f"ssh -o StrictHostKeyChecking=no {user}@{ip} {remote_cmd}", encoding="utf-8", timeout=timeout_connect)

        i = child.expect([
            r'password:',
            r'Are you sure you want to continue connecting \(yes/no\)\?',
            pexpect.EOF,
            pexpect.TIMEOUT
        ])

        if i == 1:
            child.sendline('yes')
            i = child.expect([r'password:', pexpect.EOF, pexpect.TIMEOUT])

        if i == 0:
            child.sendline(password)
            child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=timeout_exec)
            output = child.before or ""

            if "command not found" in output and "ros2" in output:
                print("❌ ros2를 찾지 못했습니다. (ROS 배포판/경로 확인 필요)\n", output)
                return False

            if ("Request" in output) or ("response" in output) or (service in output):
                print("✅ ROS2 서비스 호출 결과:\n", output)
                return True

            print("⚠️ 실행 출력(확인 필요):\n", output)
            return True

        print("❌ SSH 연결 실패(EOF/TIMEOUT)\n", child.before or "")
        return False

    except pexpect.exceptions.TIMEOUT:
        print("❌ SSH/ROS2 서비스 호출 시간 초과 (TIMEOUT)")
        return False
    except Exception as e:
        print(f"❌ SSH/ROS2 서비스 호출 중 예외 발생: {e}")
        return False


# ---------- (이하 UdpReassembler, load_calib, build_detector, parse_args는 변경 없음) ----------

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
    p.add_argument("--window", default="ArUco", help="표시 창 이름")

    # ROS2 SSH 호출
    p.add_argument("--ros-ip", default="192.168.0.33", help="원격 ROS 장치 IP")
    p.add_argument("--ros-user", default="pinky", help="원격 SSH 사용자")
    p.add_argument("--ros-pass", default="1", help="원격 SSH 비밀번호(보안 유의)")
    p.add_argument("--ros-distro", default="jazzy", help="ROS 배포판명 (예: jazzy/humble/foxy)")
    p.add_argument("--ros-ws-setup", default="~/pinky_pro/install/setup.bash",
                   help="원격 워크스페이스 install/setup.bash 경로")
    p.add_argument("--service", default="/set_emotion", help="호출할 서비스 이름")
    p.add_argument("--srv-type", default="pinky_interfaces/srv/Emotion", help="서비스 타입")
    p.add_argument("--emotion", default="happy", help="감정값(e.g., happy/sad/neutral)")
    p.add_argument("--call-interval", type=float, default=2.0, help="서비스 호출 최소 간격(초)")
    p.add_argument("--require-service", action="store_true",
                   help="서비스가 떠 있지 않으면 호출 시도 자체를 생략")

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
    rclpy.init()

    global time_count

    args = parse_args()

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

    # ROS 2 호출 타이밍/상태
    last_service_call_time = 0.0
    last_service_check_time = 0.0
    service_exists_cache = None  # None: 모름, True/False: 캐시

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

            # JPEG -> BGR
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue

            if args.flip_v:
                img = cv2.flip(img, 0)

            # 그레이 변환(가드)
            try:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except cv2.error as e:
                print("[warn] cvtColor error -> skip:", e)
                continue

            # 마커 검출(가드)
            try:
                if use_new_api:
                    corners, ids, _rej = detector.detectMarkers(gray)
                else:
                    corners, ids, _rej = aruco.detectMarkers(gray, dictionary, parameters=params)
            except cv2.error as e:
                print("[warn] detectMarkers error -> skip:", e)
                continue

            if ids is not None and len(ids) > 0:
                ids = ids.flatten()
                keep_idx = list(range(len(ids))) if args.ids is None else [
                    i for i, mid in enumerate(ids) if mid in args.ids
                ]

                if keep_idx:
                    draw_corners = [corners[i] for i in keep_idx]
                    draw_ids = ids[keep_idx]
                    aruco.drawDetectedMarkers(img, draw_corners, draw_ids.reshape(-1, 1))

                    if time_count == 0 or (time.time() - time_count > 5):

                        node_talker = Talker(ids)  

                        rclpy.spin_once(node_talker)

                        time_count = time.time()

                    """간헐적 정지가 발생하는 위치"""
                    # ---- ROS2 호출 (빈도 제한 + 서비스 프리체크) ----
                    now = time.time()
                    if now - last_service_call_time > args.call_interval:
                        # 서비스 존재 캐시 갱신
                        if (service_exists_cache is None) or (now - last_service_check_time > 5.0):
                            print(f"[info] 원격 서비스 {args.service} 존재 여부 확인 중...")
                            service_exists_cache = remote_has_service(
                                args.ros_ip, args.ros_user, args.ros_pass,
                                args.ros_distro, args.ros_ws_setup, args.service
                            )
                            last_service_check_time = now
                            if not service_exists_cache:
                                print(f"[info] 원격 서비스 {args.service} 가 보이지 않습니다. (SKIP)")
                        
                        # 호출 조건 확인
                        should_call = (not args.require_service) or service_exists_cache

                        if should_call:
                            # ROS2 YAML 바디 생성
                            yaml_body = f"{{emotion: {args.emotion}}}"
                            # 호출 시도
                            threading.Thread(
                                target=call_ros2_service_with_ssh,
                                args=(
                                    args.ros_ip, args.ros_user, args.ros_pass,
                                    args.service, args.srv_type, yaml_body,
                                    args.ros_distro, args.ros_ws_setup
                                ),
                                daemon=True
                            ).start()
                            last_service_call_time = now
                    # -----------------------------------------------

                    # 자세/거리
                    if K is not None and D is not None:
                        rvecs, tvecs, _obj = aruco.estimatePoseSingleMarkers(
                            draw_corners, marker_len_m, K, D
                        )
                        for (rvec, tvec, mid) in zip(rvecs, tvecs, draw_ids):
                            R, _ = cv2.Rodrigues(rvec[0])
                            yaw_deg = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
                            z = float(tvec[0][2])
                            cv2.putText(
                                img, f"ID {mid}  z={z:.2f}m  yaw={yaw_deg:+.1f}deg",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
                            )
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
        node_talker.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()