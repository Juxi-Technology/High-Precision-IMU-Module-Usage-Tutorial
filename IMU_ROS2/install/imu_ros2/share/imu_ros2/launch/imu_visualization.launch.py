#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    # 获取当前包的路径
    pkg_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # 创建LaunchDescription对象
    ld = LaunchDescription()
    
    # 添加IMU发布节点
    imu_publisher = Node(
        package='imu_ros2',
        executable='imu_publisher',
        name='imu_publisher',
        parameters=[
            {'imu_type': 'serial'},
            {'serial_port': '/dev/imu-serial'},  # 修改为固定端口
            {'publish_rate': 100.0}
        ],
        output='screen'
    )
    
    # 添加rviz2节点
    rviz2 = ExecuteProcess(
        cmd=['rviz2', '-d', os.path.join(pkg_dir, 'rviz', 'imu_config.rviz')],
        output='screen'
    )
    
    # 将节点添加到LaunchDescription
    ld.add_action(imu_publisher)
    ld.add_action(rviz2)
    
    return ld