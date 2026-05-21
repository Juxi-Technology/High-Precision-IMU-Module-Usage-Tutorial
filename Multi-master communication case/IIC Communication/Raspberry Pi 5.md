## 1. Connect the device

This tutorial takes the Raspberry Pi 5 motherboard and the official 64-bit version of the mirroring as an example. 

Connect the IMU attitude sensor to the I2C interface of Raspberry Pi 5 as shown in the figure below. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=OWJhNDBjZTk5YWM1NmM4MmM3ZDY3N2ZlNmQyY2NjZjhfUEpRdkwwYzJkcUlla21adzZQbFB4ekxwT3UxNlQ0bFVfVG9rZW46QmFFOGJ1b2Jab3hUZ1l4bGM0OGNoRmJTbjBjXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

| IMU姿态传感器 | 树莓派5（物理引脚） |
| ------------- | ------------------- |
| SDA           | 3                   |
| SCL           | 5                   |
| GND           | GND                 |
| 3.3V          | 3.3V                |

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZWUzNTBhZDQ3Njc3OWU0Nzk5MjBlMjhiZjFlZTk4MzdfWld4Q3NrMzRUSnIxVnNJU21NZ0VqN0hrV2l6S09SQ2JfVG9rZW46UXg2YWJHY1pqb3lOVmd4Vjh1dGNYYjZWblJmXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

## 2. Check device status

First, install I2Ctool, then enter the following in the terminal: 

```PowerShell
sudo apt-get update
sudo apt-get install -y i2c-tools
```

View I2C Devices 

```PowerShell
sudo i2cdetect -y -r -a 1
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=YmRkZjEzZjYxMTg3NTMwODMwNDViY2Q4NzUxOGFjNmNfWmR5dVVnUEx5NHM3bVNOc2ZEYm04U2VHYXROeEEwTjRfVG9rZW46S254eWJ2ZmhSbzBlRXR4OHRENWM1bWoyblllXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

## 3. Install the driver library

3.1 **Install the Python libraries required for the code** 

```PowerShell
sudo apt update
sudo apt install -y python3-serial
sudo apt install -y python3-smbus2
```

3.2 Transfer Files

Friends who are not yet familiar with using MobaXterm to transfer files, please refer to the following webpage for detailed installation and operation methods of MobaXterm:[文件远程传输](https://github.com/Juxi-Technology/ICM42670P-High-Precision-IMU-Module/blob/main/Multi-master%20communication%20case/Remote%20File%20Transfer.md)

Drag the decompressed files onto Raspberry Pi 5 via MobaXterm software. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MDFhOWMzOWI5OGIxMDBmNzU4Mzg3M2E0MDI1N2Q1YmRfbWkwRmpaMThTNE9GazJVY2s1bDN4VWhwak03THJCVHhfVG9rZW46SGJtMGJ2enZwb1U0cmx4bGxZa2N6QkU0bkRiXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

## 4. View IMU data

**Enter the ~/IMU_Library directory and run the IMU_Serial_Library.py file** 

```PowerShell
cd ~/imu_ros2/src/IMU_ROS1/IMU_Library

# 运行 IMU 数据打印文件
python3 -m IMU_Library.IMU_I2C_Library
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjVjNDc2OWU3N2VkMzliYTMxMDhmYjczNzJlOTMzODFfSG1TZ25iNmpaMU9xMVVFZnM1aWVOc3JBSEcwMEZ0SWdfVG9rZW46QUVXWWJJZ3hEb3N0WkV4NDNrRmNUeGxqbjRlXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

Note: The above is the data reading for a 10-axis IMU. The 6-axis has no Magnetometer and Barometer data, and the 9-axis has no Barometer data.

## **5. IMU Calibration**

**Enter the ~/IMU_Library directory and run the imu_calibration_tool.py file** 

```PowerShell
cd ~/IMU_Library

# 运行 IMU 校准代码文件 --I2C通讯校准
# 执行所有校准（整体、磁力计、温度）
python3 -m IMU_Library.imu_calibration_tool --mode i2c --port 1

# 仅整体校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 1 --calibrate imu

# 仅磁力计校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 1 --calibrate mag

# 仅温度校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 1 --calibrate temp
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MmRlY2Y2MThjZWE0M2Q5MzQxODY2ZDA5ZTkwMDA2NWRfdXdOZ1lYWkVMR1FoeDUzTkx1SUVqdjdjWHZscFNQNnJfVG9rZW46VGFiV2JOOUlyb2RvcDR4eXExamN3QXlybjFjXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

## 6. Precautions

Raspberry Pi 5 needs to enable the i2c pin in advance. 

The opening operation is as follows: 

Terminal run command

```PowerShell
sudo raspi-config
```

Select using the arrow keys on the keyboard, and press the Enter key on the keyboard to enter after selection

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=NmM3ZTVlYTFjZDI2YzU0ZTA4MGZjYjEwZTA4MTg2Y2ZfQmZnM2xqUFpPUTV3czBLdXJCM2FMcmxKdkM0RlBvMlRfVG9rZW46TTFRR2JtVjUzbzg1YUx4VDBYQ2NJajl3bnVlXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

Select I2C, and after selection, press the Enter key on the keyboard to enter.

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZmEzN2ExMDNlMmUxMzdkMDQ4MDFmNmI5MGRlMGVhMzhfSlNPQU1BS1FUT1dsTUtpeUx3RWFNZ2k2Yk1Pdkc3WnFfVG9rZW46QVhLQWJNYjVsbzdpRnl4VzRuRmM0UnlhbmpiXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

After selecting I2C, press the Enter key on the keyboard, use the arrow keys to select Yes, and then press the Enter key to confirm. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MWNiMjhkYWI5NGRjNTM5ZGM2YzNlMmZmMzE5NjZiN2ZfamxabW9NUDROSEZkdmQ1TTFOTkYyOTZLZFF5c1ZxOWFfVG9rZW46UDU0V2Jad1Zqb3kxZ3R4VUNoRGNqbnB2bkhjXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

Press Enter to confirm

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=NGFlMjQ3MjYxY2YzMWZjMjdjM2RhZjhiZjdjY2QzNDRfamhlZUtGc29BUFJKaWtLRGd6VGpwRnVMalg4a251WlZfVG9rZW46RVhrY2JGWjdnb29CREt4YjRTZGNQajdBbmFmXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)

Press the arrow keys to select Finish, then press Enter to exit the configuration.

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=NjViYWU0OGI5MmVkMzMxYzU2ZWUyODJiMzJjMDY2ZWRfOU56ZW5VT0tEbExKbUlaSlJSOUJOUjZWUEVKZ1BmWEpfVG9rZW46TUJCdmJhVmhDb1plOGx4bVVFYmNwUHBXbnJnXzE3NzkzMzI3MTY6MTc3OTMzNjMxNl9WNA)
