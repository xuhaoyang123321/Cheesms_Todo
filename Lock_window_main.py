import os
import sys
import time
import subprocess
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from Lock_windows import Ui_MainWindow
import socket
class SocketServerThread(QThread):
    data_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.host = 'localhost'
        self.port = 45028

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 防止端口占用
                s.bind((self.host, self.port))
                s.listen()
                print(f"锁屏窗口Socket服务器已启动，监听 {self.host}:{self.port}")

                while True:
                    conn, addr = s.accept()
                    with conn:
                        print(f"接收到来自 {addr} 的连接")
                        data = conn.recv(1024).decode()
                        if data:
                            print(f"接收到数据: {data}")
                            self.data_received.emit(data)
        except Exception as e:
            print(f"Socket服务器错误: {e}")
class Chemms_Todo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("CheemsTodo - 专注模式")
        self.server_thread = SocketServerThread()
        self.server_thread.data_received.connect(self.handle_data_from_client)
        self.server_thread.start()
        self.Lock = False


        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.showFullScreen()
        self.timer_show.timeout.connect(self.on_timer_finished)

        # 连接退出按钮
        self.pushButton.clicked.connect(self.request_exit)  # 连接按钮点击信号

        # 禁用Alt+F4、Win键等系统快捷键
        self.setup_keyboard_hooks()

        # 可选：隐藏任务栏
        self.hide_taskbar()

        # 设置定时器检查窗口状态
        self.watchdog_timer = QtCore.QTimer(self)
        self.watchdog_timer.timeout.connect(self.ensure_fullscreen)
        self.watchdog_timer.start(1000)  # 每秒检查一次88

    def handle_data_from_client(self, data):
        print(f"[handle_data_from_client] 收到数据: {data}")  # 调试打印
        try:

            if data == "Lock":
                self.Lock = True

            else:
                self.time_toto = int(data)  # 尝试转换为整数
                print(f"转换后的倒计时时间: {self.time_toto}秒")

                # 设置倒计时时间并启动
                self.timer_show.total_seconds = self.time_toto
                self.timer_show.start()

        except ValueError as e:
            print(f"无效的倒计时数据: {data}, 错误: {e}")
            QMessageBox.warning(self, "错误", f"接收到无效的时间数据: {data}")

    def on_timer_finished(self):
        print("倒计时结束!")
        self.restore_system()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 45027))  # 连接主程序
            s.sendall(b"OK")  # 发送通知（二进制格式）
            print("通知已发送！")
        QApplication.quit()





    def setup_keyboard_hooks(self):
        """禁用系统快捷键"""
        try:
            if sys.platform == 'win32':
                import ctypes
                ctypes.windll.user32.BlockInput(True)
        except Exception as e:
            print(f"禁用快捷键失败: {e}")

    def hide_taskbar(self):
        """更安全的隐藏任务栏方法"""
        if sys.platform == 'win32':
            try:
                # 先尝试温柔地结束explorer
                subprocess.run(['taskkill', '/IM', 'explorer.exe', '/F'], timeout=5)
            except subprocess.TimeoutExpired:
                print("正常结束explorer超时，强制终止")
                subprocess.run(['taskkill', '/IM', 'explorer.exe', '/F'])
            except Exception as e:
                print(f"隐藏任务栏失败: {e}")

    def restore_taskbar(self):
        """恢复Windows任务栏"""
        if sys.platform == 'win32':
            try:
                subprocess.Popen('explorer.exe')
            except Exception as e:
                print(f"恢复任务栏失败: {e}")

    def ensure_fullscreen(self):
        """确保窗口保持全屏状态"""
        if not self.isFullScreen():
            self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def request_exit(self):
        """处理退出请求"""
        # 可以添加密码验证或其他确认机制
        if  not self.Lock :
            reply = QMessageBox.question(
                self, '确认退出',
                "您确定要退出专注模式吗?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.restore_system()
                QApplication.quit()
        elif  self.Lock:
            QMessageBox.warning(self, "警告", f"已开启严格模式或者处于锁机模式无法提前退出")


    def restore_system(self):
        """恢复系统设置"""
        self.restore_taskbar()
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.BlockInput(False)



if __name__ == "__main__":
    try:
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
        app = QApplication(sys.argv)
        myWin = Chemms_Todo()
        myWin.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback

        with open("error_Lock.log", "a") as f:
            f.write(f"{time.ctime()} Error: {e}\n{traceback.format_exc()}\n")

        # 确保即使崩溃也恢复系统状态
        if 'myWin' in locals():
            myWin.restore_system()
        sys.exit(1)