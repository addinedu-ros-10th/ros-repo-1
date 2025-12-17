from setuptools import find_packages, setup

import os, glob

package_name = 'drive'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/params', glob.glob(os.path.join('params', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='psh',
    maintainer_email='bshyun1199@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "straight_rotate=drive.straight_rotate:main",
            "coordinate_finder=drive.coordinate_finder:main"
        ],
    },
)
