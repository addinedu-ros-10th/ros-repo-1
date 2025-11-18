from setuptools import find_packages, setup

package_name = 'pinky_state_machine'

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
    maintainer='guehojung',
    maintainer_email='emotionalmachine88@gmail.com',
    description='State machine based control package for Pinky robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'move_pinky_state_machine = pinky_state_machine.move_pinky_state_machine:main',
            'qmonitor_pinky_state_machine = pinky_state_machine.qmonitor_pinky_state_machine:main',
        ],
    },
)

