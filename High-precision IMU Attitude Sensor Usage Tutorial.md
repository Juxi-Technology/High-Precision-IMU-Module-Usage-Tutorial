## 1. Download and Installation

### 1.1 Download the Compressed Package

Download [IMU_ROS1.zip](https://juxitech.feishu.cn/wiki/GNgWwGnYIiBd4Gk81yccEN6jnNf), unzip it, and navigate to the `~/IMU_Library` directory.

### 1.2 Install Required Python Libraries

```PowerShell
pip install pyserial
pip install smbus2
```

### 1.3 Install the IMU_Library

```PowerShell
# Install the library and its dependencies
pip install -e .

# Or install using setup.py
python setup.py install
```

---

## 2. Port Mapping Configuration

To prevent port number changes after device reconnection, configure a persistent port mapping:

```PowerShell
# Create and edit the udev rules file
sudo gedit /etc/udev/rules.d/99-serial-imu.rules

# If gedit command is not found, install it first
sudo apt install gedit

# Add the following mapping content
KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE:="0777", SYMLINK+="imu-serial"
```

### Parameter Description

| Parameter | Description                                                  |
| --------- | ------------------------------------------------------------ |
| `--mode`  | Communication mode, optional values: `serial` (UART) or `i2c` |
| `--port`  | Serial port name (e.g., `/dev/ttyUSB0`) or I2C bus number (e.g., `7`) |
| `--rate`  | Data output frequency (Hz), default: 10Hz                    |
| `--debug` | Enable debug mode to display detailed runtime information    |

### Apply Configuration

```PowerShell
# Save and exit the editor, then run these commands to activate the rules
sudo udevadm trigger
sudo service udev reload
sudo service udev restart

# Verify the configuration
ll /dev/imu-serial

# Expected output example:
lrwxrwxrwx 1 root root 7 Jan 22 10:00 /dev/imu-serial -> ttyUSB0
```

---

## 3. Communication Usage

### 3.1 Serial Communication

```PowerShell
# Navigate to the IMU_Library directory (choose appropriate path for your ROS version)
cd ~/imu_ros1/src/IMU_ROS1/IMU_Library/IMU_Library 
# Or for ROS2:
cd ~/imu_ros2/src/IMU_ROS2/IMU_Library/IMU_Library

# Run the IMU serial data output script
python3 IMU_Serial_Library.py
```

### 3.2 I2C Communication

```PowerShell
# Navigate to the IMU_Library directory
cd ~/IMU_Library/IMU_Library

# Run the IMU I2C data output script
python3 IMU_I2C_Library.py
```

---

## 4. IMU Calibration

### 4.1 Serial Communication Calibration

```PowerShell
# Navigate to the IMU_Library directory
cd ~/IMU_Library/IMU_Library

# Run full calibration (IMU + magnetometer + temperature)
python3 imu_calibration_tool.py --mode serial --port /dev/imu-serial

# Run IMU only calibration
python3 imu_calibration_tool.py --mode serial --port /dev/imu-serial --calibrate imu

# Run magnetometer only calibration
python3 imu_calibration_tool.py --mode serial --port /dev/imu-serial --calibrate mag

# Run temperature only calibration
python3 imu_calibration_tool.py --mode serial --port /dev/imu-serial --calibrate temp
```

### 4.2 I2C Communication Calibration

```PowerShell
# Run full calibration (IMU + magnetometer + temperature)
python3 imu_calibration_tool.py --mode i2c --port 1

# Run IMU only calibration
python3 imu_calibration_tool.py --mode i2c --port 1 --calibrate imu

# Run magnetometer only calibration
python3 imu_calibration_tool.py --mode i2c --port 1 --calibrate mag

# Run temperature only calibration
python3 imu_calibration_tool.py --mode i2c --port 1 --calibrate temp
```
