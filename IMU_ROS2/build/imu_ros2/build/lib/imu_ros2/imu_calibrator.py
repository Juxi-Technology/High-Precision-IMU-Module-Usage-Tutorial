#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMU ROS2 标定节点
作者: JuxiTech
版本: 1.0.0
描述: 该节点提供IMU和磁力计的标定服务
"""

import rclpy
from rclpy.node import Node
import sys
import os
import time

# 获取项目根目录
project_root = os.getcwd()
# 构建IMU_Library路径
imu_library_path = os.path.join(project_root, 'IMU_Library')
# 添加到Python路径
sys.path.append(imu_library_path)

# 导入IMU库中的I2C和Serial通信类
from IMU_Library.IMU_I2C_Library import IMU_I2C
from IMU_Library.IMU_Serial_Library import IMU_Serial

# 导入自定义服务消息
from imu_ros2.srv import CalibrateIMU, CalibrateMagnetometer, ResetCalibration


class IMUCalibrator(Node):
    """IMU标定节点类, 继承自ROS2 Node类"""
    
    def __init__(self):
        """构造函数，初始化标定节点"""
        # 调用父类Node的构造函数，节点名称为'imu_calibrator'
        super().__init__('imu_calibrator')
        
        # 声明节点参数，设置默认值
        self.declare_parameter('imu_type', 'serial')  # IMU接口类型：'i2c'或'serial'，默认'serial'
        self.declare_parameter('i2c_port', 7)         # I2C端口号
        self.declare_parameter('serial_port', '/dev/ttyUSB0')  # 串口设备路径
        self.declare_parameter('serial_baudrate', 115200)      # 串口波特率
        self.declare_parameter('debug_mode', False)    # 是否启用调试模式，默认关闭
        
        # 获取参数值
        self.imu_type = self.get_parameter('imu_type').value
        self.debug_mode = self.get_parameter('debug_mode').value
        
        # 根据IMU接口类型初始化传感器
        self._initialize_imu()
        
        # 创建服务服务器
        self.calibrate_imu_service = self.create_service(
            CalibrateIMU, '/imu/calibrate_imu', self.calibrate_imu_callback)
        
        self.calibrate_mag_service = self.create_service(
            CalibrateMagnetometer, '/imu/calibrate_magnetometer', self.calibrate_magnetometer_callback)
        
        self.reset_calibration_service = self.create_service(
            ResetCalibration, '/imu/reset_calibration', self.reset_calibration_callback)
        
        # 记录节点启动信息
        self.get_logger().info(f'IMU标定节点已启动, 使用{self.imu_type}接口')
        self.get_logger().info('标定服务已注册：')
        self.get_logger().info('  - /imu/calibrate_imu')
        self.get_logger().info('  - /imu/calibrate_magnetometer')
        self.get_logger().info('  - /imu/reset_calibration')
        
    def _initialize_imu(self):
        """初始化IMU传感器"""
        if self.imu_type == 'i2c':
            # 获取I2C端口参数
            i2c_port = self.get_parameter('i2c_port').value
            try:
                # 初始化I2C接口的IMU
                self.imu = IMU_I2C(port=i2c_port, debug=self.debug_mode)
                self.get_logger().info(f'I2C IMU初始化成功，端口: {i2c_port}')
            except Exception as e:
                self.get_logger().error(f'I2C IMU初始化失败: {str(e)}')
                sys.exit(1)
        elif self.imu_type == 'serial':
            # 获取串口参数
            serial_port = self.get_parameter('serial_port').value
            serial_baudrate = self.get_parameter('serial_baudrate').value
            
            try:
                # 初始化串口接口的IMU
                self.imu = IMU_Serial(port=serial_port, debug=self.debug_mode)
                self.get_logger().info(f'串口IMU初始化成功，端口: {serial_port}, 波特率: {serial_baudrate}')
                
                # 启动数据接收线程
                self.imu.start_data_reception()
                self.get_logger().info('串口数据接收线程已启动')
                
                # 获取固件版本
                version = self.imu.get_firmware_version()
                if version:
                    self.get_logger().info(f'IMU固件版本: {version}')
                else:
                    self.get_logger().warning('无法获取IMU固件版本')
                    
            except Exception as e:
                self.get_logger().error(f'串口IMU初始化失败: {str(e)}')
                sys.exit(1)
        else:
            # 如果IMU类型无效，记录错误并退出程序
            self.get_logger().error('无效的IMU类型参数。请使用 "i2c" 或 "serial"')
            sys.exit(1)
    
    def calibrate_imu_callback(self, request, response):
        """IMU标定服务回调函数"""
        try:
            self.get_logger().info('开始IMU标定...')
            self.get_logger().info('请保持IMU静止不动！')
            
            # 执行IMU标定
            self.imu.calibrate_imu()
            
            response.success = True
            response.message = 'IMU标定成功完成'
            self.get_logger().info(response.message)
        except Exception as e:
            response.success = False
            response.message = f'IMU标定失败: {str(e)}'
            self.get_logger().error(response.message)
        return response
    
    def calibrate_magnetometer_callback(self, request, response):
        """磁力计标定服务回调函数"""
        try:
            self.get_logger().info('开始磁力计标定...')
            self.get_logger().info('请将IMU绕三个轴旋转360度，确保磁力计采集完整磁场信息！')
            
            # 执行磁力计标定
            self.imu.calibrate_magnetometer()
            
            response.success = True
            response.message = '磁力计标定成功完成'
            self.get_logger().info(response.message)
        except Exception as e:
            response.success = False
            response.message = f'磁力计标定失败: {str(e)}'
            self.get_logger().error(response.message)
        return response
    
    def reset_calibration_callback(self, request, response):
        """重置标定数据服务回调函数"""
        try:
            self.get_logger().info('开始重置标定数据...')
            
            # 执行重置标定数据
            self.imu.reset_calibration_data()
            
            response.success = True
            response.message = '标定数据已成功重置'
            self.get_logger().info(response.message)
        except Exception as e:
            response.success = False
            response.message = f'重置标定数据失败: {str(e)}'
            self.get_logger().error(response.message)
        return response


def main(args=None):
    """主函数，节点的入口点"""
    
    # 初始化ROS2通信
    rclpy.init(args=args)
    
    # 创建IMUCalibrator节点实例
    imu_calibrator = IMUCalibrator()
    
    try:
        # 运行节点，处理回调函数
        rclpy.spin(imu_calibrator)
    except KeyboardInterrupt:
        # 捕获键盘中断信号，记录节点停止信息
        imu_calibrator.get_logger().info('IMU标定节点已停止')
    except Exception as e:
        # 捕获其他异常
        imu_calibrator.get_logger().error(f'节点运行时发生未预期错误: {str(e)}')
    finally:
        # 销毁节点，释放资源
        imu_calibrator.destroy_node()
        # 关闭ROS2通信
        rclpy.shutdown()


if __name__ == '__main__':
    # 如果直接运行该脚本，调用main函数
    main()