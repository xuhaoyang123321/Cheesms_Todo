import sys
from PySide6 import QtCore
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QConicalGradient, QFont, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication


class CountdownTimer(QWidget):
    """倒计时插件"""
    timeout = Signal()  # 倒计时结束信号

    def __init__(self, parent=None, total_seconds=300):
        super().__init__(parent)
        self._total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.is_running = False
        self.paused_time = 0  # 新增：记录暂停时已经过去的时间

        # 创建UI
        self.init_ui()

        # 初始化计时器
        self.elapsed_timer = QElapsedTimer()
        self.update_timer = QTimer(self)
        self.update_timer.setTimerType(Qt.PreciseTimer)
        self.update_timer.timeout.connect(self.update_time)

        # 初始显示并自动开始
        self.update_display()
        self.start()

    @property
    def total_seconds(self):
        return self._total_seconds

    @total_seconds.setter
    def total_seconds(self, value):
        if isinstance(value, (int, float)):
            self._total_seconds = value
            self.remaining_seconds = value
            self.update_display()
        else:
            raise ValueError("total_seconds must be a number")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 圆环进度条
        self.progress = RoundProgress(self)
        self.progress.setMinimumSize(200, 200)
        layout.addWidget(self.progress, 1, Qt.AlignCenter)

        # 暂停/继续按钮




    def start(self):
        if self.total_seconds <= 0:
            return

        if not self.is_running:
            self.elapsed_timer.start()
            self.update_timer.start(200)
            self.is_running = True


    def pause(self):
        if self.is_running:
            # 记录已经过去的时间
            self.paused_time = self.elapsed_timer.elapsed()
            self.update_timer.stop()
            self.is_running = False


    def resume(self):
        # 重新开始计时器，但总时间减去已经过去的时间
        remaining_msecs = max(0, self.total_seconds * 1000 - self.paused_time)
        self.remaining_seconds = round(remaining_msecs / 1000)

        self.elapsed_timer.restart()
        self.update_timer.start(200)
        self.is_running = True

        self.update_display()

    def update_time(self):
        elapsed_msecs = self.elapsed_timer.elapsed()
        remaining_msecs = max(0, self.total_seconds * 1000 - elapsed_msecs)

        new_seconds = round(remaining_msecs / 1000)
        if new_seconds != self.remaining_seconds:
            self.remaining_seconds = new_seconds
            self.update_display()

        if remaining_msecs <= 0:
            self.update_timer.stop()
            self.is_running = False
            self.timeout.emit()

    def update_display(self):
        if isinstance(self.total_seconds, (int, float)) and self.total_seconds > 0:
            progress = min(100, int(100 - (self.remaining_seconds / self.total_seconds * 100)))
            self.progress.set_persent(progress, animate=True)
        self.progress.set_remaining_time(self.remaining_seconds)

    def set_progress_colors(self, start_color, end_color):
        self.progress.set_colors(start_color, end_color)


class RoundProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._persent = 0
        self.target_persent = 0
        self.timer_text = "00:00:00"
        self.remaining_seconds = 0
        self.setMinimumSize(100, 100)

        self.color_start = QColor("#4fd1c5")
        self.color_end = QColor("#ffffff")

        self.animation = QPropertyAnimation(self, b"persent")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def set_colors(self, start_color, end_color):
        self.color_start = QColor(start_color) if isinstance(start_color, str) else start_color
        self.color_end = QColor(end_color) if isinstance(end_color, str) else end_color
        self.update()

    def set_persent(self, value, animate=False):
        self.target_persent = max(0, min(100, value))
        if animate:
            self.animation.stop()
            self.animation.setStartValue(self._persent)
            self.animation.setEndValue(self.target_persent)
            self.animation.start()
        else:
            self._persent = self.target_persent
            self.update()

    def set_remaining_time(self, seconds):
        self.remaining_seconds = seconds
        self.update_time_text()
        self.update()

    def update_time_text(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        self.timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        size = min(width, height)

        outer_rect = QtCore.QRectF(0, 0, size, size)
        inner_rect = QtCore.QRectF(10, 10, size - 20, size - 20)
        text_rect = QtCore.QRectF(10, 10, size - 20, size - 20)
        rotateAngle = 360 * self._persent / 100

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 30, 180)))
        painter.drawEllipse(outer_rect)

        # 绘制进度条背景
        painter.setPen(QPen(QColor(255, 255, 255, 30), 8))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(inner_rect)

        # 绘制进度条
        gradient = QConicalGradient(size / 2, size / 2, 90)
        gradient.setColorAt(0, self.color_start)
        gradient.setColorAt(1, self.color_end)

        pen = QPen()
        pen.setBrush(gradient)
        pen.setWidth(8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(inner_rect, (90 - 0) * 16, -rotateAngle * 16)

        # 绘制时间文本
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(int(size / 7))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(text_rect, Qt.AlignCenter, self.timer_text)

    def sizeHint(self):
        return QSize(200, 200)

    def get_persent_value(self):
        return self._persent

    def set_persent_value(self, value):
        self._persent = value
        self.update()

    persent = QtCore.Property(float, get_persent_value, set_persent_value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer = CountdownTimer(total_seconds=30)  # 测试30秒倒计时
    timer.timeout.connect(lambda: print("倒计时结束!"))
    timer.show()
    sys.exit(app.exec())