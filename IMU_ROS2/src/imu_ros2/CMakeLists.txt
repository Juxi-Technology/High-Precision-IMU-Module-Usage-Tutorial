cmake_minimum_required(VERSION 3.8)
project(imu_ros2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖包
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# 生成服务消息
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/CalibrateIMU.srv"
  "srv/CalibrateMagnetometer.srv"
  "srv/ResetCalibration.srv"
  DEPENDENCIES std_msgs
)

ament_package()