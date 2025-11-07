import socket, subprocess, time

UDP_IP = "192.168.4.18"   # 영상을 확인할 PC의 IP로 수정
UDP_PORT = 5005
MTU = 1000                 # 조각 크기 (더 보수적으로)
SLEEP_PER_PACKET = 0.0005  # 버스트 완화 (필요 시 0.001로)

# libcamera-vid: MJPEG 스트림 출력
cmd = [
    "libcamera-vid",
    "--width","640","--height","480",
    "--framerate","30",          # 낮춰서 먼저 성공
    "--codec","mjpeg",
    "--quality","65",            # 50~70 사이 권장
    "-t","0",
    "-o","-"
]

# 표준출력 버퍼링 최소화
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # 브로드캐스트 사용 시 주석 해제
SOI = b"\xff\xd8"
EOI = b"\xff\xd9"

buf = bytearray()
frame_id = 0

print("UDP MJPEG 송신 시작...")

try:
    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            # libcamera가 멈췄을 수 있음
            time.sleep(0.01)
            continue
        buf.extend(chunk)

        # SOI..EOI로 프레임 컷
        while True:
            si = buf.find(SOI)
            if si < 0:
                # 아직 프레임 시작을 못찾음 → 버퍼 축적
                # 너무 오래 SOI를 못 찾으면 버퍼 비우기
                if len(buf) > 2_000_000:
                    buf.clear()
                break

            ei = buf.find(EOI, si+2)
            if ei < 0:
                # 프레임 끝이 아직 안 옴 → 더 받기
                break

            frame = bytes(buf[si:ei+2])
            del buf[:ei+2]

            # 조각화 + 헤더 붙여 전송
            total = (len(frame) + MTU - 1)//MTU
            # 너무 큰 프레임은 드롭(네트워크 보호)
            if total > 2000:
                continue

            # [frame_id:uint32][seq:uint16][total:uint16] + payload
            import struct
            for seq in range(total):
                part = frame[seq*MTU:(seq+1)*MTU]
                hdr = struct.pack("!IHH", frame_id, seq, total)
                sock.sendto(hdr + part, (UDP_IP, UDP_PORT))
                if SLEEP_PER_PACKET:
                    time.sleep(SLEEP_PER_PACKET)

            frame_id = (frame_id + 1) & 0xFFFFFFFF

except KeyboardInterrupt:
    pass
finally:
    proc.terminate()
    sock.close()