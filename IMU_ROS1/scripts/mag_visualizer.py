#!/usr/bin/env python3

import rospy
import numpy as np
from visualization_msgs.msg import Marker
from sensor_msgs.msg import MagneticField
from geometry_msgs.msg import Point
import math

class MagVisualizer:
    def __init__(self):
        rospy.init_node('mag_visualizer', anonymous=True)
        
        # 订阅磁力计数据
        self.mag_sub = rospy.Subscriber("/imu/mag", MagneticField, self.mag_callback)
        
        # 发布可视化标记
        self.marker_pub = rospy.Publisher("mag_arrow", Marker, queue_size=1)
        
        # 创建箭头标记
        self.marker = Marker()
        self.marker.header.frame_id = "imu_link"
        self.marker.type = Marker.ARROW  # 使用箭头
        self.marker.action = Marker.ADD
        
        # 设置初始点（起点为原点）
        start_point = Point()
        start_point.x = 0.0
        start_point.y = 0.0
        start_point.z = 0.0
        self.marker.points.append(start_point)
        
        # 设置结束点（初始为单位向量，长度1米）
        end_point = Point()
        end_point.x = 1.0  # 长度为1米
        end_point.y = 0.0
        end_point.z = 0.0  # Z轴为0，限制在XY平面
        self.marker.points.append(end_point)
        
        # 设置颜色（蓝色代表磁场）
        self.marker.color.r = 0.0
        self.marker.color.g = 0.0
        self.marker.color.b = 1.0  # 蓝色
        self.marker.color.a = 1.0  # 不透明度
        
        # 设置尺寸
        self.marker.scale.x = 0.05  # 箭头轴直径
        self.marker.scale.y = 0.1   # 箭头头部宽度
        self.marker.scale.z = 0.1   # 箭头头部长度
        
        # 设置ID
        self.marker.id = 0
        
    def mag_callback(self, msg):
        # 更新标记header的时间戳
        self.marker.header.stamp = rospy.Time.now()
        
        # 获取磁场数据
        mag_x = msg.magnetic_field.x
        mag_y = msg.magnetic_field.y
        # 强制Z轴为0，限制在XY平面
        mag_z = 0.0
        
        # 计算XY平面内的磁场强度
        magnitude_xy = math.sqrt(mag_x**2 + mag_y**2)
        
        if magnitude_xy > 0.001:  # 避免除以零
            # 归一化XY平面的向量，保持长度为1米
            norm_x = mag_x / magnitude_xy
            norm_y = mag_y / magnitude_xy
            
            # 设置箭头终点，长度固定为1米
            self.marker.points[1].x = norm_x * 1.0  # 长度固定为1米
            self.marker.points[1].y = norm_y * 1.0
            self.marker.points[1].z = 0.0  # 保持在XY平面
        else:
            # 如果磁场太弱，保持默认方向（沿X轴）
            self.marker.points[1].x = 1.0
            self.marker.points[1].y = 0.0
            self.marker.points[1].z = 0.0
        
        # 发布标记
        self.marker_pub.publish(self.marker)

def main():
    try:
        visualizer = MagVisualizer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()

# 更新权限
# chmod +x ~/imu_ros1/src/IMU_ROS1/scripts/mag_visualizer.py