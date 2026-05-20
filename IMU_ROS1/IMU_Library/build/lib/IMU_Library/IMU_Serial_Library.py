#!/usr/bin/env python3
# coding: utf-8

"""
IMU 串口通信库
作者: JuxiTech
版本: 1.0.0
描述: 用于通过串口与IMU传感器通信的Python库
"""

import struct
import time
import serial
import threading
import math


class IMU_Serial:
    """IMU传感器串口通信类"""
    
    def __init__(self, port, debug=False):
        """
        初始化IMU串口通信
        
        参数:
            port: 串口号，如"COM3"或"/dev/ttyUSB0"
            debug: 是否启用调试模式，默认False
        """
        # 初始化串口设备
        self._serial_dev = serial.Serial(str(port), 115200)
        self._debug = debug  # 调试模式标志
        
        # 通信协议常量
        self._FRAME_HEADER1 = 0x7E
        self._FRAME_HEADER2 = 0x23
        self._MAX_RX_LENGTH = 40  # 最大接收帧长度
        
        # 功能命令定义
        self._CMD_VERSION = 0x01  # 版本信息
        
        # 数据报告命令
        self._CMD_REPORT_RAW_IMU = 0x04     # 原始IMU数据
        self._CMD_REPORT_QUATERNION = 0x16  # 四元数数据
        self._CMD_REPORT_EULER = 0x26       # 欧拉角数据
        self._CMD_REPORT_BAROMETER = 0x32   # 气压计数据
        
        # 配置命令
        self._CMD_REPORT_RATE = 0x60   # 数据报告频率
        self._CMD_ALGORITHM_TYPE = 0x61  # 融合算法类型
        
        # 校准命令
        self._CMD_CALIB_IMU = 0x70        # IMU校准
        self._CMD_CALIB_MAGNETOMETER = 0x71  # 磁力计校准
        self._CMD_CALIB_BAROMETER = 0x72   # 气压计校准
        self._CMD_CALIB_TEMPERATURE = 0x73  # 温度校准
        
        # 数据请求命令
        self._CMD_REQUEST_DATA = 0x80    # 请求数据
        self._CMD_RETURN_STATE = 0x81    # 返回状态
        
        # 系统命令
        self._CMD_RESET_FLASH = 0xA0     # 重置闪存
        
        # 传感器数据缓存
        self._accel_x = 0.0
        self._accel_y = 0.0
        self._accel_z = 0.0
        self._gyro_x = 0.0
        self._gyro_y = 0.0
        self._gyro_z = 0.0
        self._mag_x = 0.0
        self._mag_y = 0.0
        self._mag_z = 0.0
        
        # 姿态数据缓存
        self._yaw = 0.0
        self._roll = 0.0
        self._pitch = 0.0
        
        # 四元数数据缓存
        self._quat_w = 0.0
        self._quat_x = 0.0
        self._quat_y = 0.0
        self._quat_z = 0.0
        
        # 气压计数据缓存
        self._height = 0.0
        self._temperature = 0.0
        self._pressure = 0.0
        self._pressure_ref = 0.0
        
        # 接收状态变量
        self._rx_function = 0
        self._rx_state = 0
        self._rx_flag = 0
        
        # 固件版本信息
        self._version_major = -1
        self._version_minor = -1
        self._version_patch = -1
        
        # 打印串口状态
        if self._serial_dev.isOpen():
            print(f"IMU串口已打开! 波特率: 115200")
        else:
            print(f"IMU串口打开失败!")
    
    def __del__(self):
        """析构函数，关闭串口"""
        try:
            self._serial_dev.close()
            print(f"IMU串口已关闭!")
        except:
            pass
    
    def _print_debug(self, cmd_data, log="发送"):
        """
        打印调试日志
        
        参数:
            cmd_data: 命令数据
            log: 日志前缀，默认"发送"
        """
        if not self._debug:
            return
        print(f"{log}: [{''.join(f'{x:02X}' for x in cmd_data)}]")
    
    def _send_command(self, cmd_data):
        """
        发送命令数据
        
        参数:
            cmd_data: 要发送的命令数据
        """
        self._serial_dev.write(cmd_data)
    
    def _parse_data_frame(self, frame_type, frame_data):
        """
        解析数据帧
        
        参数:
            frame_type: 数据帧类型
            frame_data: 数据帧内容
        """
        # 解析原始IMU数据
        if frame_type == self._CMD_REPORT_RAW_IMU:
            # 加速度计数据 (单位: g)
            accel_ratio = 16 / 32767.0
            self._accel_x = struct.unpack('h', bytearray(frame_data[0:2]))[0] * accel_ratio
            self._accel_y = struct.unpack('h', bytearray(frame_data[2:4]))[0] * accel_ratio
            self._accel_z = struct.unpack('h', bytearray(frame_data[4:6]))[0] * accel_ratio
            
            # 陀螺仪数据 (单位: rad/s)
            deg_to_rad = math.pi / 180.0
            gyro_ratio = (2000 / 32767.0) * deg_to_rad
            self._gyro_x = struct.unpack('h', bytearray(frame_data[6:8]))[0] * gyro_ratio
            self._gyro_y = struct.unpack('h', bytearray(frame_data[8:10]))[0] * gyro_ratio
            self._gyro_z = struct.unpack('h', bytearray(frame_data[10:12]))[0] * gyro_ratio
            
            # 磁力计数据 (单位: uT)
            mag_ratio = 800.0 / 32767.0
            self._mag_x = struct.unpack('h', bytearray(frame_data[12:14]))[0] * mag_ratio
            self._mag_y = struct.unpack('h', bytearray(frame_data[14:16]))[0] * mag_ratio
            self._mag_z = struct.unpack('h', bytearray(frame_data[16:18]))[0] * mag_ratio
        
        # 解析欧拉角数据
        elif frame_type == self._CMD_REPORT_EULER:
            self._roll = struct.unpack('f', bytearray(frame_data[0:4]))[0]
            self._pitch = struct.unpack('f', bytearray(frame_data[4:8]))[0]
            self._yaw = struct.unpack('f', bytearray(frame_data[8:12]))[0]
        
        # 解析四元数数据
        elif frame_type == self._CMD_REPORT_QUATERNION:
            self._quat_w = struct.unpack('f', bytearray(frame_data[0:4]))[0]
            self._quat_x = struct.unpack('f', bytearray(frame_data[4:8]))[0]
            self._quat_y = struct.unpack('f', bytearray(frame_data[8:12]))[0]
            self._quat_z = struct.unpack('f', bytearray(frame_data[12:16]))[0]
        
        # 解析气压计数据
        elif frame_type == self._CMD_REPORT_BAROMETER:
            self._height = round(struct.unpack('f', bytearray(frame_data[0:4]))[0], 2)
            self._temperature = round(struct.unpack('f', bytearray(frame_data[4:8]))[0], 2)
            self._pressure = round(struct.unpack('f', bytearray(frame_data[8:12]))[0], 5)
            self._pressure_ref = round(struct.unpack('f', bytearray(frame_data[12:16]))[0], 5)
        
        # 解析版本信息
        elif frame_type == self._CMD_VERSION:
            self._version_major = struct.unpack('B', bytearray(frame_data[0:1]))[0]
            self._version_minor = struct.unpack('B', bytearray(frame_data[1:2]))[0]
            self._version_patch = struct.unpack('B', bytearray(frame_data[2:3]))[0]
        
        # 解析返回状态
        elif frame_type == self._CMD_RETURN_STATE:
            self._rx_function = struct.unpack('B', bytearray(frame_data[0:1]))[0]
            self._rx_state = struct.unpack('B', bytearray(frame_data[1:2]))[0]
    
    def _process_received_byte(self, data):
        """
        处理接收到的单个字节数据
        
        参数:
            data: 接收到的字节数据
        """
        if self._rx_flag == 0:
            # 等待帧头1
            if data == self._FRAME_HEADER1:
                self._rx_flag = 1
        elif self._rx_flag == 1:
            # 等待帧头2
            if data == self._FRAME_HEADER2:
                self._rx_flag = 2
            else:
                self._rx_flag = 0  # 帧头错误，重置
        elif self._rx_flag == 2:
            # 接收数据长度
            self._data_length = data
            if self._data_length <= self._MAX_RX_LENGTH:
                self._rx_flag = 3
            else:
                self._data_length = 0
                self._rx_flag = 0  # 数据长度错误，重置
        elif self._rx_flag == 3:
            # 接收功能字
            self._data_function = data
            self._rx_data_buffer = []
            self._rx_byte_count = 4
            self._rx_flag = 4
        elif self._rx_flag == 4:
            # 接收数据内容
            self._rx_data_buffer.append(data)
            self._rx_byte_count += 1
            if self._rx_byte_count >= self._data_length - 1:
                self._rx_flag = 5
        elif self._rx_flag == 5:
            # 接收校验和
            self._rx_flag = 0
            rx_checksum = data
            
            # 计算校验和
            checksum = self._FRAME_HEADER1 + self._FRAME_HEADER2 + self._data_length + self._data_function
            for byte in self._rx_data_buffer:
                checksum += byte
            checksum %= 256
            
            # 校验和验证
            if rx_checksum == checksum:
                self._parse_data_frame(self._data_function, self._rx_data_buffer)
            else:
                if self._debug:
                    print(f"校验和错误: 收到{rx_checksum}, 计算{checksum}")
                    print(f"数据: {self._data_length}, {self._data_function}, {self._rx_data_buffer}")
    
    def _data_receive_thread(self):
        """数据接收线程函数"""
        # 清空串口缓冲区
        self._serial_dev.flushInput()
        
        while True:
            # 检查串口缓冲区数据量
            data_count = self._serial_dev.inWaiting()
            if data_count <= 0:
                time.sleep(0.001)
                continue
            
            # 读取所有可用数据
            data_array = self._serial_dev.read_all()
            for data in data_array:
                self._process_received_byte(data)
    
    def _construct_request_command(self, function, param=0):
        """
        构建请求命令
        
        参数:
            function: 请求的功能命令
            param: 请求参数，默认0
            
        返回:
            完整的命令数据
        """
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_REQUEST_DATA, function & 0xFF, param & 0xFF]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        return cmd
    
    def start_data_reception(self):
        """启动数据接收线程"""
        try:
            thread_name = "IMU_Serial_Receive_Thread"
            receive_thread = threading.Thread(target=self._data_receive_thread, name=thread_name)
            receive_thread.daemon = True  # 设置为守护线程
            receive_thread.start()
            print("-----------------数据接收线程已启动-----------------")
            time.sleep(0.05)  # 等待线程初始化
        except Exception as e:
            print(f"---启动数据接收线程失败: {e}---")
    
    def clear_sensor_data(self):
        """清除所有传感器数据缓存"""
        self._accel_x = 0.0
        self._accel_y = 0.0
        self._accel_z = 0.0
        self._gyro_x = 0.0
        self._gyro_y = 0.0
        self._gyro_z = 0.0
        self._mag_x = 0.0
        self._mag_y = 0.0
        self._mag_z = 0.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._quat_w = 0.0
        self._quat_x = 0.0
        self._quat_y = 0.0
        self._quat_z = 0.0
        self._height = 0.0
        self._temperature = 0.0
        self._pressure = 0.0
        self._pressure_ref = 0.0
    
    def set_report_rate(self, rate):
        """
        设置数据报告频率
        
        参数:
            rate: 报告频率，范围10-100Hz
        """
        # 限制频率范围
        if rate < 10:
            rate = 10
        if rate > 100:
            rate = 100
        
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_REPORT_RATE, int(rate), 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "report rate")
        time.sleep(1)  # 等待设置生效
    
    def set_fusion_algorithm(self, algo_type):
        """
        设置融合算法类型
        
        参数:
            algo_type: 算法类型，6表示六轴算法，9表示九轴算法
        """
        if algo_type != 6 and algo_type != 9:
            return  # 无效的算法类型
        
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_ALGORITHM_TYPE, int(algo_type), 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "algo type")
        time.sleep(1)  # 等待设置生效
    
    def _wait_for_calibration(self, func, name, timeout_ms=None):
        """
        等待校准完成
        
        参数:
            func: 校准功能命令
            name: 校准名称
            timeout_ms: 超时时间（毫秒），默认无超时
            
        返回:
            校准状态或None（超时）
        """
        count = 0
        while True:
            if self._rx_function == func:
                if self._debug:
                    print(f"接收 {name} 状态: {self._rx_state}")
                return self._rx_state
            time.sleep(0.001)
            if timeout_ms is not None:
                count += 1
                if count > timeout_ms:
                    if self._debug:
                        print(f"{name} 超时")
                    return None
    
    def calibrate_imu(self):
        """校准IMU（陀螺仪和加速度计）"""
        self._rx_function = 0
        self._rx_state = 0
        
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_CALIB_IMU, 0x01, 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "cali imu")
        
        # 等待校准完成
        self._wait_for_calibration(self._CMD_CALIB_IMU, "cali imu", 7000)
    
    def calibrate_magnetometer(self):
        """校准磁力计"""
        self._rx_function = 0
        self._rx_state = 0
        
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_CALIB_MAGNETOMETER, 0x01, 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "cali mag")
        
        # 等待校准完成
        self._wait_for_calibration(self._CMD_CALIB_MAGNETOMETER, "cali mag")
    
    def calibrate_temperature(self, current_temperature):
        """
        校准温度传感器
        
        参数:
            current_temperature: 当前环境温度
        """
        self._rx_function = 0
        self._rx_state = 0
        
        # 检查温度范围
        if current_temperature > 50 or current_temperature < -50:
            return
        
        # 转换温度数据格式
        temp_value = bytearray(struct.pack('h', int(current_temperature * 100)))
        
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_CALIB_TEMPERATURE, temp_value[0], temp_value[1], 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "cali temp")
        
        # 等待校准完成
        self._wait_for_calibration(self._CMD_CALIB_TEMPERATURE, "cali temp", 2000)
    
    def get_accelerometer_data(self):
        """
        获取加速度计三轴数据
        
        返回:
            加速度计数据列表 [ax, ay, az]，单位：g
        """
        ax, ay, az = self._accel_x, self._accel_y, self._accel_z
        return [ax, ay, az]
    
    def get_gyroscope_data(self):
        """
        获取陀螺仪三轴数据
        
        返回:
            陀螺仪数据列表 [gx, gy, gz]，单位：rad/s
        """
        gx, gy, gz = self._gyro_x, self._gyro_y, self._gyro_z
        return [gx, gy, gz]
    
    def get_magnetometer_data(self):
        """
        获取磁力计三轴数据
        
        返回:
            磁力计数据列表 [mx, my, mz]，单位：uT
        """
        mx, my, mz = self._mag_x, self._mag_y, self._mag_z
        return [mx, my, mz]
    
    def get_attitude_data(self, to_angle=True):
        """
        获取IMU姿态角
        
        参数:
            to_angle: 是否返回角度，True返回角度，False返回弧度，默认True
            
        返回:
            姿态角列表 [roll, pitch, yaw]，单位：度或弧度
        """
        if to_angle:
            rad_to_deg = 57.2957795  # 弧度转角度系数 (180/π)
            roll = self._roll * rad_to_deg
            pitch = self._pitch * rad_to_deg
            yaw = self._yaw * rad_to_deg
        else:
            roll, pitch, yaw = self._roll, self._pitch, self._yaw
        
        return [roll, pitch, yaw]
    
    def get_quaternion_data(self):
        """
        获取IMU四元数数据
        
        返回:
            四元数列表 [w, x, y, z]
        """
        return [self._quat_w, self._quat_x, self._quat_y, self._quat_z]
    
    def get_barometer_data(self):
        """
        获取气压计数据
        
        返回:
            气压计数据列表 [height, temperature, pressure, pressure_ref]
            单位: 高度(m), 温度(℃), 气压(bar), 参考气压(bar)
        """
        return [self._height, self._temperature, self._pressure, self._pressure_ref]
    
    def get_firmware_version(self):
        """
        获取IMU固件版本号
        
        返回:
            固件版本字符串，格式: VX.Y.Z
        """
        self._version_major = -1
        self._version_minor = -1
        self._version_patch = -1
        
        # 构建请求命令
        cmd = self._construct_request_command(self._CMD_VERSION)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "request")
        
        # 等待版本信息返回
        for _ in range(20):
            if self._version_major != -1:
                time.sleep(0.001)
                version = f"V{self._version_major}.{self._version_minor}.{self._version_patch}"
                if self._debug:
                    print(f"固件版本: {version}")
                return version
            time.sleep(0.01)
        
        return None
    
    def reset_calibration_data(self):
        """
        重置所有校准数据
        注意: 此操作会清空所有已保存的校准值
        """
        # 构建命令
        cmd = [self._FRAME_HEADER1, self._FRAME_HEADER2, 0x00, 
               self._CMD_RESET_FLASH, 0x01, 0x5F]
        cmd[2] = len(cmd) + 1  # 更新数据长度
        
        # 计算校验和
        checksum = sum(cmd) & 0xFF
        cmd.append(checksum)
        
        # 发送命令
        self._send_command(cmd)
        self._print_debug(cmd, "reset user data")
        time.sleep(1)  # 等待重置完成


if __name__ == '__main__':
    """示例代码"""
    import platform
    
    # 获取操作系统类型
    system = platform.system()
    print(f"当前系统: {system}")
    
    imu_serial = None
    
    # 根据操作系统选择串口
    if system == 'Windows':
        # Windows系统自动查找可用串口
        com_index = 1
        while True:
            com_index += 1
            try:
                port = f'COM{com_index}'
                print(f"尝试打开串口: {port}")
                imu_serial = IMU_Serial(port, debug=True)
                break
            except Exception as e:
                if com_index > 256:
                    print("-----------------------未找到可用串口--------------------------")
                    exit()
                continue
        print(f"--------------------成功打开串口: {port}---------------------")
    else:
        # Linux系统尝试常用串口
        common_ports = ["/dev/myserial", "/dev/ttyUSB0", "/dev/ttyUSB1", 
                       "/dev/ttyUSB2", "/dev/ttyTHS1", "/dev/ttyAMA0"]
        for port in common_ports:
            try:
                imu_serial = IMU_Serial(port, debug=True)
                print(f"成功打开串口: {port}")
                break
            except Exception as e:
                pass
    
    # 检查串口是否成功打开
    if imu_serial is None:
        print("无法打开任何串口")
        exit()
    
    # 启动数据接收线程
    imu_serial.start_data_reception()
    
    # 获取固件版本
    version = imu_serial.get_firmware_version()
    print(f"固件版本: {version}")
    
    # 以下校准功能可根据需要启用
    # time.sleep(1)
    # imu_serial.calibrate_imu()
    # imu_serial.calibrate_magnetometer()
    # imu_serial.calibrate_temperature(27.1)
    # imu_serial.set_report_rate(25)
    # imu_serial.set_fusion_algorithm(9)
    # imu_serial.reset_calibration_data()
    
    time.sleep(1)
    
    try:
        while True:
            # 读取各类传感器数据
            accel = imu_serial.get_accelerometer_data()
            gyro = imu_serial.get_gyroscope_data()
            mag = imu_serial.get_magnetometer_data()
            attitude = imu_serial.get_attitude_data()
            quat = imu_serial.get_quaternion_data()
            baro = imu_serial.get_barometer_data()
            
            # 打印数据
            print(f"加速度计: {accel}")
            print(f"陀螺仪: {gyro}")
            print(f"磁力计: {mag}")
            print(f"姿态角: {attitude}")
            print(f"四元数: {quat}")
            print(f"气压计: {baro}")
            print("")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n程序已停止")