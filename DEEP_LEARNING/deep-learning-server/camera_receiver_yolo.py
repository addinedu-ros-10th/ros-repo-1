import socket, struct, time, cv2, numpy as np

from ultralytics import YOLO

PORT = 5005
GC_SEC = 0.7    # 프레임 타임아웃(수신 느리면 1.0~1.5로)
SHOW_WINDOW = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 큰 수신 버퍼 확보 (커널이 허용하는 한도 내에서)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8*1024*1024)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(0.5)

if SHOW_WINDOW:
    cv2.namedWindow("UDP MJPEG", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("UDP MJPEG", 800, 600)

frames = {}  # frame_id -> {"chunks": dict, "total": int, "t0": float}

print("수신 대기 중...")

last_gc = time.time()

try:
    while True:
        # 가비지 컬렉션(타임아웃 프레임 드롭)
        now = time.time()
        if now - last_gc > 0.2:
            stale = [fid for fid,d in frames.items() if now - d["t0"] > GC_SEC]
            for fid in stale:
                del frames[fid]
            last_gc = now

        try:
            data, _ = sock.recvfrom(65535)
        except socket.timeout:
            # 표준 GUI 루프
            if SHOW_WINDOW and cv2.waitKey(1) == ord('q'):
                break
            continue

        if len(data) < 8:
            continue
        frame_id, seq, total = struct.unpack("!IHH", data[:8])
        payload = data[8:]

        # 새 프레임 시작
        if frame_id not in frames:
            frames[frame_id] = {"chunks": {}, "total": total, "t0": time.time()}
        entry = frames[frame_id]
        entry["chunks"][seq] = payload
        entry["total"] = total  # 혹시 변동되면 최신 유지

        # 완성?
        if len(entry["chunks"]) == entry["total"]:
            jpg = b"".join(entry["chunks"][i] for i in range(entry["total"]))
            del frames[frame_id]

            img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                # 손상 추적
                with open(f"bad_{frame_id}.jpg", "wb") as f:
                    f.write(jpg)
                continue

            if SHOW_WINDOW:
                model = YOLO("best.pt")

                rotated_img = cv2.rotate(img, cv2.ROTATE_180)

                results = model(rotated_img)
                show_image = results[0].plot()
                cv2.imshow("UDP MJPEG", show_image)
                if cv2.waitKey(1) == ord('q'):
                    break

finally:
    sock.close()
    if SHOW_WINDOW:
        cv2.destroyAllWindows()
