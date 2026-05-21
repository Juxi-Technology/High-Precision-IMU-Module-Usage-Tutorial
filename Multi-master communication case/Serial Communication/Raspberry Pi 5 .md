## 1. Connect the device

This tutorial takes the Raspberry Pi 5 motherboard and the official 64-bit version of the mirroring as an example. 

Connect the IMU attitude sensor to the USB port of the main controller via a Type-C cable. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MjkxNTVkYjcwY2NiMzgyYzNjYzRhNGQxNzZmYThhMzlfenFFUThsakdZek1tUU9oR3lreEQ5VDUwTXpvWTE1ckxfVG9rZW46TnE2eWJRRDRVb041UHZ4Ym9UTWNvTlUzblNiXzE3NzkzMjk0OTc6MTc3OTMzMzA5N19WNA)

## 2. Check device status

View device ID

```PowerShell
lsusb
```

View Device Number

```PowerShell
ls -l /dev/ttyU*
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=ODc2ZTM1MDQzMmJhZDI4NGZmMjBhZjliMDM4NGE4OGRfd0ZkZlRFSlEyNVJ3bnZ4VHFyUUlBd04yUW9TT3JRUUNfVG9rZW46Wk9TOGJ4OXh5b3JJdHF4aHdXM2NMbXBhbkZiXzE3NzkzMjk0OTc6MTc3OTMzMzA5N19WNA)

Set Port Mapping

```Bash
# 防止插拔后端口变更，请设置端口映射
sudo gedit /etc/udev/rules.d/99-serial-imu.rules

# 如出现没有gedit命令相关内容，先下载安装
sudo apt install gedit

# 填写映射内容
KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE:="0777", SYMLINK+="imu-serial"

# 参数说明：
`--mode`: 通信模式，可选值为`serial`(串口)或`i2c`
`--port`: 串口名(如`/dev/ttyUSB0`)或I2C端口号(如`7`)
`--rate`: 数据打印频率(Hz)，默认10Hz
`--debug`: 启用调试模式，显示详细信息

# 保存退出，运行命令使规则生效
sudo udevadm trigger
sudo service udev reload
sudo service udev restart

# 验证
ll /dev/imu-serial

# 输出示例：
lrwxrwxrwx 1 root root 7 1月 22 10:00 /dev/imu-serial -> ttyUSB0
```

## 3. Install the driver library

**3.1** **Install** **the Python libraries required for the code**

```PowerShell
sudo apt update
sudo apt install -y python3-serial
sudo apt install -y python3-smbus2
```

**3.2 Transfer Files**

Friends who are not yet familiar with using MobaXterm to transfer files, please refer to the following webpage for detailed installation and operation methods of MobaXterm:[文件远程传输](https://juxitech.feishu.cn/wiki/KB0Jw2o6Wis9f0ksyeFceVmgnfd)

Drag the decompressed files **IMU_ROS2** onto Raspberry Pi 5 via MobaXterm software. 

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=MjY2YWE3NzBlZDQ3MGQ1ZDc3NjdlNjg5YTUyODFiZTJfeDdEWHp5cGxBNzNaRlRGNHRmS1lRUjJ0VDZWTXlweVpfVG9rZW46RFZwcGI5U0V0b0xpRXB4Y3RUQ2NwanZrbm9mXzE3NzkzMjk0OTc6MTc3OTMzMzA5N19WNA)

## 4. View IMU data

**Enter the ~/IMU_Library directory and run the IMU_Serial_Library.py file** 

```PowerShell
cd ~/IMU_ROS2/IMU_Library

# 运行 IMU 数据打印文件
python3 -m IMU_Library.IMU_Serial_Library
```

![img](https://juxitech.feishu.cn/space/api/box/stream/download/asynccode/?code=N2Q0ZmEzNDc5MzlhYTlhMGQzNjk4N2U2YzMyYzUxOTZfdzYwU3M4RkVxVEVFeTBBdWdQYnMxOHZQQThvcGNVT3dfVG9rZW46UlRpYWJyV283b1NXTzZ4VHU3UmNHUmNYbnNiXzE3NzkzMjk0OTc6MTc3OTMzMzA5N19WNA)

Note: The above is the data reading for a 10-axis IMU. The 6-axis has no Magnetometer and Barometer data, and the 9-axis has no Barometer data.

## **5.** **IMU** **Calibration**

**Enter the ~/IMU_Library directory and run the imu_calibration_tool.py file** 

```PowerShell
cd ~/IMU_Library

# 运行 IMU 校准代码文件 --串口通讯校准
# 执行所有校准（整体、磁力计、温度）
python3 -m IMU_Library.imu_calibration_tool --mode serial --port /dev/imu-serial

# 仅整体校准
python3 -m IMU_Library.imu_calibration_tool --mode serial --port /dev/imu-serial --calibrate imu

# 仅磁力计校准
python3 -m IMU_Library.imu_calibration_tool --mode serial --port /dev/imu-serial --calibrate mag

# 仅温度校准
python3 -m IMU_Library.imu_calibration_tool --mode serial --port /dev/imu-serial --calibrate temp
```

## 6. Precautions

If the device ID can be found but the device number cannot, you can refer to the following command to install the ch34x driver 

```PowerShell
sudo apt remove brltty
git clone https://github.com/clhchan/CH341SER.git
cd CH341SER
make -j6
sudo make install
sudo modprobe ch34x
```
