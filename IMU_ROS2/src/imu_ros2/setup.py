from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'imu_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'srv'), glob('srv/*.srv')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='JuxiTech',
    maintainer_email='pe@juxitech.com',
    description='IMU ROS2 Publisher with calibration support',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu_publisher = imu_ros2.imu_publisher:main',
            'imu_calibrator = imu_ros2.imu_calibrator:main',
        ],
    },
)