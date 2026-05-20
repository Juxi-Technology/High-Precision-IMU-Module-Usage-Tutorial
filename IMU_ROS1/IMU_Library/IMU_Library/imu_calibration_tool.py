#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMU校准工具
作者: JuxiTech
版本: 1.0.0
支持I2C和串口通信模式
包含IMU整体校准、磁力计校准和温度校准功能
"""

import sys
import argparse
import time
from typing import Optional, Tuple

from IMU_Library.IMU_Serial_Library import IMU_Serial
from IMU_Library.IMU_I2C_Library import IMU_I2C

# 校准后额外等待时间（秒）
POST_CALIBRATION_WAIT = 2.0


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='IMU校准工具')
    parser.add_argument('--mode', '-m', choices=['serial', 'i2c'], required=True,
                        help='通信模式：serial(串口) 或 i2c(I2C)')
    parser.add_argument('--port', '-p', required=True,
                        help='串口端口(如/dev/ttyUSB0)或I2C总线号(如7)')
    parser.add_argument('--calibrate', '-c', choices=['imu', 'mag', 'temp', 'all'], default='all',
                        help='校准类型：imu(整体校准)、mag(磁力计校准)、temp(温度校准)或all(全部校准)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='启用调试模式')
    return parser.parse_args()


def create_imu_device(args) -> Tuple[Optional[object], Optional[str]]:
    """
    创建IMU设备实例并初始化通信
    
    参数:
        args: 命令行参数对象
        
    返回:
        Tuple[IMU设备实例, 错误信息]，如果成功则错误信息为None
    """
    try:
        if args.mode == 'serial':
            print(f"正在初始化串口通信: {args.port}")
            imu = IMU_Serial(port=args.port, debug=args.debug)
            imu.start_data_reception()
            time.sleep(0.1)  # 等待数据接收线程启动
        else:  # i2c模式
            print(f"正在初始化I2C通信: 总线 {args.port}")
            i2c_port = int(args.port)
            imu = IMU_I2C(port=i2c_port, debug=args.debug)
            imu.start_data_reception()
            time.sleep(0.1)
        
        return imu, None
            
    except Exception as e:
        error_msg = f"初始化IMU失败: {str(e)}"
        print(error_msg)
        return None, error_msg


def get_firmware_version(imu: object) -> str:
    """
    获取IMU固件版本
    
    参数:
        imu: IMU设备实例
        
    返回:
        固件版本字符串
    """
    try:
        if hasattr(imu, 'get_firmware_version'):
            version = imu.get_firmware_version()
        elif hasattr(imu, 'get_version'):
            version = imu.get_version()
        else:
            version = None
            
        if version:
            return version
        return "unavailable"
    except Exception:
        return "unavailable"


def format_state(state: Optional[int]) -> str:
    """
    将校准状态转换为可读文本
    
    参数:
        state: 校准状态码
        
    返回:
        可读的状态文本
    """
    if state == 1:
        return "success"
    if state == 0 or state is None:
        return "incomplete"
    return f"code {state}"


def get_calibration_state(imu: object, calibration_type: str) -> Optional[int]:
    """
    获取校准状态，包含备份检查机制
    
    参数:
        imu: IMU设备实例
        calibration_type: 校准类型 ('imu', 'mag', 'temp')
        
    返回:
        校准状态码
    """
    # 根据校准类型获取对应的命令和内部变量名
    state_map = {
        'imu': {
            'cmd_serial': getattr(imu, '_CMD_CALIB_IMU', None),
            'cmd_i2c': getattr(imu, 'FUNC_CALIB_IMU', None),
            'rx_func': '_rx_function',
            'rx_state': '_rx_state'
        },
        'mag': {
            'cmd_serial': getattr(imu, '_CMD_CALIB_MAGNETOMETER', None),
            'cmd_i2c': getattr(imu, 'FUNC_CALIB_MAG', None),
            'rx_func': '_rx_function',
            'rx_state': '_rx_state'
        },
        'temp': {
            'cmd_serial': getattr(imu, '_CMD_CALIB_TEMPERATURE', None),
            'cmd_i2c': getattr(imu, 'FUNC_CALIB_TEMP', None),
            'rx_func': '_rx_function',
            'rx_state': '_rx_state'
        }
    }
    
    if calibration_type not in state_map:
        return None
        
    config = state_map[calibration_type]
    
    # 获取IMU的通信模式（通过检查是否有串口属性）
    is_serial = hasattr(imu, '_serial_dev')
    
    # 根据通信模式选择对应的命令
    if is_serial and config['cmd_serial']:
        expected_func = config['cmd_serial']
    elif not is_serial and config['cmd_i2c']:
        expected_func = config['cmd_i2c']
    else:
        return None
    
    # 直接检查内部状态变量的备份机制
    if hasattr(imu, config['rx_func']) and hasattr(imu, config['rx_state']):
        rx_func = getattr(imu, config['rx_func'])
        rx_state = getattr(imu, config['rx_state'])
        
        if rx_func == expected_func:
            return rx_state
            
    return None


def calibrate_imu(imu: object) -> bool:
    """
    执行IMU整体校准
    
    参数:
        imu: IMU设备实例
        
    返回:
        校准是否成功
    """
    print("\n=== 开始IMU整体校准 ===")
    print("请将IMU保持静止水平放置...")
    time.sleep(2)
    
    try:
        # 调用IMU库的校准方法
        state = imu.calibrate_imu()
        
        # 使用备份机制检查校准状态
        if state is None:
            state = get_calibration_state(imu, 'imu')
            
        # 显示校准结果
        result_text = format_state(state)
        print(f"IMU整体校准结果: {result_text}")
        
        # 校准后等待
        time.sleep(POST_CALIBRATION_WAIT)
        
        return state == 1
    except Exception as e:
        print(f"IMU整体校准出错: {str(e)}")
        return False


def calibrate_magnetometer(imu: object) -> bool:
    """
    执行磁力计校准
    
    参数:
        imu: IMU设备实例
        
    返回:
        校准是否成功
    """
    print("\n=== 开始磁力计校准 ===")
    print("请缓慢旋转IMU，确保各个方向都被测量到...")
    print("校准过程需要约10秒，请保持旋转...")
    time.sleep(1)  # 给用户准备时间
    
    try:
        # 调用IMU库的校准方法
        state = imu.calibrate_magnetometer()
        
        # 使用备份机制检查校准状态
        if state is None:
            state = get_calibration_state(imu, 'mag')
            
        # 显示校准结果
        result_text = format_state(state)
        print(f"磁力计校准结果: {result_text}")
        
        # 校准后等待
        time.sleep(POST_CALIBRATION_WAIT)
        
        return state == 1
    except Exception as e:
        print(f"磁力计校准出错: {str(e)}")
        return False


def calibrate_temperature(imu: object) -> bool:
    """
    执行温度传感器校准
    
    参数:
        imu: IMU设备实例
        
    返回:
        校准是否成功
    """
    print("\n=== 开始温度传感器校准 ===")
    
    # 获取用户输入的当前环境温度
    while True:
        try:
            user_input = input("请输入当前环境温度(摄氏度，例如: 25.0): ").strip()
            calibration_temperature = float(user_input)
            if not (-50.0 <= calibration_temperature <= 50.0):
                print("温度必须在 -50.0 到 50.0 °C 之间，请重新输入。")
                continue
            break
        except ValueError:
            print("无效的温度值，请输入数字。")
    
    print(f"正在使用温度 {calibration_temperature}°C 进行校准...")
    print("请保持IMU温度稳定...")
    time.sleep(2)  # 给温度稳定时间
    
    try:
        # 调用IMU库的校准方法
        state = imu.calibrate_temperature(calibration_temperature)
        
        # 使用备份机制检查校准状态
        if state is None:
            state = get_calibration_state(imu, 'temp')
            
        # 显示校准结果
        result_text = format_state(state)
        print(f"温度校准结果: {result_text}")
        
        # 校准后等待
        time.sleep(POST_CALIBRATION_WAIT)
        
        return state == 1
    except Exception as e:
        print(f"温度校准出错: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("IMU校准工具")
    print("支持I2C和串口通信模式")
    print("=" * 50)
    
    # 解析命令行参数
    args = parse_args()
    
    # 创建并初始化IMU设备
    imu, error_msg = create_imu_device(args)
    if not imu:
        print(f"初始化失败: {error_msg}")
        sys.exit(1)
    
    # 获取并显示固件版本
    version = get_firmware_version(imu)
    print(f"Firmware version: {version}")
    
    # 执行校准
    success_count = 0
    total_count = 0
    
    # 根据命令行参数选择要执行的校准类型
    calibrations_to_run = []
    if args.calibrate in ['imu', 'all']:
        calibrations_to_run.append(('imu', calibrate_imu))
    if args.calibrate in ['mag', 'all']:
        calibrations_to_run.append(('mag', calibrate_magnetometer))
    if args.calibrate in ['temp', 'all']:
        calibrations_to_run.append(('temp', calibrate_temperature))
    
    # 执行所有选定的校准
    for cal_type, cal_func in calibrations_to_run:
        total_count += 1
        if cal_func(imu):
            success_count += 1
    
    # 校准结果总结
    print("\n" + "=" * 50)
    print("校准完成！")
    print(f"结果: {success_count}/{total_count} 项校准成功")
    
    if success_count == total_count:
        print("✅ 所有校准项目均已成功完成！")
    else:
        print("⚠️  部分校准项目失败，请检查IMU连接后重试")
    
    # 关闭IMU连接
    print("\n正在关闭IMU连接...")
    if hasattr(imu, 'stop_data_reception'):
        imu.stop_data_reception()
    
    print("校准工具已退出")


if __name__ == "__main__":
    main()