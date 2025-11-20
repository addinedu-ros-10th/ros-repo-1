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
process_stop_flag = False

# 코드 A에서 사용한 PinkyDockController 클래스
class PinkyDockController:
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

# UDP 수신 및 MJPEG 디코딩
def main():
    rclpy.init()
    node = rclpy.create_node("pinky_recognize_and_tracking")

    """====== 초기 설정 변수 일람 ======"""
    switch_time = None

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
    """=============================="""

    # 로봇 제어 클래스 인스턴스 생성
    dock_ctrl = PinkyDockController(node)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 * 1024 * 1024)
    sock.bind(("0.0.0.0", 5005))
    sock.settimeout(0.5)

    frames = {}
    print("수신 대기 중...")

    try:
        while True:
            global tracking_switch
            global process_stop_flag

            if switch_time is None:
                switch_time = time.time()

            current_time = time.time()

            try:
                data, _ = sock.recvfrom(65535)
            except socket.timeout:
                continue

            if len(data) < 8:
                continue
            frame_id, seq, total = struct.unpack("!IHH", data[:8])
            payload = data[8:]

            if frame_id not in frames:
                frames[frame_id] = {"chunks": {}, "total": total, "t0": time.time()}
            entry = frames[frame_id]
            entry["chunks"][seq] = payload
            entry["total"] = total

            if len(entry["chunks"]) == entry["total"]:
                jpg = b"".join(entry["chunks"][i] for i in range(entry["total"]))
                del frames[frame_id]

                img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue

                rotated_img = cv2.rotate(img, cv2.ROTATE_180)

                if current_time - switch_time > 0.2:

                    # YOLO 얼굴 인식 코드
                    # model = YOLO("best_demon_slayer.pt")
                    # model = YOLO("yolo11n.pt")
                    model = YOLO("demon_slayer_parameter_tuning.pt")
                    results = model(rotated_img)

                    bbox_all_coodinate = []
                    bbox_all_iou = []
                    bbox_all_center_distance = []

                    bbox_all_cost = []

                    control_input_x1 = None
                    control_input_x2 = None

                    idx = None

                    for result in results:
                        if len(result.boxes) > 0:
                            for box in result.boxes:
                                cls_id = int(box.cls[0])
                                x1, y1, x2, y2 = box.xyxy[0]

                                x1 = int(x1)
                                x2 = int(x2)
                                y1 = int(y1)
                                y2 = int(y2)

                                box_coordinate = [x1, y1, x2, y2]
                                bbox_all_coodinate.append(box_coordinate)

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

                            if tracking_switch is True:

                                if len(bbox_all_iou) > 0 and len(bbox_all_center_distance) > 0:

                                    for i in range(0, len(bbox_all_iou)):
                                        cost = (1 - bbox_all_iou[i]) + (bbox_all_center_distance[i] / max_distance)
                                        bbox_all_cost.append(cost)
                                        print("cost: ", cost)

                                    min_cost = min(bbox_all_cost)
                                    print("minimum cost: ", min_cost)

                                for i in range(0, len(bbox_all_cost)):
                                    if bbox_all_cost[i] == min_cost:
                                        idx = i
                                        print("idx: ", idx)
                                        break

                                control_input_x1 = bbox_all_coodinate[idx][0]
                                control_input_x2 = bbox_all_coodinate[idx][2]

                                print("control_input: ", control_input_x1, control_input_x2)

                                bbox_previous_coordinate = bbox_all_coodinate[idx]

                                dock_ctrl.update_from_marker(rotated_img, control_input_x1, control_input_x2)

                            else:
                                bbox_previous_coordinate = None
                                dock_ctrl.stop()
                        
                        else:
                            dock_ctrl.stop()

                        print(tracking_switch)

                    # show_image = results[0].plot()

                    if idx is not None:
                        target_coord_x1 = bbox_all_coodinate[idx][0]
                        target_coord_y1 = bbox_all_coodinate[idx][1]
                        target_coord_x2 = bbox_all_coodinate[idx][2]
                        target_coord_y2 = bbox_all_coodinate[idx][3]

                        cv2.rectangle(show_image, (target_coord_x1, target_coord_y1),
                                        (target_coord_x2, target_coord_y2),
                                        (0, 255, 255), 1)

                    switch_time = current_time
                    print(frame_count)
                    frame_count = 0

                else:
                    show_image = rotated_img
                    if target_coord_x1 is not None and tracking_switch is True:
                        cv2.rectangle(show_image, (target_coord_x1, target_coord_y1),
                                        (target_coord_x2, target_coord_y2),
                                        (0, 255, 255), 1)

                frame_count += 1
                
                key_input = cv2.waitKey(1)

                # rectangle_coord_x1 = int(central_coordinate[0] - (screen_height / 4))
                # rectangle_coord_y1 = int(central_coordinate[1] - (screen_height / 4))
                # rectangle_coord_x2 = int(central_coordinate[0] + (screen_height / 4))
                # rectangle_coord_y2 = int(central_coordinate[1] + (screen_height / 4))


                # cv2.rectangle(show_image, (rectangle_coord_x1, rectangle_coord_y1),
                #                 (rectangle_coord_x2, rectangle_coord_y2),
                #                 (0, 255, 255), 1)
                
                cv2.imshow("UDP MJPEG", show_image)

                if key_input == ord('q') or process_stop_flag is True:
                    break
                elif key_input == ord('w'):
                    print("Tracking activated")
                    tracking_switch = True
                elif key_input == ord('e'):
                    print("Tracking deactivated")
                    tracking_switch = False
            
    finally:
        sock.close()
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

        return "yolo terminated"

if __name__ == "__main__":
    main()