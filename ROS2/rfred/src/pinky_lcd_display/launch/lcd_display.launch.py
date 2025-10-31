# pinky_lcd_display/launch/lcd_display.launch.py
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
