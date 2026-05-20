#!/usr/bin/env python3
# coding: utf-8

"""
IMU_Library 安装配置文件
作者: JuxiTech
版本: 1.0.0
"""

from setuptools import find_packages, setup

setup(
    name='IMU_Library',
    version='1.0.0',
    author='JuxiTech',
    packages=find_packages(),
    description='IMU传感器通信Python库, 支持串口和I2C通信',
    install_requires=[
        'pyserial',
        'smbus2',
        'PyQt5',
        'PyOpenGL'
    ]
)