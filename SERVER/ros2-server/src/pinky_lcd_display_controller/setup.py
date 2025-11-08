from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pinky_lcd_display_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 한글 폰트 파일 설치
        (os.path.join('share', package_name, 'fonts', 'maruburi', 'TTF'),
            glob('fonts/maruburi/TTF/*.ttf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pinky',
    maintainer_email='pinky@todo.todo',
    description='Controller package for pinky_lcd_display',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'lcd_controller_server = pinky_lcd_display_controller.lcd_controller_server:main',
        ],
    },
)

