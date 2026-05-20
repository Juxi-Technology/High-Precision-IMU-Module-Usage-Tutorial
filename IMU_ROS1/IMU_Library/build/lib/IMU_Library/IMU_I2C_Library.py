#!/usr/bin/env python3
# coding: utf-8

"""
IMU I2C通信库
作者: JuxiTech
版本: 1.0.0
描述: 用于通过I2C协议与IMU传感器通信的Python库
"""

import struct
import time
import math
from smbus2 import SMBus


class IMU_I2C:
    """IMU传感器I2C通信类"""
    
    def __init__(self, port=7, debug=False):
        """
        初始化IMU I2C通信
        
        参数:
            port: I2C总线端口号，默认7
            debug: 是否启用调试模式，默认False
        """
        self._port = int(port)
        self._delay_time = 0.001  # 数据读取延迟时间
        self._debug = debug       # 调试模式标志
        self._addr = 0x23         # I2C设备地址
        
        # 功能命令定义
        self.FUNC_VERSION = 0x01        # 版本信息
        self.FUNC_RAW_ACCEL = 0x04      # 原始加速度数据
        self.FUNC_RAW_GYRO = 0x0A       # 原始陀螺仪数据
        self.FUNC_RAW_MAG = 0x10        # 原始磁力计数据
        self.FUNC_QUAT = 0x16           # 四元数数据
        self.FUNC_EULER = 0x26          # 欧拉角数据
        self.FUNC_BARO = 0x32           # 气压计数据
        
        self.FUNC_ALGO_TYPE = 0x61      # 融合算法类型
        
        self.FUNC_CALIB_IMU = 0x70      # IMU校准
        self.FUNC_CALIB_MAG = 0x71      # 磁力计校准
        self.FUNC_CALIB_TEMP = 0x73     # 温度校准
        
        self.FUNC_RESET_FLASH = 0xA0    # 重置闪存数据
    
    def __del__(self):
        """析构函数"""
        pass
        
    def _print_log(self, cmd_data, log="Send"):
        """
        打印调试日志
        
        参数:
            cmd_data: 命令数据
            log: 日志前缀，默认"Send"
        """
        if not self._debug:
            return
        print(f"{log}: [{''.join(f'{x:02X}' for x in cmd_data)}]")
    
    def _send_data(self, reg, cmd_data):
        """
        发送单个字节数据
        
        参数:
            reg: 寄存器地址
            cmd_data: 要发送的数据
        """
        with SMBus(self._port) as bus:
            bus.write_byte_data(self._addr, reg, cmd_data)
    
    def _send_data_array(self, reg, cmd_array):
        """
        发送数据数组
        
        参数:
            reg: 寄存器地址
            cmd_array: 要发送的数据数组
        """
        with SMBus(self._port) as bus:
            bus.write_i2c_block_data(self._addr, reg, cmd_array)
    
    def _read_data(self, reg, num):
        """
        读取数据
        
        参数:
            reg: 寄存器地址
            num: 要读取的字节数
            
        返回:
            读取到的数据数组
        """
        if num > 32:
            num = 32  # I2C单次最多读取32字节
        data = None
        with SMBus(self._port) as bus:
            data = bus.read_i2c_block_data(self._addr, reg, num)
        return data
    
    def set_fusion_algorithm(self, algo):
        """
        设置融合算法类型
        
        参数:
            algo: 算法类型，6表示六轴算法，9表示九轴算法
        """
        if algo != 6 and algo != 9:
            return
        cmd = [self.FUNC_ALGO_TYPE, int(algo)]
        self._send_data(cmd[0], cmd[1])
        self._print_log(cmd, "algo type")
        time.sleep(1)  # 等待算法切换完成
    
    def _wait_calibration(self, func, name, timeout_ms=None):
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
            time.sleep(0.1)
            values = self._read_data(func, 1)
            if values[0]:
                if self._debug:
                    print(f"{name} {values[0]}")
                return values[0]
            if timeout_ms is not None:
                count += 1
                if count > timeout_ms:
                    if self._debug:
                        print(f"{name} timeout")
                    return None
    
    def calibrate_imu(self):
        """校准IMU（陀螺仪和加速度计）"""
        cmd = [self.FUNC_CALIB_IMU, 0x01]
        self._send_data(cmd[0], cmd[1])
        self._print_log(cmd, "cali imu")
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        self._wait_calibration(self.FUNC_CALIB_IMU, "cali imu", 7000)
    
    def calibrate_magnetometer(self):
        """校准磁力计"""
        cmd = [self.FUNC_CALIB_MAG, 0x01]
        self._send_data(cmd[0], cmd[1])
        self._print_log(cmd, "cali mag")
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        self._wait_calibration(self.FUNC_CALIB_MAG, "cali mag")
    
    def calibrate_temperature(self, current_temperature):
        """
        校准温度传感器
        
        参数:
            current_temperature: 当前环境温度
        """
        if current_temperature > 50 or current_temperature < -50:
            return  # 温度超出有效范围
        value = bytearray(struct.pack('h', int(current_temperature * 100)))
        cmd = [self.FUNC_CALIB_TEMP, value[0], value[1]]
        self._send_data_array(cmd[0], cmd[1:])
        self._print_log(cmd, "cali temp")
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        self._wait_calibration(self.FUNC_CALIB_TEMP, "cali temp", 2000)
    
    def reset_calibration_data(self):
        """
        重置用户数据
        注意: 此操作会将所有校准值清零，请谨慎操作
        """
        cmd = [self.FUNC_RESET_FLASH, 0x01]
        self._send_data(cmd[0], cmd[1])
        self._print_log(cmd, "reset user data")
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        time.sleep(1)  # 等待重置完成
    
    def get_accelerometer_data(self):
        """
        获取加速度计三轴数据
        
        返回:
            加速度计数据列表 [ax, ay, az]，单位：g
        """
        values = self._read_data(self.FUNC_RAW_ACCEL, 6)
        # 转换单位为g (重力加速度)
        accel_ratio = 16 / 32767.0
        ax = struct.unpack('h', bytearray(values[0:2]))[0] * accel_ratio
        ay = struct.unpack('h', bytearray(values[2:4]))[0] * accel_ratio
        az = struct.unpack('h', bytearray(values[4:6]))[0] * accel_ratio
        accel_data = [ax, ay, az]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return accel_data
    
    def get_gyroscope_data(self):
        """
        获取陀螺仪三轴数据
        
        返回:
            陀螺仪数据列表 [gx, gy, gz]，单位：rad/s
        """
        values = self._read_data(self.FUNC_RAW_GYRO, 6)
        # 转换单位为rad/s (弧度/秒)
        deg_to_rad = math.pi / 180.0
        gyro_ratio = (2000 / 32767.0) * deg_to_rad
        gx = struct.unpack('h', bytearray(values[0:2]))[0] * gyro_ratio
        gy = struct.unpack('h', bytearray(values[2:4]))[0] * gyro_ratio
        gz = struct.unpack('h', bytearray(values[4:6]))[0] * gyro_ratio
        gyro_data = [gx, gy, gz]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return gyro_data
    
    def get_magnetometer_data(self):
        """
        获取磁力计三轴数据
        
        返回:
            磁力计数据列表 [mx, my, mz]，单位：uT
        """
        values = self._read_data(self.FUNC_RAW_MAG, 6)
        # 转换单位为uT (微特斯拉)
        mag_ratio = 800.0 / 32767.0
        mx = struct.unpack('h', bytearray(values[0:2]))[0] * mag_ratio
        my = struct.unpack('h', bytearray(values[2:4]))[0] * mag_ratio
        mz = struct.unpack('h', bytearray(values[4:6]))[0] * mag_ratio
        mag_data = [mx, my, mz]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return mag_data
    
    def get_quaternion_data(self):
        """
        获取IMU四元数数据
        
        返回:
            四元数列表 [w, x, y, z]
        """
        values = self._read_data(self.FUNC_QUAT, 16)
        q0 = struct.unpack('f', bytearray(values[0:4]))[0]
        q1 = struct.unpack('f', bytearray(values[4:8]))[0]
        q2 = struct.unpack('f', bytearray(values[8:12]))[0]
        q3 = struct.unpack('f', bytearray(values[12:16]))[0]
        quat_data = [q0, q1, q2, q3]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return quat_data
    
    def get_attitude_data(self, to_angle=True):
        """
        获取IMU姿态角
        
        参数:
            to_angle: 是否返回角度，True返回角度，False返回弧度，默认True
            
        返回:
            姿态角列表 [roll, pitch, yaw]，单位：度或弧度
        """
        values = self._read_data(self.FUNC_EULER, 12)
        roll = struct.unpack('f', bytearray(values[0:4]))[0]
        pitch = struct.unpack('f', bytearray(values[4:8]))[0]
        yaw = struct.unpack('f', bytearray(values[8:12]))[0]
        
        if to_angle:
            rad_to_deg = 180.0 / math.pi
            roll *= rad_to_deg
            pitch *= rad_to_deg
            yaw *= rad_to_deg
        
        attitude_data = [roll, pitch, yaw]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return attitude_data
    
    def get_barometer_data(self):
        """
        获取气压计数据
        
        返回:
            气压计数据列表 [height, temperature, pressure, pressure_contrast]
            单位: 高度(m), 温度(℃), 气压(bar), 参考气压(bar)
        """
        values = self._read_data(self.FUNC_BARO, 16)
        height = round(struct.unpack('f', bytearray(values[0:4]))[0], 2)
        temperature = round(struct.unpack('f', bytearray(values[4:8]))[0], 2)
        pressure = round(struct.unpack('f', bytearray(values[8:12]))[0], 5)
        pressure_contrast = round(struct.unpack('f', bytearray(values[12:16]))[0], 5)
        baro_data = [height, temperature, pressure, pressure_contrast]
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return baro_data
    
    def get_firmware_version(self):
        """
        获取IMU固件版本号
        
        返回:
            固件版本字符串，格式: X.Y.Z
        """
        values = self._read_data(self.FUNC_VERSION, 3)
        version = f"{values[0]}.{values[1]}.{values[2]}"
        
        if self._delay_time > 0:
            time.sleep(self._delay_time)
        return version


if __name__ == '__main__':
    # 示例代码
    imu = IMU_I2C(port=7, debug=True)
    
    # 获取固件版本
    version = imu.get_firmware_version()
    print(f"固件版本: {version}")
    
    # 以下校准功能可根据需要启用
    # time.sleep(1)
    # imu.calibrate_imu()
    # imu.calibrate_magnetometer()
    # imu.calibrate_temperature(25.1)
    # imu.set_fusion_algorithm(9)
    # imu.reset_calibration_data()
    
    time.sleep(1)
    
    try:
        while True:
            # 读取各类传感器数据
            accel = imu.get_accelerometer_data()
            gyro = imu.get_gyroscope_data()
            mag = imu.get_magnetometer_data()
            attitude = imu.get_attitude_data()
            quat = imu.get_quaternion_data()
            baro = imu.get_barometer_data()
            
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