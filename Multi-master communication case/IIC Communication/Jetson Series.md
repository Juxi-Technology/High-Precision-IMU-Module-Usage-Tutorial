## 1. Connect the device

This tutorial takes the Jetson Orin NX motherboard as an example. 

Connect the IMU attitude sensor to the I2C interface of Jetson Orin NX as shown in the figure below. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MjRmYTdhNDc2MjY0MzhkYzc0MzRhNjhjNTEyZTQ5N2VfUjBGNGVYTUhuU1pWeWpTbGVzd3VQbnFYUVZTc3c4TzhfVG9rZW46T2hDdmJ2UTdNb0Nqakp4bDV0UWNxb3AybmtmXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

| IMU姿态传感器 | Jetson Orin NX（物理引脚） |
| ------------- | -------------------------- |
| SDA           | 3                          |
| SCL           | 5                          |
| GND           | GND                        |
| 3.3V          | 3.3V                       |

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=Zjk3Y2U3NTBlNDk1YmUyYzJjMTczOTFhM2NiMTc0N2FfUlI3UkhrTk1CM0lXU2RzM0x5VXhxaXhZV2o1bGJHT1pfVG9rZW46Q05MdGI5UkJlb0dERGF4YW9KYWMwbWNzbnNjXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

## 2. Check device status

First, install I2Ctool, then enter the following in the terminal: 

```PowerShell
sudo apt-get update
sudo apt-get install -y i2c-tools
```

View I2C Devices 

```PowerShell
sudo i2cdetect -y -r -a 7
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDIwMDk2ODA4OTMwYjA3Yzk2NGNiMzEyZDFlZTVlNWZfeVlyOVdTME9seVdmcmpZT2FKQU9WME5ORVc3RE9CbnVfVG9rZW46S1hJQ2JmZTY3b09uT2p4SGNMdWNKbUFDbk1oXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

## 3. Install the driver library

3.1 **Install the Python libraries required for the code** 

```PowerShell
sudo apt update
sudo apt install -y python3-serial
sudo apt install -y python3-smbus2
```

3.2 Transfer Files

暂时无法在飞书文档外展示此内容

Friends who are not yet familiar with using MobaXterm to transfer files, please refer to the following webpage for detailed installation and operation methods of MobaXterm:[文件远程传输](https://juxitech.feishu.cn/wiki/KB0Jw2o6Wis9f0ksyeFceVmgnfd)

Drag the decompressed files onto Raspberry Pi 5 via MobaXterm software. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=OGFmZTQyMGI1YTgwNDNkZWZlMGYwYzcxOGExODY1YjVfeWlvdzBjNm94NE9WQlVDM2d5ZUhwNDg5MWhvVTFLbE5fVG9rZW46Wm9mQ2JTN2ZUb2RuZ0Z4NEtUWGMxc3NjbjhlXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

## 4. View IMU data

**Enter the ~/IMU_Library directory and run the IMU_Serial_Library.py file** 

```PowerShell
cd ~/imu_ros2/src/IMU_ROS2/IMU_Library

# 运行 IMU 数据打印文件
python3 -m IMU_Library.IMU_I2C_Library
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ODI0MjQzMmY5ZTA1ZTI4YjAwZDM3OTkwNTk1MWRlNGZfaTczT3JXZnJweTNrYnJnazhnekUyTFlKZGdFNXdRTUZfVG9rZW46VXR4RGJxSFdnb2RydEl4a3BSTGN2TWRpbjlkXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

Note: The above is the data reading for a 10-axis IMU. The 6-axis has no Magnetometer and Barometer data, and the 9-axis has no Barometer data.

## **5. IMU Calibration**

**Enter the ~/IMU_Library directory and run the imu_calibration_tool.py file** 

```PowerShell
cd ~/IMU_Library

# 运行 IMU 校准代码文件 --I2C通讯校准
# 执行所有校准（整体、磁力计、温度）
python3 -m IMU_Library.imu_calibration_tool --mode i2c --port 7

# 仅整体校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 7 --calibrate imu

# 仅磁力计校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 7 --calibrate mag

# 仅温度校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 7 --calibrate temp
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=NTczZjVmMjlmMjU3ZmY2MGE0ZmU2MjZjNjhlMDAxZDdfcnZpWnRESEV1UEU2ZmtXa3JXVGdPWjNkSzVQWFlMN3dfVG9rZW46S2F5SmI0V2Nyb0VtTll4MUQyb2NjdnVHblVlXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)

## 6. Precautions

When using the Orin series motherboard, you need to modify the bus number of the I2C according to the actual situation. The modification location is shown in the figure below. Usually, it is bus 7. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=N2ZiMTc2ODAzNjA0ZGFkNzgxZDRmNzAwMmJjNTM4MGJfNlU3c3VxTHVtS1Y2UWFsV2lTclpNQWk3ZUNkenZNMGtfVG9rZW46R0xUdWJ4amg1b0hiNzd4V1BYZ2M5TTFCblc4XzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=OGM2YzRmOGJmNWFmY2Y0ZmZlMWM3ZTYzMjFjY2M5OTBfUjUwYXBpdDRkVmFrZHhEUEtTZjVyYXJKZEFCMk5sSnpfVG9rZW46RVlVQWJCOFlLbzB1N3V4R2NwRGM0TERKbjNjXzE3NzkzMzI3NTY6MTc3OTMzNjM1Nl9WNA)
