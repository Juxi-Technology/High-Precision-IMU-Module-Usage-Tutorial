**System Configuration: ubuntu20.04**

**ROS1 Version: noetic**

1. ### ROS1 Environment Configuration

   1. **Set up ROS1 Installation** **Source**

   ```PowerShell
   sudo sh -c '. /etc/lsb-release && echo "deb http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
   ```

   2. **Set Key**

   ```PowerShell
   sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
   ```

   ```Plain
   sudo apt update
   ```

   3. **Install ROS1 (Official Download)**

   ```PowerShell
   sudo apt install ros-noetic-desktop-full
   ```

   Proxy Accelerated Download and Installation of ROS1

   wget http://fishros.com/install -O fishros && . fishros

   4. **Configure** **environment variables**

   ```Plain
   echo "source /opt/ros/noetic/setup.bash">> ~/.bashrc
   ```

   ```PowerShell
   source ~/.bashrc
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

   3. **Fill in the content of the mapping file**

   ```PowerShell
   KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE:="0777", SYMLINK+="imu-serial"
   ```

   4. **Save and exit, then run the command to make the rules take effect**

   ```PowerShell
   sudo udevadm trigger
   ```

   ```Plain
   sudo service udev reload
   ```

   ```Plain
   sudo service udev restart
   ```

   5. **Verify**

   ```PowerShell
   ll /dev/imu-serial
   ```
      ```PowerShell
   sudo usermod -aG dialout ash
      ```

3. ### Import the prepared Compressed Packet 

   1. **Feishu has it in the same level directory** **[IMU_ROS1.zip](https://juxitech.feishu.cn/wiki/GNgWwGnYIiBd4Gk81yccEN6jnNf)**
   2. **Transferred into the** **virtual machine** **via file transfer software**
   3. **Install** **the IMU_Library** 

   ```PowerShell
   cd IMU_ROS1
   # 下载解压IMU_ROS1压缩文件后，进入到IMU_Library目录下，运行以下指令
   cd IMU_Library
   
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

**When rendering issues occur, execute the following command** 

```PowerShell
sudo apt-get install ros-noetic-imu-filter-madgwick
sudo apt-get install ros-noetic-rviz-imu-plugin
```

5. ### Build ROS1 Project 

   1. **Open a new terminal in the /home directory and create a new ROS1 workspace**

   ```PowerShell
   mkdir imu_ros1
   cd imu_ros1
   mkdir src
   cd src/
   catkin_init_workspace
   ```

   2. **Copy the transferred file IMU_ROS1 folder to the ~/imu_ros1/src/ directory**

   ```PowerShell
   # 复制 IMU_ROS1 文件夹到新建的 src 目录下
   cp -r ~/IMU_ROS1 ~/imu_ros1/src
   cd ~/imu_ros1
   catkin_make
   ```

   3. **Write the working directory ~/imu_ros1 into the environment variable**

   ```PowerShell
   # 编辑 ~/.bashrc
   sudo gedit ~/.bashrc
   
   # 把下面命令写到末尾
   source ~/imu_ros1/devel/setup.bash
   
   source ~/.bashrc
   ```

6. ### Start ROS1 Node 

   1. **Open the terminal, enter roscore to start the node**

   ```PowerShell
   # 启动roscore
   roscore
   
   # 新开终端，设置环境，启动节点
   source ~/imu_ros1/devel/setup.bash
   ```

   2. **Add executable permission to the Python script (crucial)**

    Enter the `scripts` directory where the script is located, and execute the `chmod +x` command to grant executable permissions (`+x` means add execute, i.e., add execution permissions):

   ```PowerShell
   # 进入imu_driver.py所在目录（按你的实际路径）
   cd ~/imu_ros1/src/IMU_ROS1/scripts/ 
   
   # 赋予可执行权限（仅需执行1次，永久生效）
   chmod +x imu_driver.py
   chmod +x mag_visualizer.py
   ```

    Return to the imu_ros1 folder and run imu_driver.py 

   ```Plain
   cd ~/imu_ros1
   ```

   ```Plain
   rosrun IMU_ROS1 imu_driver.py
   ```

7. ### IMU Data Printing

   1. **Open a new terminal and view the imu topic** 

   ```PowerShell
   # 查看当前发布的所有话题
   rostopic list
   ```

   2. **Print topic data**

   ```PowerShell
   # 打印IMU原始数据
   rostopic echo /imu/data_raw
   
   # 打印磁力计数据
   rostopic echo /imu/mag
   ```

8. ### RViz Visualization

   1. **Run the command to start rviz()**

   ```PowerShell
   roslaunch IMU_ROS1 imu_display.launch
   ```

9. ### Frequently Asked Questions 

   1. If the startup node fails to open, please try the following commands 

   ```PowerShell
   # 在~/imu_ros1目录下运行
   source devel/setup.bash
   
   # 端口号问题
   sudo chmod 666 /dev/imu-serial
   ```

   2. The three axes display is very small in RVIZ visualization, recheck Enable axes 
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/552f6bfac177422bba374fb11e525f74.png)
