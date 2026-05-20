**System configuration: ubuntu22.04**

**ROS2 Version: humble**

1. ### ROS2 Environment Configuration

   1. **Update download source**

   ```PowerShell
   sudo apt update
   ```

   2. **Enter the ros2 download command** 

   ```PowerShell
   wget http://fishros.com/install -O fishros && . fishros
   ```

2. ### Device Connected to Virtual Machine

   1. **View Device**

   ```PowerShell
   ll /dev/ttyUSB*
   ```

   2. **Establish Port Mapping** 

   ```PowerShell
   sudo gedit /etc/udev/rules.d/99-serial-imu.rules
   ```

   2. **Fill in the content of the mapping file**

   ```PowerShell
   KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE:="0777", SYMLINK+="imu-serial"
   ```

   3. **Save and exit, then run the command to make the rules take effect**

   ```PowerShell
   sudo udevadm trigger
   sudo service udev reload
   sudo service udev restart
   ```

   4. **Verify**

   ```PowerShell
   ll /dev/imu-serial
   ```

3. ### Import the prepared Compressed Packet 

   1. **Feishu has it in the same level directory** **[IMU_ROS2.zip](https://juxitech.feishu.cn/wiki/ElvZwpfqniF9EikmSVoc3xMgn5c)**
   2. **Transferred into the virtual machine via file transfer software**
   3. **Install the IMU_Library** 

   ```PowerShell
   # 下载解压IMU_ROS2压缩文件后，进入到IMU_Library目录下，运行setup.py
   cd IMU_ROS2/IMU_Library
   
   # 安装库及其依赖
   pip install -e .
   
   # 或使用setup.py安装
   python setup.py install
   ```

4. ### Installation of Python-related Libraries

   ```PowerShell
   sudo pip3 install pyserial
   sudo pip3 install smbus2
   ```

5. ### Build ROS2 project 

   1. **Return to the ~/IMU_ROS2 directory** 

   ```PowerShell
   cd IMU_ROS2
   colcon build --symlink-install
   ```

   2. **Write the working directory ~/IMU_ROS2 into the environment variable**

   ```PowerShell
   # 编辑 ~/.bashrc
   sudo gedit ~/.bashrc
   
   # 把下面命令写到末尾
   source ~/IMU_ROS2/install/setup.bash
   ```

After successful compilation, execute the following command to check if there are any executable files under the imu_ros2 package 

```
ros2 pkg executables imu_ros2
```

6. ### Start ROS2 node 

   ```PowerShell
   source install/setup.bash
   ros2 run imu_ros2 imu_publisher
   ```

7. ### IMU Data Printing

   1. **Open a new terminal and view the imu topic** 

   ```PowerShell
   ros2 topic list
   ```

   2. **Print the data of the /imu/data topic**

   ```PowerShell
   ros2 topic echo /imu/data
   ```

   3. **Open a new terminal and view the msg topic**

   ```PowerShell
   ros2 topic echo /imu/mag
   ```

8. ### RViz2 Visualization

   1. **Run the command to open the rviz visualization interface**

   ```PowerShell
   ros2 launch imu_ros2 imu_visualization.launch.py
   ```

9. ### Frequently Asked Questions 

   1. If the startup node fails to open, please try the following commands 

   ```PowerShell
   # 在~/IMU_ROS2目录下运行
   source install/setup.bash
   
   # 端口号问题
   sudo chmod 666 /dev/imu-serial
   ```
