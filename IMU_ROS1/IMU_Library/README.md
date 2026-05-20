# IMU_Library

IMU传感器通信Python库，支持通过串口和I2C协议与IMU设备进行通信，并提供实时3D可视化界面。

## 作者
JuxiTech

## 版本
1.0.0

## 功能特性
- 支持串口通信和I2C通信两种模式
- 读取加速度计、陀螺仪、磁力计原始数据
- 获取姿态数据（欧拉角和四元数）
- 读取气压计数据（高度、温度、气压）
- 支持传感器校准功能（整体校准、磁力计校准、温度校准）
- 可配置数据报告频率和融合算法类型
- 实时3D模型和2D指南针可视化界面

## 环境要求
- Python 3.8 或更高版本
- pip 包管理器

## 安装依赖
```bash
# 安装所有必需的依赖库
pip install pyserial smbus2 PyQt5 PyOpenGL numpy
如不用PyQt5可视化程序，可不用下载该库也可直接使用IMU_Library库进行数据读取和校准。
```

## 安装库
```bash
# 进入项目根目录
cd /path/to/IMU_Library/

# 安装库及其依赖
pip install -e .

# 或使用setup.py安装
python setup.py install
```

## 运行可视化程序
```bash
# 进入IMU_Library目录
cd /path/to/IMU_Library/IMU_Library/

# 运行可视化程序
python IMU_visualization.py
```

可视化程序功能：
- 左侧显示3D模型，实时反映IMU的姿态变化
- 右侧显示2D指南针，指示IMU的方位
- 顶部控制面板可选择IMU类型和进行连接操作

## IMU校准

### 校准说明
- **整体校准(imu)**：对加速度计和陀螺仪进行校准
- **磁力计校准(mag)**：对磁力计进行校准
- **温度校准(temp)**：对温度传感器进行校准

### 串口模式校准
```bash
# 进入IMU_Library目录
cd /path/to/IMU_Library/IMU_Library/

# 执行所有校准（整体、磁力计、温度）
python3 imu_calibration_tool.py --mode serial --port /dev/ttyUSB0

# 仅整体校准
python3 imu_calibration_tool.py --mode serial --port /dev/ttyUSB0 --calibrate imu

# 仅磁力计校准
python3 imu_calibration_tool.py --mode serial --port /dev/ttyUSB0 --calibrate mag

# 仅温度校准
python3 imu_calibration_tool.py --mode serial --port /dev/ttyUSB0 --calibrate temp
```

### I2C模式校准
```bash
# 进入IMU_Library目录
cd /path/to/IMU_Library/IMU_Library/

# 执行所有校准（整体、磁力计、温度）
python3 imu_calibration_tool.py --mode i2c --port 7

# 仅整体校准
python3 imu_calibration_tool.py --mode i2c --port 7 --calibrate imu

# 仅磁力计校准
python3 imu_calibration_tool.py --mode i2c --port 7 --calibrate mag

# 仅温度校准
python3 imu_calibration_tool.py --mode i2c --port 7 --calibrate temp
```

## 命令行工具使用

### 打印IMU数据

IMU_Library提供了命令行工具用于实时打印IMU传感器数据。

```bash
# 进入IMU_Library目录
cd /path/to/IMU_Library/IMU_Library/

# 使用串口模式打印IMU数据
python3 IMU_Serial_Library.py
#( ’*‘根据命令ll /dev/ttyUSB* 查看可用串口)
python3 IMU_Serial_Library.py --port /dev/ttyUSB* --rate 5

# 使用I2C模式打印IMU数据
python print_imu_data.py --mode i2c --port 7 --rate 5

# 启用调试模式
python print_imu_data.py --mode serial --port /dev/ttyUSB0 --debug
```

参数说明：
- `--mode`: 通信模式，可选值为`serial`(串口)或`i2c`
- `--port`: 串口名(如`/dev/ttyUSB0`)或I2C端口号(如`7`)
- `--rate`: 数据打印频率(Hz)，默认10Hz
- `--debug`: 启用调试模式，显示详细信息

## 不同轴数IMU设备的输出差异

根据IMU设备的轴数不同，可获取的数据类型也有所差异：

### 6轴IMU（加速度计+陀螺仪）
- ✅ 加速度计数据
- ✅ 陀螺仪数据
- ❌ 磁力计数据（无磁力计）
- ✅ 姿态角数据（通过6轴融合算法计算）
- ✅ 四元数数据（通过6轴融合算法计算）
- ❌ 气压计数据（无气压计）

### 9轴IMU（加速度计+陀螺仪+磁力计）
- ✅ 加速度计数据
- ✅ 陀螺仪数据
- ✅ 磁力计数据
- ✅ 姿态角数据（通过9轴融合算法计算）
- ✅ 四元数数据（通过9轴融合算法计算）
- ❌ 气压计数据（无气压计）

### 10轴IMU（加速度计+陀螺仪+磁力计+气压计）
- ✅ 加速度计数据
- ✅ 陀螺仪数据
- ✅ 磁力计数据
- ✅ 姿态角数据（通过10轴融合算法计算）
- ✅ 四元数数据（通过10轴融合算法计算）
- ✅ 气压计数据（高度、温度、气压）

注意：对于不支持的传感器类型，命令行工具会自动跳过相关数据的打印。

## 使用示例
### 串口通信示例
```python
from IMU_Library import IMU_Serial

# 初始化串口通信
imu = IMU_Serial(port="/dev/ttyUSB0", debug=True)

# 启动数据接收线程
imu.start_data_reception()

# 获取固件版本
version = imu.get_firmware_version()
print(f"固件版本: {version}")

# 读取传感器数据
accel = imu.get_accelerometer_data()
gyro = imu.get_gyroscope_data()
mag = imu.get_magnetometer_data()
attitude = imu.get_attitude_data()
quat = imu.get_quaternion_data()
baro = imu.get_barometer_data()
```

### I2C通信示例
```python
from IMU_Library import IMU_I2C

# 初始化I2C通信
imu = IMU_I2C(port=7, debug=True)

# 获取固件版本
version = imu.get_firmware_version()
print(f"固件版本: {version}")

# 读取传感器数据
accel = imu.get_accelerometer_data()
gyro = imu.get_gyroscope_data()
mag = imu.get_magnetometer_data()
attitude = imu.get_attitude_data()
quat = imu.get_quaternion_data()
baro = imu.get_barometer_data()
```

## 支持的平台
- Windows
- Linux

## 注意事项
1. 使用前请确保已正确连接IMU设备
2. 串口通信时需确保波特率设置为115200
3. I2C通信时需确保设备地址为0x23且已启用I2C接口
4. 首次使用建议先进行传感器校准
5. 可视化程序需要图形界面支持

## 常见问题解决方案

### 解决USB设备热插拔端口号变化问题

在Linux系统中，USB设备热插拔后可能会分配不同的端口号（如从`/dev/ttyUSB0`变为`/dev/ttyUSB1`）。
以下是使用udev规则创建固定端口号的解决方案：

#### 1. 查看USB设备信息
首先，连接IMU设备并获取其供应商ID和产品ID：
```bash
lsusb
```
输出示例：
Bus 001 Device 004: ID 1a86:7523 QinHeng Electronics CH340 serial converter
这里的`1a86`是供应商ID，`7523`是产品ID。

#### 2. 创建udev规则
创建一个新的udev规则文件：
```bash
sudo nano /etc/udev/rules.d/99-imu-serial.rules
```

添加以下内容（替换为您设备的实际ID）：
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="imu-serial", MODE="0666"

参数说明：
- `SUBSYSTEM=="tty"`：指定设备类型为串口
- `ATTRS{idVendor}=="1a86"`：设备的供应商ID
- `ATTRS{idProduct}=="7523"`：设备的产品ID
- `SYMLINK+="imu-serial"`：创建固定符号链接`/dev/imu-serial`
- `MODE="0666"`：设置设备权限，允许普通用户访问

#### 3. 重新加载udev规则
执行以下命令使新规则生效：
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 4. 验证设置
重新插拔IMU设备，检查符号链接是否创建成功：
```bash
ls -la /dev/imu-serial
```
输出示例：
lrwxrwxrwx 1 root root 7 1月 22 10:00 /dev/imu-serial -> ttyUSB0

#### 5. 使用固定端口号
现在可以使用`/dev/imu-serial`作为固定端口号：
```bash
# 使用固定端口号打印IMU数据
python3 IMU_Serial_Library.py --port /dev/imu-serial --rate 5

# 使用固定端口号进行校准
python3 imu_calibration_tool.py --mode serial --port /dev/imu-serial
```

## 许可证
MIT License