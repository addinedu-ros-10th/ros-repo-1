#!/bin/bash
# ROS2 서비스를 통한 감정 표현 테스트 스크립트

echo "=========================================="
echo "ROS2 감정 표현 전체 테스트"
echo "=========================================="
echo ""

# 지원하는 모든 감정 타입
emotions=("hello" "basic" "angry" "bored" "fun" "happy" "interest" "sad")

echo "📋 지원하는 감정 타입:"
for emotion in "${emotions[@]}"; do
    echo "  - $emotion"
done
echo ""

echo "1. 서비스 목록 확인"
echo "----------------------------------------"
ros2 service list | grep -i emotion
echo ""

echo "2. 감정 표현 테스트 (ROS2 서비스)"
echo "----------------------------------------"
for emotion in "${emotions[@]}"; do
    echo "테스트: $emotion"
    ros2 service call /emotion_controller/set_emotion \
        pinky_interfaces/srv/Emotion \
        "{emotion: '${emotion}'}"
    echo ""
    sleep 2  # 각 감정 표현 사이에 2초 대기
done

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

