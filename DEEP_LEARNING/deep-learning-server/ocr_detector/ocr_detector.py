#!/usr/bin/env python3
import socket, struct, time, cv2, numpy as np
import easyocr
from typing import List, Tuple

# =================== 설정값 ===================
PORT = 5005
GC_SEC = 0.7                # 조립 중 프레임 타임아웃
SHOW_WINDOW = True          # 영상 출력
ROTATE_180 = True           # 필요 시 화면 반전
LANGS = ['ko', 'en']        # 한국어/영어 동시 인식
USE_GPU = False             # GPU 미사용(노트북 환경에 따라 True로 가능)
OCR_EVERY = 2               # n프레임마다 OCR (부하 줄이기: 2~5 권장)
MIN_CONF = 0.5              # 최소 신뢰도
MAX_WIDTH = 1280            # 너무 큰 프레임은 리사이즈
DRAW_BOX = True             # 박스·텍스트 오버레이
PRINT_TEXT = True           # 콘솔 텍스트 출력
# ==============================================

def safe_resize(img, max_w=1280):
    h, w = img.shape[:2]
    if w <= max_w: return img
    scale = max_w / w
    return cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

def draw_easyocr_results(img, results, min_conf=0.5):
    """EasyOCR 결과를 OpenCV로 그려줌"""
    for (bbox, text, conf) in results:
        if conf < min_conf: 
            continue
        # bbox: 4점 (x,y)
        pts = np.array(bbox, dtype=np.int32)
        cv2.polylines(img, [pts], isClosed=True, color=(0,255,0), thickness=2)
        # 텍스트 배경
        x, y = pts[0]
        label = f"{text} ({conf:.2f})"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x, y - th - baseline - 4), (x + tw + 4, y), (0,255,0), -1)
        cv2.putText(img, label, (x + 2, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2, cv2.LINE_AA)

def aggregate_text(results, min_conf=0.5) -> List[Tuple[str, float]]:
    """(text, conf) 정리해 상위 신뢰도 위주로 반환"""
    pairs = [(text, conf) for (_bbox, text, conf) in results if conf >= min_conf and text.strip()]
    # 긴 텍스트가 많을 때 상위 몇 개만
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:10]

def main():
    # ---- EasyOCR 리더 1회 로드 (가장 무거움) ----
    print("[OCR] Loading EasyOCR reader...")
    reader = easyocr.Reader(LANGS, gpu=USE_GPU)
    print("[OCR] Ready.")

    # ---- UDP 소켓 준비 ----
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8*1024*1024)
    sock.bind(("0.0.0.0", PORT))
    sock.settimeout(0.5)

    if SHOW_WINDOW:
        cv2.namedWindow("UDP MJPEG + OCR", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("UDP MJPEG + OCR", 960, 720)

    frames = {}  # frame_id -> {"chunks": dict, "total": int, "t0": float}
    last_gc = time.time()
    frame_counter = 0

    print(f"[UDP] Listening on 0.0.0.0:{PORT}")

    try:
        while True:
            # 가비지 컬렉션: 오래된 프레임 버림
            now = time.time()
            if now - last_gc > 0.2:
                stale = [fid for fid, d in frames.items() if now - d["t0"] > GC_SEC]
                for fid in stale:
                    del frames[fid]
                last_gc = now

            try:
                data, _ = sock.recvfrom(65535)
            except socket.timeout:
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
            entry["total"] = total

            # 프레임 완성?
            if len(entry["chunks"]) == entry["total"]:
                jpg = b"".join(entry["chunks"][i] for i in range(entry["total"]))
                del frames[frame_id]

                img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    with open(f"bad_{frame_id}.jpg", "wb") as f:
                        f.write(jpg)
                    continue

                if ROTATE_180:
                    img = cv2.rotate(img, cv2.ROTATE_180)

                # 성능 위해 리사이즈
                img = safe_resize(img, MAX_WIDTH)

                # n프레임마다 OCR
                do_ocr = (frame_counter % OCR_EVERY == 0)
                ocr_results = []
                if do_ocr:
                    # EasyOCR는 BGR/GRAY 상관없이 내부 처리, 그대로 전달
                    # 복잡 배경이 심하면 업샘플/샤픈/대비향상(CLAHE) 등을 고려
                    ocr_results = reader.readtext(img, detail=1, paragraph=False)  # [(bbox, text, conf), ...]
                    if PRINT_TEXT:
                        pairs = aggregate_text(ocr_results, MIN_CONF)
                        if pairs:
                            print("---- OCR ----")
                            for text, conf in pairs:
                                print(f"{conf:0.2f}  {text}")
                        else:
                            print("---- OCR: (no confident text) ----")

                if SHOW_WINDOW:
                    draw_img = img.copy()
                    if DRAW_BOX and ocr_results:
                        draw_easyocr_results(draw_img, ocr_results, MIN_CONF)
                    cv2.imshow("UDP MJPEG + OCR", draw_img)
                    if cv2.waitKey(1) == ord('q'):
                        break

                frame_counter += 1

    finally:
        sock.close()
        if SHOW_WINDOW:
            cv2.destroyAllWindows()
        print("[EXIT] closed.")

if __name__ == "__main__":
    main()
