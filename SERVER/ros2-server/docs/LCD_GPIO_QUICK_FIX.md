# LCD GPIO 오류 빠른 해결 가이드

## 문제 증상

```
lgpio.error: 'GPIO not allocated'
```

**발생 위치**: `pinky_lcd` 패키지의 `LCD()` 초기화 중

## 즉시 해결 방법 (우선순위)

### 1단계: 기존 프로세스 종료 (가장 빠른 해결)

```bash
# 실행 중인 LCD 관련 프로세스 확인
ps aux | grep -E "lcd_node|pinky_lcd|pinky_emotion"

# 모든 LCD 관련 프로세스 종료
pkill -f lcd_node
pkill -f pinky_lcd
pkill -f pinky_emotion

# 프로세스가 종료되었는지 확인
ps aux | grep -E "lcd_node|pinky_lcd|pinky_emotion"

# 2-3초 대기 후 다시 실행
sleep 2
ros2 launch pinky_lcd_display lcd_display.launch.py
```

### 2단계: GPIO 상태 확인 및 해제

```bash
# GPIO 정보 확인
gpioinfo

# GPIO 핀 해제 (필요시)
# GPIO 27번 (RST_PIN) 해제
sudo gpioset -m time -s 0 0 27=0

# GPIO 25번 (DC_PIN) 해제
sudo gpioset -m time -s 0 0 25=0

# GPIO 18번 (BL_PIN) 해제
sudo gpioset -m time -s 0 0 18=0
```

### 3단계: gpiod 서비스 재시작

```bash
# gpiod 서비스 재시작
sudo systemctl restart gpiod

# 서비스 상태 확인
sudo systemctl status gpiod
```

### 4단계: 권한 확인

```bash
# 현재 사용자가 gpio 그룹에 속하는지 확인
groups | grep gpio

# gpio 그룹에 사용자 추가 (필요시)
sudo usermod -a -G gpio $USER

# 그룹 변경 적용 (재로그인 또는)
newgrp gpio
```

## 사용 중인 GPIO 핀

`pinky_lcd` 패키지에서 사용하는 GPIO 핀:

- **RST_PIN = 27**: 리셋 핀
- **DC_PIN = 25**: 데이터/커맨드 핀
- **BL_PIN = 18**: 백라이트 핀 (PWM)

## 원인 분석

### 가장 일반적인 원인

1. **이전 프로세스가 GPIO 핀을 점유**
   - 이전에 실행된 `lcd_node` 또는 `pinky_emotion` 노드가 종료되지 않음
   - 프로세스가 비정상 종료되어 GPIO 핀이 해제되지 않음

2. **여러 인스턴스 동시 실행**
   - `lcd_node`와 `pinky_emotion`이 동시에 실행되어 같은 GPIO 핀 사용 시도

### 해결 확인

다음 명령으로 문제가 해결되었는지 확인:

```bash
# 1. 프로세스 확인 (아무것도 나오지 않아야 함)
ps aux | grep -E "lcd_node|pinky_lcd|pinky_emotion"

# 2. GPIO 상태 확인
gpioinfo | grep -E "27|25|18"

# 3. LCD 노드 실행
ros2 launch pinky_lcd_display lcd_display.launch.py
```

## 예방 방법

### 1. 프로세스 종료 스크립트 생성

```bash
#!/bin/bash
# stop_lcd.sh

echo "Stopping LCD related processes..."
pkill -f lcd_node
pkill -f pinky_lcd
pkill -f pinky_emotion
sleep 2
echo "Done."
```

### 2. Launch 파일에 종료 핸들러 추가

`lcd_display.launch.py`에 종료 시 GPIO 정리 로직 추가 (권장)

### 3. 단일 인스턴스 보장

동시에 여러 LCD 인스턴스가 실행되지 않도록 시스템 레벨에서 제한

## 추가 디버깅

### GPIO 핀 상태 상세 확인

```bash
# 특정 GPIO 핀 정보 확인
gpioinfo 0 27  # chip 0, GPIO 27
gpioinfo 0 25  # chip 0, GPIO 25
gpioinfo 0 18  # chip 0, GPIO 18
```

### 로그 확인

```bash
# 시스템 로그에서 GPIO 관련 오류 확인
dmesg | grep -i gpio
journalctl -u gpiod | tail -20
```

## 참고

- `lgpio`는 Linux GPIO 인터페이스로, Raspberry Pi에서 GPIO를 제어합니다
- GPIO 핀은 한 번에 하나의 프로세스만 사용할 수 있습니다
- 프로세스가 비정상 종료되면 GPIO 핀이 해제되지 않을 수 있습니다
- `gpiod` 서비스는 GPIO 핀을 관리하는 시스템 서비스입니다

