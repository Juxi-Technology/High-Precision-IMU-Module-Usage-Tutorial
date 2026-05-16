## High-Precision IMU Module Usage Tutorial

This repository contains complete documentation, usage guides, application cases, and supporting resources for a high-performance IMU (Inertial Measurement Unit) module powered by a 72MHz 32-bit processor. The module delivers real-time attitude calculation, dynamic compensation, and up to 100Hz data output frequency, making it ideal for robotics, UAVs, navigation systems, and more.

## Key Features
- Built-in high-precision attitude sensor paired with a 72MHz high-performance 32-bit processor
- Real-time attitude calculation and dynamic compensation for reliable output
- Up to 100Hz data update frequency, balancing fast response and stable performance
- Dual communication interface support: IIC and UART (Serial)
- Wide compatibility: Works seamlessly with microcontrollers, Linux-based main controllers, and ROS (Robot Operating System)
- Suitable for use cases including robot motion control, UAV attitude stabilization, and intelligent navigation/positioning

## What's Included
### 📚 Documentation
1. **Core Module Specification**: Complete version introduction, pin function description, product parameters, sensor performance metrics, and dimension drawings
2. **Full Usage Tutorial**: Step-by-step guide for library installation, communication setup, and IMU calibration
3. **Multi-Master Communication Guide**: Instructions for CH341 driver installation and multi-device communication configuration
4. **ROS Integration Resources**: Pre-built packages and setup guides for ROS1 and ROS2 compatibility
5. **Remote Access Guides**:
  - MobaXterm installation and usage tutorial for SSH/SFTP remote management
  - WinSCP step-by-step guide for Windows-based SSH file transfer
### 📦 Supporting Resources
- **Serial Communication uartassist5.15.zip**: Serial port debugging tool for communication testing
- **IMU_ROS1.zip**: Preconfigured ROS1 package for out-of-the-box IMU integration
- **IMU_ROS2.zip**: Preconfigured ROS2 package for out-of-the-box IMU integration

### Important Notes
- CH341 serial driver must be installed with administrator privileges on Windows systems
- Ensure your host machine and target device are on the same local network for SSH/SFTP file transfer
- All tools support both serial and I2C communication modes, configurable via command line parameters
- File transfer failures are usually caused by insufficient permissions on the target device: run chmod 777 <target-directory> to resolve
