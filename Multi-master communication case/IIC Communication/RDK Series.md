## Step 1 Connect devices

This tutorial takes the mirroring of the? version of the RDK X5 motherboard as an example. 

Connect the IMU attitude sensor to the I2C interface of the RDK X5 as shown below.

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MjFhNTQxMDhjMTQ5OWY5YTNhNDYzMjczMTY1YmE4MzdfYlRlRFE5NlpFU2ZXNXBxYnVaakh5QkpCeDJuVjNSeHRfVG9rZW46S2FZemI1Wmhsb0UzY2F4TW94QmNrWkRibnFlXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

| IMU姿态传感器 | RDK5（物理引脚） |
| ------------- | ---------------- |
| SDA           | 3                |
| SCL           | 5                |
| GND           | GND              |
| 3.3V          | 3.3V             |

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=N2E3MmRiODliZjBhYzcxNDk1Y2JmNjgwNmJjMjE3MmNfeERndEtnaXFFNjcyQ2VMOFBQblU5UGNmM2Y1eW1JcEdfVG9rZW46UGUxZmJ3VnBGb09JTHB4N21aRmN4RjllbmdnXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

## 2. Check device status

View I2C Devices 

```PowerShell
python3 /app/40pin_samples/test_i2c.py
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=N2UyNTQwNTA2OGNjMTc2MWE3ZmNmYzkxNTMzMjRlZjZfSG9hR2hMdENQaXRDdk80MGJLeVVsT0dET00xRDVQWHBfVG9rZW46QlFOOWJvdmhabzJSS014TmN4NmNCb2p0bm9jXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

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

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=NDBkODk0ZmY2NDcxODc1N2M0NzZlMjY3MThhNDZiZDNfanQ4a2IzQkFEUmR1cWlFRWp1WUdCUXpXTXRDRGU1dDdfVG9rZW46QmlYUWJqak9Wb2ZCSEp4UG10MWNtMUZFblZjXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

## 4. View IMU data

**Enter the ~/IMU_Library directory and run the IMU_Serial_Library.py file** 

```PowerShell
cd ~/imu_ros1/src/IMU_ROS1/IMU_Library
# 或
cd ~/imu_ros2/src/IMU_ROS2/IMU_Library

# 运行 IMU 数据打印文件
python3 -m IMU_Library.IMU_I2C_Library
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjkyNzk0ODcxNzcyNGQzOTQ3MzQ5YzQzNjk3ZjU3ZGJfdGFQSTZmbVhteDVsSjZvNEVtdTJFcU1HRUhTWHowWjNfVG9rZW46UkN1Q2JWaDVSb21DbE14ZzFNV2N4U1hobjVmXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

Attention: The above is the data reading of 10-axis IMU, 6-axis without magnetometer and barometer data, 9-axis without barometer data.

## **5. IMU Calibration**

**Enter the ~/IMU_Library directory and run the imu_calibration_tool.py file** 

```PowerShell
cd ~/IMU_Library

# 运行 IMU 校准代码文件 --I2C通讯校准
# 执行所有校准（整体、磁力计、温度）
python3 -m IMU_Library.imu_calibration_tool --mode i2c --port 0

# 仅整体校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 0 --calibrate imu

# 仅磁力计校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 0 --calibrate mag

# 仅温度校准
python3-m IMU_Library.imu_calibration_tool --mode i2c --port 0 --calibrate temp
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTRkODljOTJlMmJlZDkzNGNkNGE3YTM5ZjEwODVjNGFfMWNXT0dMRmRCZUh0dFlYblNkcndWbEtVZmZkNTBRYXZfVG9rZW46THpHZ2JUV2JXb2tiUnh4S3FrdWN6NVhRbkJkXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)

## 6. Precautions

 When using the RDK X5 main board, it is necessary to modify the serial number of the I2C bus according to the actual situation. The modification position is shown in the figure below. Usually, it is bus number 0.

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDZkYmY4ZmEyYzMxNjQxNzYxYzU0NzA2Y2YwYTFiZDlfd0pBc2lBbHoxQlZJUTJrVzhvdXpwMklUYzR1aU51WmRfVG9rZW46RnZjZmJ4a2Nhb2lrVFN4ZFBydmNPa0lobnFiXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=YzUxODU4MTc0NDU0ZDRkMjkwYjM4ZjI3MTg5YzNiMDBfcDk0eUU2ZjlBR2swU2hValo1RmY5bXd6QWttbm95dlRfVG9rZW46TFJzeGJCc3Vnb2RUdWJ4SFp2QWNyYzU2blJlXzE3NzkzMzI4NTg6MTc3OTMzNjQ1OF9WNA)
