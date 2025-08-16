import os
import subprocess

import sys
import time

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, QParallelAnimationGroup, QTimer, \
    QDateTime, QSequentialAnimationGroup, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSizePolicy, QGraphicsOpacityEffect
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice, QLegend
from PySide6.QtGui import QPainter, QColor, QFont
from Todo_ui import Ui_MainWindow
import json
import ctypes
from datetime import datetime
import webbrowser
import sys
import os
from PySide6 import QtCore

import sys
import os
from pathlib import Path


def run_as_admin(exe_path, args=None):
    """以管理员权限运行程序"""
    if args is None:
        args = []

    # 转换路径为Windows可识别的格式
    params = ' '.join([f'"{x}"' for x in args])

    # 调用ShellExecute以管理员权限运行
    ctypes.windll.shell32.ShellExecuteW(
        None,  # 父窗口句柄
        "runas",  # 操作：请求管理员权限
        exe_path,  # 程序路径
        params,  # 参数
        None,  # 工作目录（None表示当前目录）
        1  # 显示窗口（SW_SHOWNORMAL）
    )


import socket


class SocketServerThread(QThread):
    """
    在后台运行的Socket服务端线程
    """
    data_received = Signal(str)  # 定义信号，用于传递接收到的数据

    def __init__(self):
        super().__init__()
        self.host = 'localhost'  # 本地通信
        self.port = 45027  # 端口号（确保未被占用）

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"主程序监听中：{self.host}:{self.port}")

            while True:
                conn, addr = s.accept()  # 等待客户端连接
                with conn:
                    data = conn.recv(1024).decode()  # 接收数据（UTF-8解码）
                    if data:
                        self.data_received.emit(data)  # 发射信号


# 可视化饼图
"""class AnimatedPieChart(QWidget):
    def __init__(self, data=None, colors=None, parent=None):
        super().__init__(parent)
        self.data = data or {"数学": 45, "语文": 30, "物理": 15, "化学": 10}
        self.colors = colors or [
            QColor("#FF6384"),  # 红色
            QColor("#36A2EB"),  # 蓝色
            QColor("#FFCE56"),  # 黄色
            QColor("#4BC0C0"),  # 青色
            QColor("#9966FF"),  # 紫色
            QColor("#FF9F40")  # 橙色
        ]
        self.series = QPieSeries()
        self.chart = QChart()
        self.chart_view = QChartView()

        # 初始化UI
        self.setup_ui()

        # 初始化动画
        self.setup_animation()

    def setup_ui(self):

        # 添加数据
        for i, (label, value) in enumerate(self.data.items()):
            if value > 0:  # 只添加值大于0的数据
                slice_ = self.series.append(label, value)
                slice_.setLabel(f"{label}: {value}%")
                slice_.setLabelVisible(True)
                slice_.setBrush(self.colors[i % len(self.colors)])
                # 设置标签位置和视觉优化
                slice_.setLabelPosition(QPieSlice.LabelOutside)
                slice_.setLabelArmLengthFactor(0.2)  # 缩短连接线长度

        # 设置图表
        self.chart.addSeries(self.series)
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chart.legend().setAlignment(Qt.AlignRight)
        self.chart.setTitle("Focus Distribution")
        self.chart.setTitleFont(QFont("Arial", 10, QFont.Bold))  # 缩小标题字体

        # 调整图例位置和大小
        self.chart.legend().setVisible(True)
        self.chart.legend().setMarkerShape(QLegend.MarkerShapeCircle)

        # 设置图表视图
        self.chart_view.setChart(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # 设置布局 - 使用伸展因子让图表填满可用空间
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # 保留少量边距
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

        # 设置尺寸策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setup_animation(self):

        self.chart.animationOptions = QChart.AllAnimations"""


################################################主程序########################3

class Chemms_Todo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.load_tasks_from_json()
        self.setWindowTitle("CheemsTodo")
        self.server_thread = SocketServerThread()
        self.server_thread.data_received.connect(self.handle_data_from_client)  # 连接信号
        self.server_thread.start()
        print("主程序Socket线程ID：", self.server_thread.isRunning())
        #######################################变量####################################
        # 获取当前日期时间
        now = datetime.now()
        self.current_date = f"{now.year}{now.month:02d}{now.day:02d}"  # 格式: 20230814
        self.last_recorded_date = self.read_config_json("Times", "datetimes", "0")

        # 初始化统计变量（使用清晰命名）
        self.total_sessions = 0  # 总专注次数
        self.total_seconds = 0  # 总专注时间(秒)
        self.today_sessions = 0  # 今日专注次数
        self.today_seconds = 0  # 今日专注时间(秒)

        # 从配置文件加载历史数据
        last_total_sessions = int(self.read_config_json("Times", "Total_num", "0"))
        last_total_seconds = int(self.read_config_json("Times", "Total_time", "0"))
        last_today_sessions = int(self.read_config_json("Times", "Today_times", "0"))
        last_today_seconds = int(self.read_config_json("Times", "Today_num", "0"))

        # 如果是新的一天
        if self.current_date != self.last_recorded_date:
            self.total_sessions = last_total_sessions
            self.total_seconds = last_total_seconds
            # 重置今日数据
            self.today_sessions = 0
            self.today_seconds = 0
            # 更新记录日期
            self.update_config_json("Times", "datetimes", self.current_date)
        else:
            # 如果是同一天，累加数据
            self.total_sessions = last_total_sessions
            self.total_seconds = last_total_seconds
            self.today_sessions = last_today_sessions
            self.today_seconds = last_today_seconds

        # 更新UI显示
        self.label_17.setText(str(self.today_seconds))
        self.label_11.setText(str(self.today_sessions))
        self.label_14.setText(str(self.today_sessions))
        self.label_8.setText(str(self.total_sessions))
        self.label_9.setText(str(self.total_seconds))
        self.add_show_state = False
        self.ban_app = False
        self.Notifications = False
        self.Strict_Mode = False
        self.Lock = False

        timer = QTimer(self)
        timer.timeout.connect(self.update_info)
        timer.start(1000)
        # 连接信号槽
        self.listWidget.itemClicked.connect(self.switch_page)
        #####################################程序初始化#######################################

        self.Strict_Mode = self.read_setting_json('Strict_Mode', 'strict_mode') == "1"

        # 初始化Strict_Mode状态 - 这里原来是错误的检查了notifications
        if self.Strict_Mode:
            self.setting_ui.Open_Enable_Strict.setText("Close")
            self.setting_ui.Open_Enable_Strict.setStyleSheet("""
                       QPushButton#Open_Enable_Strict {
                           border-radius: 7px;
                           background-color: rgb(255, 74, 74);
                           font: 700 10pt "Microsoft YaHei UI";
                       }
                       QPushButton#Open_Enable_Strict:hover {
                           background-color: rgb(223, 65, 65);
                       }
                   """)
            self.Strict_Mode = True
            self.Lock = True
        #######################################饼图初始化####################################
        # 初始化饼图
        self.init_pie_chart()

        # 初始化动画系统
        self.init_animation_system()

    def init_animation_system(self):
        """初始化动画所需的系统属性"""
        # 确保动画控件具有正确的属性

        # 初始位置设置
        self.task_ui.Add.move(400, -280)
        self.task_ui.Add.show()

    # 饼图显示
    def init_pie_chart(self):
        """初始化饼图"""
        # 确保widget_9有布局
        if not self.widget_9.layout():
            layout = QVBoxLayout(self.widget_9)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        # 自定义颜色
        custom_colors = [
            QColor("#79D1C5"),  # 主色调
            QColor("#6892D5"),  # 蓝色
            QColor("#F2C14E"),  # 黄色
            QColor("#F78154")  # 橙色
        ]

        # 创建饼图数据
        chart_data = {
            "数学": 45,
            "语文": 30,
            "物理": 15,
            "化学": 10,
        }

        # 创建并添加饼图
        """self.pie_chart = AnimatedPieChart(
            data=chart_data,
            colors=custom_colors,
            parent=self.widget_9
        )"""

        # 添加到布局
        # self.widget_9.layout().addWidget(self.pie_chart)

        #######################################样式及位置临时调整####################################
        self.task_ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.task_ui.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.widget_9.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.Notice.setGeometry(QRect(1550, 20, 401, 91))
        self.tableWidget_2.setStyleSheet("""/* 整体表格样式 */
        QTableWidget {
             /* 浅灰色背景 */
            gridline-color: transparent;
        	background-color: rgb(255, 255, 255);
            border: 1px solid #e5e5e5;
            border-radius: 4px;
            gridline-color: #e5e5e5;

        	font: 700 10pt "Microsoft YaHei UI";
            font-size: 12px;
            selection-background-color: #0078d4;  /* Windows 11选中色 */
            selection-color: white;
            outline: 0;  /* 移除选中时的虚线框 */
        }
        QTableView::item {

            border-right: none;  /* 隐藏竖线 */
        }
        /* 表头样式 */
        QHeaderView::section {

        	color: rgb(160, 174, 192);
        	background-color: rgb(255, 255, 255);

            border: none;
            border-bottom: 1px solid #e5e5e5;
            font-weight: 500;  /* 中等粗细 */
            padding-left: 8px; 

        }

        /* 悬停效果 */
        QHeaderView::section:hover {
            background-color: #edebe9;
        }

        /* 按下效果 */
        QHeaderView::section:pressed {
            background-color: #e1dfdd;
        }

        /* 行交替颜色 */
        QTableWidget::item:alternate {
            background-color: #faf9f8;
        }

        /* 单元格悬停效果 */
        QTableWidget::item:hover {
            background-color: #f3f3f3;
        }

        /* 滚动条样式 */
        QScrollBar:vertical {
            border: none;
            background: #f3f3f3;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical {
            background: #c4c4c4;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }""")
        self.task_ui.tableWidget.setStyleSheet("""/* 整体表格样式 */
QTableWidget {
     /* 浅灰色背景 */
    gridline-color: transparent;
	background-color: rgb(255, 255, 255);
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    gridline-color: #e5e5e5;

	font: 700 10pt "Microsoft YaHei UI";
    font-size: 12px;
    selection-background-color: #0078d4;  /* Windows 11选中色 */
    selection-color: white;
    outline: 0;  /* 移除选中时的虚线框 */
}
QTableView::item {

    border-right: none;  /* 隐藏竖线 */
}
/* 表头样式 */
QHeaderView::section {

	color: rgb(160, 174, 192);
	background-color: rgb(255, 255, 255);

    border: none;
    border-bottom: 1px solid #e5e5e5;
    font-weight: 500;  /* 中等粗细 */
    padding-left: 8px; 

}

/* 悬停效果 */
QHeaderView::section:hover {
    background-color: #edebe9;
}

/* 按下效果 */
QHeaderView::section:pressed {
    background-color: #e1dfdd;
}

/* 行交替颜色 */
QTableWidget::item:alternate {
    background-color: #faf9f8;
}

/* 单元格悬停效果 */
QTableWidget::item:hover {
    background-color: #f3f3f3;
}

/* 滚动条样式 */
QScrollBar:vertical {
    border: none;
    background: #f3f3f3;
    width: 10px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #c4c4c4;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}""")
        ##############################################信号链接###############################################
        # 设置widget_9的尺寸策略

        self.task_ui.pushButton_2.clicked.connect(self.add_show)
        self.task_ui.Cancel_Add.clicked.connect(self.add_show)

        self.task_ui.OK_Add.clicked.connect(self.add_task)

        # Then connect
        self.pushButton_2.clicked.connect(self.switch_to_page_1)
        self.setting_ui.Open_Enable_Strict.clicked.connect(self.Open_Strict)
        self.pushButton.clicked.connect(self.web)
        self.lock_ui.pushButton_2.clicked.connect(self.lock)

    #####################################################函数区域#############################################
    def web(self):


        # 打开默认浏览器并访问指定 URL
        url = "https://xuhaoyang123321.github.io/Cheems_Todo.github.io"
        webbrowser.open(url)

        # 在新标签页中打开 URL

    def lock(self):
        Lock_time = self.lock_ui.timeEdit.time()
        Lock_time_int = f"{Lock_time.hour()}小时{Lock_time.minute()}分钟"
        if Lock_time_int is not None:
            time_str = Lock_time_int
            parts = time_str.split('小时')
            time_hour_int = int(parts[0])
            time_min_int = int(parts[1].replace('分钟', ''))
            time_s_complete = (time_hour_int * 60 + time_min_int) * 60

            print(f"开始任务，时间设置为: {time_s_complete}秒")
            self.Notice_info("Todo", "锁机开始", f"即将开始 {time_s_complete}秒 的任务！")
            self.total_seconds += time_s_complete
            self.today_seconds += time_s_complete

            # 修正路径获取方式

            exe_path = r"dist\Lock_window_main.exe"
            run_as_admin(exe_path)
            # 使用完整路径启动

            # 使用Popen而不是run

            # 等待锁屏窗口初始化
            time.sleep(1)  # 等待1秒确保Socket服务器启动

            # 发送数据
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(3)  # 设置3秒超时
                    s.connect(('localhost', 45028))
                    s.sendall(str(time_s_complete).encode())
                    print("时间数据发送成功")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(3)  # 设置3秒超时
                    s.connect(('localhost', 45028))
                    s.sendall(b"Lock")
                    print("时间数据发送成功")


            except Exception as e:
                print(f"发送数据失败: {e}")
                self.Notice_info("错误", "连接失败", "无法连接到锁屏窗口")

    def send_test_message(self, message):
        """发送测试消息到锁屏窗口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 45028))
            s.sendall(str(message).encode())

    def handle_data_from_client(self, data):
        """
        处理来自附属程序的数据
        """
        self.Notice_info("Todo", "恭喜！", "您已成功完成任务！")

        print(f"[主程序信号处理] 收到数据（类型：{type(data)}，内容：{repr(data)}）")

    def switch_to_page_1(self):
        self.stackedWidget.setCurrentIndex(1)

    def add_task(self):
        try:
            print("start")
            """向表格中添加新任务"""
            # 获取输入的任务名称和时间
            task_name = self.task_ui.lineEdit.text()
            time = self.task_ui.timeEdit.time()
            task_time = f"{time.hour()}小时{time.minute()}分钟"

            # 检查任务名称是否为空
            if not task_name:
                print("任务名称不能为空!")
                self.Notice_info("Todo", "注意", "似乎任务名没有填写")
                return
            if time.hour() == 0 and time.minute() == 0:
                print("任务时间不能为0!")
                self.Notice_info("Todo", "注意", "请设置一个有效的任务时间")
                return

            # 获取当前行数
            row_position = self.task_ui.tableWidget.rowCount()
            row_position_2 = self.tableWidget_2.rowCount()

            # 插入新行
            self.task_ui.tableWidget.insertRow(row_position)
            self.tableWidget_2.insertRow(row_position_2)

            # 设置第一列：任务名称
            name_item = QtWidgets.QTableWidgetItem(task_name)
            name_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.task_ui.tableWidget.setItem(row_position, 0, name_item)

            # 为第二个表格创建新的 QTableWidgetItem
            name_item_2 = QtWidgets.QTableWidgetItem(task_name)
            name_item_2.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_2.setItem(row_position_2, 0, name_item_2)

            # 设置第二列：任务时间
            time_item = QtWidgets.QTableWidgetItem(task_time)
            time_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.task_ui.tableWidget.setItem(row_position, 1, time_item)

            time_item_2 = QtWidgets.QTableWidgetItem(task_time)
            time_item_2.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_2.setItem(row_position_2, 1, time_item_2)

            # 设置第三列：专注次数（初始为0）
            count_item = QtWidgets.QTableWidgetItem("0")
            count_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.task_ui.tableWidget.setItem(row_position, 2, count_item)

            count_item_2 = QtWidgets.QTableWidgetItem("0")
            count_item_2.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_2.setItem(row_position_2, 2, count_item_2)

            # 设置第四列：按钮组
            Start_button = QtWidgets.QPushButton("开始")
            Start_button.setFixedSize(80, 30)
            Start_button.setStyleSheet("""
                            QPushButton {
                                background-color: #4fd1c5;
                                color: white;
                                border-radius: 4px;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background-color:#4ac5b9 ;
                            }
                        """)

            delete_btn = QtWidgets.QPushButton("删除")
            delete_btn.setFixedSize(80, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)

            # 创建容器widget用于居中按钮
            container = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(container)
            layout.addWidget(Start_button)  # 添加Start按钮
            layout.addWidget(delete_btn)  # 添加Delete按钮
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)  # 设置按钮间距
            container.setLayout(layout)
            # 设置第四列：按钮组
            Start_button_2 = QtWidgets.QPushButton("开始")
            Start_button_2.setFixedSize(80, 30)
            Start_button_2.setStyleSheet("""
                            QPushButton {
                                background-color: #4fd1c5;
                                color: white;
                                border-radius: 4px;
                                padding: 5px;
                            }
                            QPushButton:hover {
                                background-color:#4ac5b9 ;
                            }
                        """)

            delete_btn_2 = QtWidgets.QPushButton("删除")
            delete_btn_2.setFixedSize(80, 30)
            delete_btn_2.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)

            # 创建容器widget用于居中按钮
            container_2 = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(container_2)
            layout.addWidget(Start_button_2)  # 添加Start按钮
            layout.addWidget(delete_btn_2)  # 添加Delete按钮
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)  # 设置按钮间距
            container_2.setLayout(layout)

            self.task_ui.tableWidget.setCellWidget(row_position, 3, container)
            self.tableWidget_2.setCellWidget(row_position_2, 3, container_2)
            delete_btn.clicked.connect(lambda _, r=row_position: self.delete_task(r))
            delete_btn_2.clicked.connect(lambda _, r=row_position: self.delete_task(r))
            Start_button.clicked.connect(lambda _, r=row_position: self.start_task(r))
            Start_button_2.clicked.connect(lambda _, r=row_position: self.start_task(r))
            # 注意这里使用 setCellWidget

            # 清空输入框
            self.task_ui.lineEdit.clear()

            # 隐藏添加任务窗口
            self.add_show()

            # 保存到JSON文件
            self.save_tasks_to_json()
            self.Notice_info("Todo", "成功！", "任务添加成功！")
        except Exception as e:
            print(f"添加任务时出错: {str(e)}")

    def save_tasks_to_json(self):
        """将任务保存到JSON文件"""
        tasks = []
        for row in range(self.task_ui.tableWidget.rowCount()):
            task_data = {
                "name": self.task_ui.tableWidget.item(row, 0).text(),
                "time": self.task_ui.tableWidget.item(row, 1).text(),  # 已经是"XX小时XX分钟"格式
                "count": self.task_ui.tableWidget.item(row, 2).text()
            }
            tasks.append(task_data)

        try:
            with open("Task_info.json", "w", encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"保存任务失败: {str(e)}")

    def load_tasks_from_json(self):
        """从JSON文件加载任务"""
        try:
            if not os.path.exists("Task_info.json"):
                return

            with open("Task_info.json", "r", encoding='utf-8') as f:
                tasks = json.load(f)

            # 清空两个表格
            self.task_ui.tableWidget.setRowCount(0)
            self.tableWidget_2.setRowCount(0)

            for task in tasks:
                # 在两个表格中插入新行
                row = self.task_ui.tableWidget.rowCount()
                self.task_ui.tableWidget.insertRow(row)
                self.tableWidget_2.insertRow(row)

                # 设置任务名称
                name_item = QtWidgets.QTableWidgetItem(task["name"])
                name_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.task_ui.tableWidget.setItem(row, 0, name_item)
                self.tableWidget_2.setItem(row, 0, QtWidgets.QTableWidgetItem(task["name"]))  # 创建新对象避免引用问题

                # 设置任务时间
                time_item = QtWidgets.QTableWidgetItem(task["time"])
                time_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.task_ui.tableWidget.setItem(row, 1, time_item)
                self.tableWidget_2.setItem(row, 1, QtWidgets.QTableWidgetItem(task["time"]))

                # 设置专注次数
                count_item = QtWidgets.QTableWidgetItem(task["count"])
                count_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.task_ui.tableWidget.setItem(row, 2, count_item)
                self.tableWidget_2.setItem(row, 2, QtWidgets.QTableWidgetItem(task["count"]))

                # 为两个表格创建按钮
                self.create_task_buttons(row)

        except Exception as e:
            print(f"加载任务失败: {str(e)}")

    def create_task_buttons(self, row):
        """为任务行创建操作按钮（两个表格同步）"""
        # 为第一个表格创建按钮
        self._create_buttons_for_table(row, self.task_ui.tableWidget)

        # 为第二个表格创建按钮
        self._create_buttons_for_table(row, self.tableWidget_2)

    def _create_buttons_for_table(self, row, table):
        """为指定表格创建按钮"""
        Start_button = QtWidgets.QPushButton("开始")
        Start_button.setFixedSize(80, 30)
        Start_button.setStyleSheet("""
            QPushButton {
                background-color: #4fd1c5;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color:#4ac5b9;
            }
        """)

        delete_btn = QtWidgets.QPushButton("删除")
        delete_btn.setFixedSize(80, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        # 确保删除按钮操作同步两个表格
        delete_btn.clicked.connect(lambda _, r=row: self.delete_task(r))
        Start_button.clicked.connect(lambda _, r=row: self.start_task(r))

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(Start_button)
        layout.addWidget(delete_btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        container.setLayout(layout)

        table.setCellWidget(row, 3, container)

    def start_task(self, row):
        try:
            time_item = self.task_ui.tableWidget.item(row, 1)
            if time_item is not None:
                time_str = time_item.text()
                parts = time_str.split('小时')
                time_hour_int = int(parts[0])
                time_min_int = int(parts[1].replace('分钟', ''))
                time_s_complete = (time_hour_int * 60 + time_min_int) * 60

                print(f"开始任务，时间设置为: {time_s_complete}秒")
                self.Notice_info("Todo", "测试开始", f"即将开始 {time_s_complete}秒 的任务！")
                self.total_seconds += time_s_complete
                self.today_seconds += time_s_complete
                self.total_sessions += 1
                self.today_sessions += 1

                # 启动锁屏窗口

                # 获取脚本所在目录的绝对路径

                exe_path = r"dist\Lock_window_main.exe"
                run_as_admin(exe_path)
                # 使用完整路径启动

                # 直接调用exe，不需要"start"

                # 等待锁屏窗口初始化

                # 等待锁屏窗口初始化
                time.sleep(1)  # 等待1秒确保Socket服务器启动

                # 发送数据
                try:
                    if self.Lock:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(3)  # 设置3秒超时
                            s.connect(('localhost', 45028))
                            s.sendall(str(time_s_complete).encode())
                            print("时间数据发送成功")
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(3)  # 设置3秒超时
                            s.connect(('localhost', 45028))
                            s.sendall(b"Lock")
                            print("时间数据发送成功")
                    elif not self.Lock:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(3)  # 设置3秒超时
                            s.connect(('localhost', 45028))
                            s.sendall(str(time_s_complete).encode())
                            print("时间数据发送成功")
                except Exception as e:
                    print(f"发送数据失败: {e}")
                    self.Notice_info("错误", "连接失败", "无法连接到锁屏窗口")

        except Exception as e:
            print(f"开始任务时出错: {str(e)}")
            self.Notice_info("错误", "任务启动失败", str(e))

    def delete_task(self, row):
        """删除指定行的任务"""
        # 删除两个表格中的对应行
        self.task_ui.tableWidget.removeRow(row)
        self.tableWidget_2.removeRow(row)
        self.save_tasks_to_json()
        self.Notice_info("Todo", "成功！", "删除任务成功！")

        # 重新连接所有按钮（因为行号已改变）
        self.reconnect_all_buttons()

    def reconnect_all_buttons(self):
        """重新连接所有按钮的信号"""
        # 重新连接第一个表格的按钮
        for row in range(self.task_ui.tableWidget.rowCount()):
            self._reconnect_row_buttons(self.task_ui.tableWidget, row)

        # 重新连接第二个表格的按钮
        for row in range(self.tableWidget_2.rowCount()):
            self._reconnect_row_buttons(self.tableWidget_2, row)

    def _reconnect_row_buttons(self, table, row):
        """重新连接指定行按钮的信号"""
        cell_widget = table.cellWidget(row, 3)
        if cell_widget and cell_widget.layout():
            # 找到删除按钮并重新连接
            for i in range(cell_widget.layout().count()):
                widget = cell_widget.layout().itemAt(i).widget()
                if isinstance(widget, QtWidgets.QPushButton) and widget.text() == "删除":
                    # 断开旧连接
                    try:
                        widget.clicked.disconnect()
                    except:
                        pass
                    # 建立新连接
                    widget.clicked.connect(lambda _, r=row: self.delete_task(r))
            for i in range(cell_widget.layout().count()):
                widget = cell_widget.layout().itemAt(i).widget()
                if isinstance(widget, QtWidgets.QPushButton) and widget.text() == "开始":
                    # 断开旧连接
                    try:
                        widget.clicked.disconnect()
                    except:
                        pass
                    # 建立新连接
                    widget.clicked.connect(lambda _, r=row: self.start_task(r))

    def Open_Strict(self):
        try:

            if not self.Strict_Mode:

                print("updata")
                self.Strict_Mode = True
                self.Lock = True
                self.setting_ui.Open_Enable_Strict.setText("Close")
                self.setting_ui.Open_Enable_Strict.setStyleSheet("""
                    QPushButton#Open_Enable_Strict {
                        border-radius: 7px;
                        background-color: rgb(255, 74, 74);
                        font: 700 10pt "Microsoft YaHei UI";
                    }
                    QPushButton#Open_Enable_Strict:hover {
                        background-color: rgb(223, 65, 65);
                    }
                """)
                self.Notice_info("Todo", "注意", "开始严格模式成功！")
            elif self.Strict_Mode:

                self.setting_ui.Open_Enable_Strict.setText("Open")
                self.Strict_Mode = False
                self.Lock = False
                self.setting_ui.Open_Enable_Strict.setStyleSheet("""
                             QPushButton#Open_Enable_Strict {
                        border-radius: 7px;
                      background-color: rgb(79, 209, 197);

                        font: 700 10pt "Microsoft YaHei UI";
                    }
                    QPushButton#Open_Enable_Strict:hover {
                    background-color: rgb(72, 191, 179);
                    }""")
                self.Notice_info("Todo", "注意", "已经退出严格模式！")

        except Exception as e:
            print(f"写入JSON文件时出错: {str(e)}")
            # 可以在这里添加错误恢复逻辑

            # 可以在这里添加错误恢复逻辑

    def add_show(self):
        # 确保控件可见
        if not self.add_show_state:
            self.task_ui.Add.show()
            self.slide_in_animation(self.task_ui.Add, 400, -280, 471, 261, 400, 30, 471, 261)
            self.add_show_state = True
        elif self.add_show_state:
            self.slide_out_animation(self.task_ui.Add, 400, -280, 471, 261, 400, 30, 471, 261)
            self.add_show_state = False

    ######################################基本函数（动画类），与常用功能############################
    def Notice_info(self, title1, title2, content):
        # 确保通知控件可见并置于顶层
        self.Notice.show()
        self.Notice.raise_()

        # 获取主窗口宽度
        window_width = self.width()

        # 设置通知控件大小
        notice_width = 401
        notice_height = 91

        # 设置初始位置（屏幕右侧外部）
        start_x = window_width
        start_y = 20

        # 设置结束位置（屏幕右侧内部）
        end_x = window_width - notice_width - 20  # 保留20像素边距
        end_y = 20

        # 设置文本内容
        self.Title.setText(title2)
        self.First_title.setText(title1)
        self.contect.setText(content)

        # 先设置初始位置
        self.Notice.setGeometry(QRect(start_x, start_y, notice_width, notice_height))

        # 创建进入动画
        enter_anim = QPropertyAnimation(self.Notice, b"geometry")
        enter_anim.setDuration(500)
        enter_anim.setStartValue(QRect(start_x, start_y, notice_width, notice_height))
        enter_anim.setEndValue(QRect(end_x, end_y, notice_width, notice_height))
        enter_anim.setEasingCurve(QEasingCurve.OutExpo)

        # 创建退出动画
        exit_anim = QPropertyAnimation(self.Notice, b"geometry")
        exit_anim.setDuration(500)
        exit_anim.setStartValue(QRect(end_x, end_y, notice_width, notice_height))
        exit_anim.setEndValue(QRect(start_x, start_y, notice_width, notice_height))
        exit_anim.setEasingCurve(QEasingCurve.OutExpo)

        # 创建顺序动画组
        self.notice_anim_group = QSequentialAnimationGroup()
        self.notice_anim_group.addAnimation(enter_anim)
        self.notice_anim_group.addPause(1000)  # 暂停2秒
        self.notice_anim_group.addAnimation(exit_anim)

        # 动画完成后隐藏通知
        self.notice_anim_group.finished.connect(self.Notice.hide)

        # 启动动画
        self.notice_anim_group.start()

    def slide_out_animation(self, widget, x1, y1, w1, h1, x2, y2, w2, h2, duration=500):
        pos_anim = QPropertyAnimation(widget, b"geometry")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QRect(x2, y2, w2, h2))
        pos_anim.setEndValue(QRect(x1, y1, w1, h1))
        pos_anim.setEasingCurve(QEasingCurve.Type.OutExpo)

        # 创建透明度动画（增强效果）
        opacity_effect = QGraphicsOpacityEffect(widget)
        self.task_ui.Add.setGraphicsEffect(opacity_effect)
        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setDuration(400)  # 比位置动画稍快
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0)

        # 并行动画组
        anim_group = QParallelAnimationGroup(self)
        anim_group.addAnimation(pos_anim)
        anim_group.addAnimation(opacity_anim)

        # 动画完成后恢复样式

        anim_group.start()

    def slide_in_animation(self, widget, x1, y1, w1, h1, x2, y2, w2, h2, duration=500):
        pos_anim = QPropertyAnimation(widget, b"geometry")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(QRect(x1, y1, w1, h1, ))
        pos_anim.setEndValue(QRect(x2, y2, w2, h2))
        pos_anim.setEasingCurve(QEasingCurve.Type.OutExpo)

        # 创建透明度动画（增强效果）
        opacity_effect = QGraphicsOpacityEffect(widget)
        self.task_ui.Add.setGraphicsEffect(opacity_effect)
        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setDuration(400)  # 比位置动画稍快
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)

        # 并行动画组
        anim_group = QParallelAnimationGroup(self)
        anim_group.addAnimation(pos_anim)
        anim_group.addAnimation(opacity_anim)

        # 动画完成后恢复样式

        anim_group.start()

        # animation

    def update_info(self):
        self.update_config_json("Times", "Today_times", str(self.today_sessions))
        self.update_config_json("Times", "Total_time", str(self.total_seconds))
        self.update_config_json("Times", "Total_num", str(self.total_sessions))
        self.update_config_json("Times", "Today_num", str(self.today_seconds))
        self.label_17.setText(str(self.today_seconds) + "分钟")
        self.label_11.setText(str(self.today_sessions))
        self.label_14.setText(str(self.today_sessions))
        self.label_8.setText(str(self.total_sessions))
        self.label_9.setText(str(self.total_seconds) + "分钟")

        if self.Strict_Mode:
            self.update_setting_json("Strict_Mode", "strict_mode", "1")
        else:
            self.update_setting_json("Strict_Mode", "strict_mode", "0")

    def read_setting_json(self, section, key, default=None):
        """读取setting_info.json，使用直接文件名方式"""
        filename = 'setting_info.json'
        try:
            # 文件不存在时返回默认值
            if not os.path.exists(filename):
                return default

            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(section, {}).get(key, default)
        except Exception as e:
            print(f"读取setting_info.json失败: {str(e)}")
            return default

    def update_setting_json(self, section, key, value):
        """更新setting_info.json，使用直接文件名方式"""
        filename = 'setting_info.json'
        try:
            data = {}
            # 如果文件存在，读取现有数据
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print("setting_info.json损坏，将重置")
                    data = {}

            # 更新数据结构
            if section not in data:
                data[section] = {}
            data[section][key] = value

            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"更新setting_info.json失败: {str(e)}")

    # ======================================config===================================
    def read_config_json(self, section, key, default=None):
        """读取Config.json，使用直接文件名方式"""
        filename = 'Config.json'
        try:
            # 文件不存在时返回默认值
            if not os.path.exists(filename):
                return default

            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get(section, {}).get(key, default)
        except Exception as e:
            print(f"读取Config.json失败: {str(e)}")
            return default

    def update_config_json(self, section, key, value):
        """更新Config.json，使用直接文件名方式"""
        filename = 'Config.json'
        try:
            data = {}
            # 如果文件存在，读取现有数据
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print("Config.json损坏，将重置")
                    data = {}

            # 更新数据结构
            if section not in data:
                data[section] = {}
            data[section][key] = value

            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"更新Config.json失败: {str(e)}")
            return False

    def switch_page(self, item):
        """根据点击的列表项切换页面"""
        if item.text() == "Dashboard":
            self.stackedWidget.setCurrentIndex(0)
        elif item.text() == "Task":
            self.stackedWidget.setCurrentIndex(1)
        elif item.text() == "Focus Lock":
            self.stackedWidget.setCurrentIndex(2)
        elif item.text() == "Setting":
            self.stackedWidget.setCurrentIndex(3)


if __name__ == "__main__":
    try:
        # 确保使用正确的图形后端
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

        app = QApplication(sys.argv)
        myWin = Chemms_Todo()
        myWin.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback

        with open("error.log", "a") as f:
            f.write(f"{time.ctime()} Error: {e}\n{traceback.format_exc()}\n")
        sys.exit(1)