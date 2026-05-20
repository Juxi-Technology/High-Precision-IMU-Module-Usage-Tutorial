
## 功能特性

### IMU_Library
- 支持串口和I2C两种通信模式
- 读取加速度计、陀螺仪、磁力计原始数据
- 获取姿态数据（欧拉角和四元数）
- 读取气压计数据（高度、温度、气压）
- 支持传感器校准功能（整体校准、磁力计校准、温度校准）
- 可配置数据报告频率和融合算法类型
- 实时3D模型和2D指南针可视化界面
- 可移至IMU_Library目录下运行，IMU_Library库提供README.md文件，详细说明使用方法和注意事项。

### ROS2 接口
- 发布IMU数据到ROS2话题
- 提供IMU和磁力计标定服务
- 支持多种通信接口类型
- 可配置发布频率和调试模式
- 数据有效性检查和错误处理

## 环境要求

- Python 3.8 或更高版本
- ROS2 Humble 或兼容版本
- pip 包管理器

## 安装步骤

### 1. 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt update

# 安装Python依赖
pip install pyserial smbus2 PyQt5 PyOpenGL numpy
如不用PyQt5可视化程序，可不用下载PyQt5、PyOpenGL库也可直接使用IMU_Library库进行数据读取和校准。
```

### 安装IMU_Library
```bash
cd path/to/IMU_Library/
pip install -e .
```

### 编译ROS2包
```bash
cd path/to/IMU_ROS2/
colcon build --symlink-install
source install/setup.bash
```

## 使用方法
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

### 一键启动Riz2
```bash
cd path/to/IMU_ROS2/
ros2 launch imu_ros2 imu_visualization.launch.py
```

### 运行IMU数据发布节点

```bash
# 使用默认参数（串口模式，/dev/imu-serial）
ros2 run imu_ros2 imu_publisher

# 使用自定义参数
ros2 run imu_ros2 imu_publisher --ros-args -p imu_type:=serial -p serial_port:=/dev/imu-serial  -p publish_rate:=100.0

# 使用I2C接口
ros2 run imu_ros2 imu_publisher --ros-args -p imu_type:=i2c -p i2c_port:=7
```

## 话题和服务

### 发布的话题
- `/imu/data`: 发布IMU数据（sensor_msgs/Imu）
- `/imu/mag`: 发布磁力计数据（sensor_msgs/MagneticField）
- `/baro`: 发布气压计数据（std_msgs/Float32MultiArray）
- `/euler`: 发布欧拉角数据（std_msgs/Float32MultiArray）

### 运行节点并查看话题数据
#### 1. 查看话题列表
```bash
# 查看当前可用的话题列表
ros2 topic list
```

#### 2. 运行IMU数据发布节点
```bash
# 使用默认参数运行
ros2 run imu_ros2 imu_publisher

# 或使用固定端口
ros2 run imu_ros2 imu_publisher --ros-args -p serial_port:=/dev/imu-serial
```

#### 3. 查看话题数据
```bash
# 查看IMU数据（加速度计、陀螺仪、四元数）
ros2 topic echo /imu/data

# 查看磁力计数据
ros2 topic echo /imu/mag

# 查看气压计数据
ros2 topic echo /baro

# 查看欧拉角数据
ros2 topic echo /euler
```

#### 4. 查看话题详细信息
```bash
# 查看话题类型和发布者/订阅者
ros2 topic info /imu/data

# 查看话题的发布频率
ros2 topic hz /imu/data

# 查看话题的带宽
ros2 topic bw /imu/data
```

#### 5. 查看服务列表
```bash
# 查看当前可用的服务列表
ros2 service list
```

## 参数配置

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `imu_type` | string | `serial` | IMU接口类型：`i2c`、`serial`或`device` |
| `i2c_port` | int | `7` | I2C端口号 |
| `serial_port` | string | `/dev/ttyUSB0` | 串口设备路径 |
| `serial_baudrate` | int | `115200` | 串口波特率 |
| `publish_rate` | double | `100.0` | 数据发布频率（Hz） |
| `debug_mode` | bool | `False` | 是否启用调试模式 |
| `enable_auto_calib` | bool | `False` | 是否启用自动校准 |
| `fusion_algorithm` | int | `9` | 融合算法类型：6轴或9轴 |
| `allow_zero_data` | bool | `True` | 是否允许发布全0数据 |

## 支持的平台

- Linux
- Windows

## 注意事项

1. 使用前请确保已正确连接IMU设备
2. 串口通信时需确保波特率设置为115200
3. I2C通信时需确保设备地址为0x23且已启用I2C接口
4. 首次使用建议先进行传感器校准
5. 可视化程序需要图形界面支持

## 许可证

- IMU_Library: MIT License
- imu_ros2: Apache License 2.0

## 作者

JuxiTech

## 版本

1.0.0