from setuptools import find_packages, setup

package_name = 'pinky_emotion_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pinky',
    maintainer_email='pinky@todo.todo',
    description='Controller package for pinky_emotion - provides service-based control interface',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'emotion_controller_server = pinky_emotion_controller.emotion_controller_server:main',
        ],
    },
)

