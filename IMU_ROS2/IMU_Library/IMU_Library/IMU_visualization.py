import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QComboBox, QLabel, QMessageBox, QFrame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen , QFont
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
from IMU_Library.IMU_Serial_Library import IMU_Serial
from IMU_Library.IMU_I2C_Library import IMU_I2C

class GLWidget(QGLWidget):
    """OpenGL 3D 渲染窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        # 视角控制参数
        self.camera_distance = 5.0  # 相机距离物体的距离
        self.camera_theta = 0.0     # 水平旋转角度
        self.camera_phi = 0.0       # 垂直旋转角度
        
        # 鼠标交互参数
        self.mouse_pressed = False
        self.last_mouse_pos = [0, 0]
        
        # 标定参数
        self.calibration_roll = 0.0
        self.calibration_pitch = 0.0
        self.calibration_yaw = 0.0
        self.is_calibrated = False

    def initializeGL(self):
        """初始化OpenGL环境"""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        
        # 启用光照
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)  # 启用光源0
        
        # 设置环境光（均匀照亮整个场景）
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])  # 环境光强度
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])  # 漫反射光强度
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0]) # 镜面反射光强度
        
        # 设置光源位置（固定在场景上方）
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        
        # 设置材质属性
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.7, 0.7, 0.7, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    def resizeGL(self, width, height):
        """窗口大小变化时调用"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """绘制3D场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 计算相机位置（支持视角旋转）
        camera_x = self.camera_distance * np.sin(self.camera_theta) * np.cos(self.camera_phi)
        camera_y = self.camera_distance * np.sin(self.camera_phi)
        camera_z = self.camera_distance * np.cos(self.camera_theta) * np.cos(self.camera_phi)
        
        # 设置相机位置
        gluLookAt(camera_x, camera_y, camera_z,  # 相机位置
                 0.0, 0.0, 0.0,   # 观察点
                 0.0, 1.0, 0.0)   # 上方向
        
        # 根据IMU姿态旋转立方体（应用标定偏移）
        if self.is_calibrated:
            display_roll = self.roll - self.calibration_roll
            display_pitch = self.pitch - self.calibration_pitch
            display_yaw = self.yaw - self.calibration_yaw
        else:
            display_roll = self.roll
            display_pitch = self.pitch
            display_yaw = self.yaw
        
        # 修复：调整旋转方向，解决X、Z轴旋转相反的问题
        glRotatef(display_yaw, 0.0, 0.0, 1.0)    # 绕Z轴旋转 (yaw) - 移除负号
        glRotatef(display_pitch, 0.0, 1.0, 0.0)  # 绕Y轴旋转 (pitch)
        glRotatef(display_roll, 1.0, 0.0, 0.0)   # 绕X轴旋转 (roll) - 移除负号
        
        # 绘制实心立方体
        size = 1.0  # 立方体大小（半边长）
        
        # 使用四边形绘制实心立方体
        glBegin(GL_QUADS)
        
        # 前面 - 浅灰色
        glColor3f(0.7, 0.7, 0.7)
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        
        # 后面 - 稍深灰色
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, -size)
        
        # 左面 - 中灰色
        glColor3f(0.6, 0.6, 0.6)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        
        # 右面 - 中灰色
        glColor3f(0.6, 0.6, 0.6)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)
        
        # 顶面 - 浅灰色
        glColor3f(0.8, 0.8, 0.8)
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        
        # 底面 - 深灰色
        glColor3f(0.4, 0.4, 0.4)
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        
        glEnd()
        
        # 绘制立方体边框，使轮廓更清晰
        glDisable(GL_LIGHTING)  # 禁用光照以确保边框颜色一致
        glColor3f(0.0, 0.0, 0.0)  # 黑色边框
        glLineWidth(1.5)  # 边框宽度
        
        glBegin(GL_LINES)
        
        # 前面
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        
        glVertex3f(-size, size, size)
        glVertex3f(-size, -size, size)
        
        # 后面
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)
        
        glVertex3f(-size, size, -size)
        glVertex3f(-size, -size, -size)
        
        # 连接前后
        glVertex3f(-size, -size, size)
        glVertex3f(-size, -size, -size)
        
        glVertex3f(size, -size, size)
        glVertex3f(size, -size, -size)
        
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)  # 重新启用光照
        
        # 绘制坐标轴
        glDisable(GL_LIGHTING)  # 禁用光照以确保坐标轴颜色一致
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X轴 - 红色
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        
        # Y轴 - 绿色
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        
        # Z轴 - 蓝色
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)  # 重新启用光照

    def update_attitude(self, roll, pitch, yaw):
        """更新IMU姿态数据"""
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.update()  # 触发重绘

    def calibrate_position(self):
        """标定当前位置为零位"""
        self.calibration_roll = self.roll
        self.calibration_pitch = self.pitch
        self.calibration_yaw = self.yaw
        self.is_calibrated = True
        print(f"位置标定完成！标定值：roll={self.calibration_roll:.2f}, pitch={self.calibration_pitch:.2f}, yaw={self.calibration_yaw:.2f}")

    def reset_calibration(self):
        """重置标定"""
        self.calibration_roll = 0.0
        self.calibration_pitch = 0.0
        self.calibration_yaw = 0.0
        self.is_calibrated = False
        print("标定已重置")

    # 鼠标事件处理
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.mouse_pressed = True
        self.last_mouse_pos = [event.x(), event.y()]
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.mouse_pressed = False
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if not self.mouse_pressed:
            return
            
        current_pos = [event.x(), event.y()]
        dx = current_pos[0] - self.last_mouse_pos[0]
        dy = current_pos[1] - self.last_mouse_pos[1]
        
        # 修复：调整鼠标旋转方向，使视角旋转与鼠标拖动方向一致
        self.camera_theta -= dx * 0.01  # 反转水平旋转方向
        self.camera_phi += dy * 0.01    # 反转垂直旋转方向
        
        # 限制垂直旋转角度，避免翻转
        self.camera_phi = max(-np.pi/2 + 0.1, min(np.pi/2 - 0.1, self.camera_phi))
        
        self.last_mouse_pos = current_pos
        self.update()
        
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        # 缩放视角
        delta = event.angleDelta().y() / 120.0
        self.camera_distance = max(2.0, min(10.0, self.camera_distance - delta * 0.5))
        self.update()

# 极简2D指南针实现 - 简化版，不使用QPolygonF/QPointF
class CompassWidget(QWidget):
    """极简2D指南针视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.yaw = 0.0  # 偏航角（度）
        self.setMinimumSize(200, 200)
        
    def paintEvent(self, event):
        """绘制指南针"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width, height = self.width(), self.height()
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 3  # 指南针半径
        
        # 背景设置
        painter.fillRect(0, 0, width, height, QColor(30, 30, 30))
        
        # 绘制指南针中心
        painter.setPen(QColor(100, 100, 100))
        painter.setBrush(QColor(60, 60, 60))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 保存当前绘图状态
        painter.save()
        
        # 将坐标原点移动到指南针中心
        painter.translate(center_x, center_y)
        
        # 应用旋转（指南针转动）
        painter.rotate(-self.yaw)
        
        # 绘制方向线条（东南西北）
        line_length = radius
        
        # 北 (N) - 红色
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawLine(0, 0, 0, -line_length)
        
        # 东 (E) - 绿色
        painter.setPen(QPen(QColor(0, 255, 0), 3))
        painter.drawLine(0, 0, line_length, 0)
        
        # 南 (S) - 蓝色
        painter.setPen(QPen(QColor(0, 0, 255), 3))
        painter.drawLine(0, 0, 0, line_length)
        
        # 西 (W) - 黄色
        painter.setPen(QPen(QColor(255, 255, 0), 3))
        painter.drawLine(0, 0, -line_length, 0)
        
        # 绘制物体方向（X轴方向，灰色箭头）- 使用drawLine代替多边形
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        arrow_length = line_length // 2
        arrow_size = 15
        
        # 箭头主线
        painter.drawLine(0, 0, arrow_length, 0)
        
        # 箭头头部 - 使用两条线代替多边形
        painter.drawLine(arrow_length, 0, arrow_length - arrow_size, -arrow_size // 2)
        painter.drawLine(arrow_length, 0, arrow_length - arrow_size, arrow_size // 2)
        
        # 恢复绘图状态
        painter.restore()
        
        # 绘制方向文本（固定位置）
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        text_offset = 5
        
        # 北
        painter.setPen(QColor(255, 0, 0))
        painter.drawText(center_x - 10, center_y - radius - text_offset, "N")
        
        # 东
        painter.setPen(QColor(0, 255, 0))
        painter.drawText(center_x + radius + text_offset, center_y + 5, "E")
        
        # 南
        painter.setPen(QColor(0, 0, 255))
        painter.drawText(center_x - 10, center_y + radius + text_offset + 15, "S")
        
        # 西
        painter.setPen(QColor(255, 255, 0))
        painter.drawText(center_x - radius - text_offset - 20, center_y + 5, "W")
        
    def update_yaw(self, yaw):
        """更新偏航角数据"""
        self.yaw = yaw
        self.update()  # 触发重绘

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMU 3D 可视化")
        self.setGeometry(100, 100, 900, 600)
        
        # IMU连接状态
        self.is_connected = False
        self.imu = None
        
        # 创建OpenGL窗口
        self.gl_widget = GLWidget(self)
        
        # 创建极简指南针窗口（替换之前的OpenGL指南针）
        self.compass_widget = CompassWidget(self)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gl_widget, 3)  # 3:1的比例
        main_layout.addWidget(self.compass_widget, 1)
        
        # 创建控制面板
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        
        # IMU类型选择
        self.imu_type_combo = QComboBox()
        self.imu_type_combo.addItems(["Serial", "I2C"])
        control_layout.addWidget(QLabel("IMU类型:"))
        control_layout.addWidget(self.imu_type_combo)
        
        # 连接按钮
        self.connect_button = QPushButton("连接IMU")
        self.connect_button.clicked.connect(self.on_connect_clicked)
        control_layout.addWidget(self.connect_button)
        
        # 标定按钮
        self.calibrate_button = QPushButton("标定位置")
        self.calibrate_button.clicked.connect(self.on_calibrate_clicked)
        self.calibrate_button.setEnabled(False)  # 初始禁用
        control_layout.addWidget(self.calibrate_button)
        
        # 重置标定按钮
        self.reset_calibrate_button = QPushButton("重置标定")
        self.reset_calibrate_button.clicked.connect(self.on_reset_calibrate_clicked)
        self.reset_calibrate_button.setEnabled(False)  # 初始禁用
        control_layout.addWidget(self.reset_calibrate_button)
        
        # 状态标签
        self.status_label = QLabel("未连接")
        control_layout.addWidget(self.status_label)
        
        main_layout.addLayout(control_layout, 1)
        
        # 创建中央控件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 创建定时器用于更新IMU数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_imu_data)
        self.timer.start(50)  # 每50ms更新一次

    def init_ui(self):
        """初始化UI界面"""
        # 创建主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 创建3D视图和指南针布局
        view_layout = QHBoxLayout()
        
        # 创建OpenGL渲染窗口
        self.gl_widget = GLWidget()
        view_layout.addWidget(self.gl_widget, 3)  # 3D视图占3份空间
        
        # 创建指南针视图
        self.compass_widget = CompassWidget()
        self.compass_widget.setMinimumSize(200, 200)
        self.compass_widget.setMaximumSize(300, 300)
        view_layout.addWidget(self.compass_widget, 1)  # 指南针占1份空间
        
        main_layout.addLayout(view_layout)
        
        # 创建控制面板
        control_layout = QHBoxLayout()
        
        # IMU类型选择
        self.imu_type_combo = QComboBox()
        self.imu_type_combo.addItems(["Serial", "I2C"])
        control_layout.addWidget(QLabel("IMU类型:"))
        control_layout.addWidget(self.imu_type_combo)
        
        # 连接按钮
        self.connect_button = QPushButton("连接IMU")
        self.connect_button.clicked.connect(self.on_connect_clicked)
        control_layout.addWidget(self.connect_button)
        
        # 标定按钮
        self.calibrate_button = QPushButton("标定位置")
        self.calibrate_button.clicked.connect(self.on_calibrate_clicked)
        self.calibrate_button.setEnabled(False)  # 初始禁用
        control_layout.addWidget(self.calibrate_button)
        
        # 重置标定按钮
        self.reset_calibrate_button = QPushButton("重置标定")
        self.reset_calibrate_button.clicked.connect(self.on_reset_calibrate_clicked)
        self.reset_calibrate_button.setEnabled(False)  # 初始禁用
        control_layout.addWidget(self.reset_calibrate_button)
        
        # 状态标签
        self.status_label = QLabel("未连接")
        control_layout.addWidget(self.status_label)
        
        main_layout.addLayout(control_layout)
        self.setCentralWidget(central_widget)

    def on_connect_clicked(self):
        """连接/断开IMU按钮点击事件"""
        if not self.is_connected:
            # 连接IMU
            imu_type = self.imu_type_combo.currentText()
            
            try:
                if imu_type == "Serial":
                    # 假设串口设备为/dev/ttyUSB0
                    self.imu = IMU_Serial(port="/dev/ttyUSB0", debug=False)
                    self.imu.start_data_reception()  # 启动数据接收线程
                else:
                    # I2C连接
                    self.imu = IMU_I2C(debug=False)
                
                # 获取固件版本
                firmware_version = self.imu.get_firmware_version()
                print(f"IMU固件版本: {firmware_version}")
                
                # 更新连接状态
                self.is_connected = True
                self.connect_button.setText("断开IMU")
                self.connect_button.setStyleSheet("background-color: #ff6b6b;")
                self.status_label.setText(f"已连接 {imu_type} IMU")
                self.status_label.setStyleSheet("color: green;")
                
                # 启用标定按钮
                self.calibrate_button.setEnabled(True)
                self.reset_calibrate_button.setEnabled(True)
                
                print("IMU连接成功!")
                
            except Exception as e:
                QMessageBox.critical(self, "连接失败", f"无法连接IMU: {str(e)}")
                print(f"IMU连接失败: {str(e)}")
        else:
            # 断开IMU连接
            try:
                if hasattr(self.imu, 'stop_data_reception'):
                    self.imu.stop_data_reception()
                del self.imu
                self.imu = None
                
                # 更新连接状态
                self.is_connected = False
                self.connect_button.setText("连接IMU")
                self.connect_button.setStyleSheet("")
                self.status_label.setText("未连接")
                self.status_label.setStyleSheet("")
                
                # 禁用标定按钮
                self.calibrate_button.setEnabled(False)
                self.reset_calibrate_button.setEnabled(False)
                
                print("IMU已断开连接!")
                
            except Exception as e:
                QMessageBox.critical(self, "断开失败", f"无法断开IMU连接: {str(e)}")
                print(f"断开IMU连接失败: {str(e)}")

    def on_calibrate_clicked(self):
        """位置标定按钮点击事件"""
        if self.is_connected:
            self.gl_widget.calibrate_position()
            self.compass_widget.set_calibration(self.gl_widget.calibration_yaw, True)
            QMessageBox.information(self, "标定完成", "IMU位置标定已完成！")

    def on_reset_calibrate_clicked(self):
        """重置标定按钮点击事件"""
        self.gl_widget.reset_calibration()
        self.compass_widget.set_calibration(0.0, False)
        QMessageBox.information(self, "重置完成", "标定已重置！")

    def update_imu_data(self):
        """更新IMU数据并刷新显示"""
        if self.is_connected and self.imu is not None:
            try:
                # 获取最新的IMU数据
                roll, pitch, yaw = self.imu.get_attitude_data()
                
                # 更新OpenGL窗口中的姿态
                self.gl_widget.update_attitude(roll, pitch, yaw)
                
                # 更新极简指南针
                self.compass_widget.update_yaw(yaw)
                    
            except Exception as e:
                print(f"更新IMU数据失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())