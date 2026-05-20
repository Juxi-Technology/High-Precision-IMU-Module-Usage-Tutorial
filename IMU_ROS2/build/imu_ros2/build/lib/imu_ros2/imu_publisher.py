#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMU ROS2 发布器节点
作者: JuxiTech
版本: 1.0.0
描述: 该节点从IMU传感器读取数据并发布到ROS2话题, 支持多种通信接口
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, MagneticField
from std_msgs.msg import Float32MultiArray
import sys
import os
import time
import math  # 添加数学库用于数据转换

# 获取项目根目录（当前工作目录）
project_root = os.getcwd()
# 构建IMU_Library路径
imu_library_path = os.path.join(project_root, 'IMU_Library')
# 添加到Python路径
sys.path.append(imu_library_path)

# 导入不同的IMU库
try:
    from IMU_Library.IMU_I2C_Library import IMU_I2C
    from IMU_Library.IMU_Serial_Library import IMU_Serial
except ImportError as e:
    print(f"无法导入IMU_Library: {str(e)}")


class IMUPublisher(Node):
    """IMU数据发布器类，继承自ROS2 Node类，支持多种通信接口"""
    
    def __init__(self):
        """构造函数，初始化节点和IMU传感器"""
        # 调用父类Node的构造函数，节点名称为'imu_publisher'
        super().__init__('imu_publisher')
        
        # 创建IMU数据发布器，话题名称为'imu/data'，队列大小为10
        self.imu_publisher_ = self.create_publisher(Imu, 'imu/data', 10)
        
        # 创建磁力计数据发布器，话题名称为'imu/mag'，队列大小为10
        self.mag_publisher_ = self.create_publisher(MagneticField, 'imu/mag', 10)
        
        # 创建气压计数据发布器，话题名称为'baro'，队列大小为10
        self.baro_publisher_ = self.create_publisher(Float32MultiArray, 'baro', 10)
        
        # 创建欧拉角数据发布器，话题名称为'euler'，队列大小为10
        self.euler_publisher_ = self.create_publisher(Float32MultiArray, 'euler', 10)
        
        # 声明节点参数，设置默认值
        self.declare_parameter('imu_type', 'serial')  # IMU接口类型：'i2c'、'serial'或'device'，默认'serial'
        self.declare_parameter('i2c_port', 7)         # I2C端口号
        self.declare_parameter('serial_port', '/dev/ttyUSB0')  # 串口设备路径
        self.declare_parameter('serial_baudrate', 115200)      # 串口波特率
        self.declare_parameter('publish_rate', 100.0)  # 数据发布频率（Hz）
        self.declare_parameter('debug_mode', False)    # 是否启用调试模式，默认关闭
        self.declare_parameter('enable_auto_calib', False)  # 是否启用自动校准
        self.declare_parameter('fusion_algorithm', 9)  # 融合算法类型：6轴、9轴或10轴
        self.declare_parameter('allow_zero_data', True)  # 是否允许发布全0数据
        
        # 获取参数值
        self.imu_type = self.get_parameter('imu_type').value
        publish_rate = self.get_parameter('publish_rate').value
        self.debug_mode = self.get_parameter('debug_mode').value
        self.allow_zero_data = self.get_parameter('allow_zero_data').value
        
        # 初始化计数器和状态
        self.startup_counter = 0
        self.max_startup_attempts = 30  # 最大启动尝试次数
        self.is_started = False  # 标记节点是否已完成启动
        
        # 根据IMU接口类型初始化传感器
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
        elif self.imu_type in ['serial', 'device']:
            # 获取串口参数
            serial_port = self.get_parameter('serial_port').value
            serial_baudrate = self.get_parameter('serial_baudrate').value
            
            try:
                # 初始化串口接口的IMU
                # 注意：当前IMU_Serial类不支持自定义波特率，默认使用115200
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
                
                # 获取当前融合算法类型
                current_algo = None
                if hasattr(self.imu, 'get_fusion_algorithm'):
                    current_algo = self.imu.get_fusion_algorithm()
                    if current_algo:
                        self.get_logger().info(f'当前融合算法: {current_algo}轴')
                
                # 设置融合算法类型
                fusion_algorithm = self.get_parameter('fusion_algorithm').value
                if fusion_algorithm in [6, 9, 10]:
                    if current_algo != fusion_algorithm:
                        self.imu.set_fusion_algorithm(fusion_algorithm)
                        self.get_logger().info(f'融合算法已设置为{fusion_algorithm}轴')
                    else:
                        self.get_logger().info(f'融合算法保持为{fusion_algorithm}轴')
                elif current_algo:
                    # 如果用户没有指定或指定错误，使用自动识别的算法类型
                    self.get_logger().warning(f'指定的融合算法类型无效，使用自动识别的{current_algo}轴算法')
                
                # 设置数据报告频率
                self.imu.set_report_rate(int(publish_rate))
                self.get_logger().info(f'数据报告频率已设置为{publish_rate} Hz')
                
                # 启用自动校准
                if self.get_parameter('enable_auto_calib').value:
                    self.get_logger().info('开始自动校准IMU...')
                    self.imu.calibrate_imu()
                    self.get_logger().info('IMU自动校准完成')
                    
                    self.get_logger().info('开始自动校准磁力计...')
                    self.imu.calibrate_magnetometer()
                    self.get_logger().info('磁力计自动校准完成')
                    
            except Exception as e:
                self.get_logger().error(f'串口IMU初始化失败: {str(e)}')
                sys.exit(1)
        else:
            # 如果IMU类型无效，记录错误并退出程序
            self.get_logger().error('无效的IMU类型参数。请使用 "i2c"、"serial" 或 "device"')
            sys.exit(1)
        
        # 创建定时器，根据发布频率定期调用timer_callback函数
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)
        
        # 记录节点启动信息
        self.get_logger().info(f'IMU发布器节点已启动，使用{self.imu_type}接口，发布频率为{publish_rate} Hz')
        
    def timer_callback(self):
        """定时器回调函数，定期读取IMU数据并发布到ROS2话题"""
        
        # 创建IMU消息对象
        imu_msg = Imu()
        
        # 设置消息头信息
        imu_msg.header.stamp = self.get_clock().now().to_msg()  # 时间戳
        imu_msg.header.frame_id = 'imu_link'  # 坐标系ID
        
        try:
            # 使用统一的IMU接口
            accel = self.imu.get_accelerometer_data()
            gyro = self.imu.get_gyroscope_data()
            quat = self.imu.get_quaternion_data()
            mag = self.imu.get_magnetometer_data()
            baro_data = None
            euler = None
            
            if self.debug_mode:
                self.get_logger().debug(f'原始加速度计数据: {accel}')
                self.get_logger().debug(f'原始陀螺仪数据: {gyro}')
                self.get_logger().debug(f'原始四元数数据: {quat}')
                self.get_logger().debug(f'原始磁力计数据: {mag}')
                if baro_data:
                    self.get_logger().debug(f'原始气压计数据: {baro_data}')
                if euler:
                    self.get_logger().debug(f'原始欧拉角数据: {euler}')
            
            # 检查数据有效性
            accel_valid = self._is_valid_data(accel, "加速度计")
            gyro_valid = self._is_valid_data(gyro, "陀螺仪")
            quat_valid = self._is_valid_data(quat, "四元数")
            mag_valid = self._is_valid_data(mag, "磁力计")
            
            # 启动阶段处理
            if not self.is_started:
                self.startup_counter += 1
                
                # 如果允许发布全0数据，直接标记为已启动
                if self.allow_zero_data:
                    self.is_started = True
                    self.get_logger().info('节点启动完成（允许全0数据）')
                elif accel_valid and gyro_valid and quat_valid:
                    # 如果数据有效，标记为已启动
                    self.is_started = True
                    self.get_logger().info('节点启动完成（已获取有效数据）')
                elif self.startup_counter >= self.max_startup_attempts:
                    # 如果达到最大尝试次数，即使数据无效也标记为已启动
                    self.is_started = True
                    self.get_logger().warning(f'节点启动完成（已达到最大尝试次数 {self.max_startup_attempts}）')
                else:
                    # 启动阶段，等待有效数据
                    if self.startup_counter % 10 == 0:  # 每10次尝试输出一次日志
                        self.get_logger().info(f'启动阶段 ({self.startup_counter}/{self.max_startup_attempts}) - 等待有效数据...')
                    return
            
            # 发布IMU数据
            if accel_valid and gyro_valid and quat_valid:
                # 将加速度数据从g转换为m/s²（9.80665 m/s² = 1g）
                gravity = 9.80665
                imu_msg.linear_acceleration.x = accel[0] * gravity
                imu_msg.linear_acceleration.y = accel[1] * gravity
                imu_msg.linear_acceleration.z = accel[2] * gravity
                
                # 设置协方差矩阵（示例值，实际应根据传感器规格设置）
                imu_msg.linear_acceleration_covariance = [0.01, 0.0, 0.0,
                                                         0.0, 0.01, 0.0,
                                                         0.0, 0.0, 0.01]
                
                # 将陀螺仪数据赋值到IMU消息中
                imu_msg.angular_velocity.x = gyro[0]
                imu_msg.angular_velocity.y = gyro[1]
                imu_msg.angular_velocity.z = gyro[2]
                
                # 设置协方差矩阵（示例值，实际应根据传感器规格设置）
                imu_msg.angular_velocity_covariance = [0.001, 0.0, 0.0,
                                                      0.0, 0.001, 0.0,
                                                      0.0, 0.0, 0.001]
                
                # 将四元数数据赋值到IMU消息中
                imu_msg.orientation.w = quat[0]
                imu_msg.orientation.x = quat[1]
                imu_msg.orientation.y = quat[2]
                imu_msg.orientation.z = quat[3]
                
                # 设置协方差矩阵（示例值，实际应根据传感器规格设置）
                imu_msg.orientation_covariance = [0.01, 0.0, 0.0,
                                                 0.0, 0.01, 0.0,
                                                 0.0, 0.0, 0.01]
                
                # 发布IMU消息到话题
                self.imu_publisher_.publish(imu_msg)
                if self.debug_mode:
                    self.get_logger().info('IMU数据发布成功')
            
            # 读取并发布磁力计数据
            try:
                if mag_valid:
                    # 创建磁力计消息对象
                    mag_msg = MagneticField()
                    
                    # 设置消息头信息，与IMU消息保持一致
                    mag_msg.header.stamp = imu_msg.header.stamp
                    mag_msg.header.frame_id = 'imu_link'
                    
                    # 统一磁力计数据处理方式
                    mag_msg.magnetic_field.x = mag[0]
                    mag_msg.magnetic_field.y = -mag[1]
                    mag_msg.magnetic_field.z = mag[2]
                    
                    # 设置协方差矩阵（示例值，实际应根据传感器规格设置）
                    mag_msg.magnetic_field_covariance = [0.1, 0.0, 0.0,
                                                        0.0, 0.1, 0.0,
                                                        0.0, 0.0, 0.1]
                    
                    # 发布磁力计消息到话题
                    self.mag_publisher_.publish(mag_msg)
                    if self.debug_mode:
                        self.get_logger().info('磁力计数据发布成功')
                        
            except Exception as e:
                # 磁力计数据读取失败，只记录警告
                self.get_logger().warning(f'读取磁力计数据时发生错误: {str(e)}')
            
            # 发布气压计数据
            try:
                # 气压计功能可根据实际需求扩展
                pass
            except Exception as e:
                self.get_logger().warning(f'发布气压计数据时发生错误: {str(e)}')
            
            # 发布欧拉角数据
            try:
                # 欧拉角功能可根据实际需求扩展
                pass
            except Exception as e:
                self.get_logger().warning(f'发布欧拉角数据时发生错误: {str(e)}')
                
        except Exception as e:
            # 捕获并记录读取IMU数据时的错误
            self.get_logger().error(f'读取IMU数据时发生错误: {str(e)}')
            
    def _is_valid_data(self, data_list, data_type="数据"):
        """
        检查数据是否有效
        
        参数:
            data_list: 要检查的数据列表
            data_type: 数据类型名称，用于日志输出
            
        返回:
            bool: 数据是否有效
        """
        # 检查数据列表是否为空
        if not data_list:
            self.get_logger().warning(f'{data_type}数据列表为空')
            return False
            
        # 检查数据是否为None或包含None值
        for value in data_list:
            if value is None:
                self.get_logger().warning(f'{data_type}数据包含None值')
                return False
                
        # 检查数据是否为NaN或无穷大
        for value in data_list:
            if isinstance(value, (int, float)):
                if math.isnan(value) or value == float('inf') or value == float('-inf'):
                    self.get_logger().warning(f'{data_type}数据包含无效数值: {value}')
                    return False
                    
        # 检查数据是否全为0
        if all(value == 0.0 for value in data_list):
            if self.allow_zero_data:
                self.get_logger().debug(f'{data_type}数据全为0，但允许发布')
                return True
            else:
                self.get_logger().warning(f'{data_type}数据全为0')
                return False
            
        return True


def main(args=None):
    """主函数，节点的入口点"""
    
    # 初始化ROS2通信
    rclpy.init(args=args)
    
    # 创建IMUPublisher节点实例
    imu_publisher = IMUPublisher()
    
    try:
        # 运行节点，处理回调函数
        rclpy.spin(imu_publisher)
    except KeyboardInterrupt:
        # 捕获键盘中断信号，记录节点停止信息
        imu_publisher.get_logger().info('IMU发布器节点已停止')
    except Exception as e:
        # 捕获其他异常
        imu_publisher.get_logger().error(f'节点运行时发生未预期错误: {str(e)}')
    finally:
        # 销毁节点，释放资源
        imu_publisher.destroy_node()
        # 关闭ROS2通信
        rclpy.shutdown()


if __name__ == '__main__':
    # 如果直接运行该脚本，调用main函数
    main()