from setuptools import find_packages, setup

package_name = 'pinky_lcd_display'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launch 파일들
        ('share/' + package_name + '/launch', ['launch/lcd_display.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pinky',
    maintainer_email='emotionalmachine88@gmail.com',
    description='ROS2 LCD display node for Pinky robot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # ros2 run pinky_lcd_display lcd_node
            'lcd_node = pinky_lcd_display.lcd_node:main',
            # ros2 run pinky_lcd_display test_pub
            'test_pub = pinky_lcd_display.test_publisher_node:main',
        ],
    },
)
