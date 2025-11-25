# Emotion Display 빠른 시작 가이드

## 실행 순서 (중요!)

Emotion display를 사용하려면 **반드시 다음 순서로 실행**해야 합니다.

### 1단계: LCD Display 노드 실행 (터미널 1)

```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**확인 사항**:
- 로그에 "pinky_lcd_node started with service/action support" 메시지 확인
- 서비스가 등록될 때까지 2-3초 대기

### 2단계: 서비스 확인 (선택사항, 터미널 2)

```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13

# 서비스 목록 확인
ros2 service list | grep display_image

# 예상 출력:
# /lcd_controller/display_image
```

### 3단계: Emotion 서버 실행 (터미널 3)

```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion emotion_server_rfred
```

**예상 로그**:
```
[INFO] [pinky_emotion]: Waiting for LCD display service...
[INFO] [pinky_emotion]: LCD display service connected.  ← 이 메시지가 나와야 함!
[INFO] [pinky_emotion]: Pre-loading all emotion GIFs into memory...
[INFO] [pinky_emotion]:   - Cached 'hello' (41 frames)
...
[INFO] [pinky_emotion]: Pinky's emotion server is ready!! All GIFs pre-loaded.
```

## 문제 해결

### "LCD display service not available" 경고가 나오는 경우

**원인**: LCD Display 노드가 실행되지 않았거나, 서비스가 아직 등록되지 않았습니다.

**해결 방법**:
1. LCD Display 노드가 실행 중인지 확인
2. `ROS_DOMAIN_ID`가 모든 터미널에서 동일한지 확인 (13)
3. 서비스 목록 확인: `ros2 service list | grep display_image`

### 서비스가 보이지 않는 경우

```bash
# 1. 노드 목록 확인
ros2 node list | grep lcd

# 2. 서비스 목록 확인
ros2 service list | grep lcd_controller

# 3. ROS_DOMAIN_ID 확인
echo $ROS_DOMAIN_ID
```

## 테스트

### 서비스 직접 호출

```bash
# 감정 표현 설정
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "happy"}'
```

### API 서버를 통한 호출

```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'
```

## 중요 사항

1. **실행 순서**: LCD Display 노드 → Emotion 서버
2. **ROS_DOMAIN_ID**: 모든 터미널에서 동일한 값 (13)
3. **서비스 등록**: LCD Display 노드 실행 후 2-3초 대기

## 참고

- LCD Display 노드가 먼저 실행되어야 `lcd_controller/display_image` 서비스가 등록됩니다
- `emotion_server_rfred`는 이 서비스를 사용하여 LCD에 emotion을 표시합니다
- 서비스가 없으면 emotion display가 비활성화됩니다

