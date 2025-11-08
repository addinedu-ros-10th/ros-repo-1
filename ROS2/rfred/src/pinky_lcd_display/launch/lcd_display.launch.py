# pinky_lcd_display/launch/lcd_display.launch.py
"""
LCD Display Launch File

이 launch 파일은 pinky_lcd_display 노드를 실행합니다.

의존성:
- pinky_lcd_display_interfaces 패키지가 먼저 빌드되어 있어야 합니다.
- 빌드 순서: pinky_lcd_display_interfaces -> pinky_lcd_display

빌드 방법:
  cd ~/ros-repo-1/ROS2/rfred
  colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display
  source install/setup.bash
"""
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pinky_lcd_display',
            executable='lcd_node',
            name='pinky_lcd_node',
            output='screen',
        ),
    ])
