from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QLineEdit, QMessageBox)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIntValidator


class CountdownTimer(QWidget):
    """美化版倒计时定时器（支持外部信号）"""
    finished = pyqtSignal()  # 倒计时结束信号（可在外部连接）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_seconds = 1800  # 默认30分钟（1800秒）
        self.setup_ui()
        self.setup_style()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.update_display()

    def setup_ui(self):
        """初始化界面组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 大号时间显示
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 72, QFont.Bold))

        # 预设时间选择
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["10分钟", "30分钟", "50分钟", "90分钟", "180分钟", "自定义"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)

        # 自定义输入
        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText("倒计时(分钟)")
        self.custom_edit.setValidator(QIntValidator(1, 999))  # 只允许数字
        self.custom_edit.setVisible(False)

        # 控制按钮
        self.start_btn = QPushButton("▶ 开始")
        self.stop_btn = QPushButton("■ 停止")
        self.reset_btn = QPushButton("↻ 重置")

        # 按钮连接信号
        self.start_btn.clicked.connect(self.start_timer)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.reset_btn.clicked.connect(self.reset_timer)

        # 布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.preset_combo)
        control_layout.addWidget(self.custom_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addWidget(self.time_label)
        layout.addLayout(control_layout)
        layout.addLayout(btn_layout)

    def setup_style(self):
        """应用美化样式"""
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        self.setPalette(palette)

        # 按钮样式
        button_style = """
        QPushButton {
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 14px;
            min-width: 80px;
            background: #f0f0f0;
            border: 1px solid #d0d0d0;
        }
        QPushButton:hover {
            background: #e0e0e0;
        }
        QPushButton:pressed {
            background: #d0d0d0;
        }
        """
        self.setStyleSheet(button_style)

        # 时间标签特殊样式
        self.time_label.setStyleSheet("""
        QLabel {
            color: #2c3e50;
            margin: 20px 0;
        }
        """)

    def on_preset_changed(self, text):
        """处理预设时间变化"""
        if text == "自定义":
            self.custom_edit.setVisible(True)
            self.time_label.setText("00:00")
        else:
            self.custom_edit.setVisible(False)
            if text == "10分钟":
                self.total_seconds = 600
            elif text == "30分钟":
                self.total_seconds = 1800
            elif text == "50分钟":
                self.total_seconds = 3000
            elif text == "90分钟":
                self.total_seconds = 5400
            elif text == "180分钟":
                self.total_seconds = 10800
            self.update_display()

    def update_display(self):
        """更新显示的时间"""
        hours = self.total_seconds // 3600
        minutes = (self.total_seconds % 3600) // 60
        seconds = self.total_seconds % 60

        if hours > 0:
            display_text = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            display_text = f"{minutes:02d}:{seconds:02d}"
        self.time_label.setText(display_text)

    def start_timer(self):
        """启动倒计时"""
        if self.preset_combo.currentText() == "自定义":
            try:
                minutes = int(self.custom_edit.text())
                self.total_seconds = minutes * 60
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的分钟数")
                return

        if self.total_seconds > 0:
            self.timer.start(1000)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.reset_btn.setEnabled(False)

    def stop_timer(self):
        """暂停倒计时"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)

    def reset_timer(self):
        """重置倒计时"""
        self.stop_timer()
        self.on_preset_changed(self.preset_combo.currentText())

    def update_time(self):
        """每秒更新计时"""
        self.total_seconds -= 1
        self.update_display()

        if self.total_seconds <= 0:
            self.stop_timer()
            self.finished.emit()  # 发射信号给外部

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont

    app = QApplication([])

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 创建定时器实例
    timer = CountdownTimer()
    timer.setWindowTitle("精美倒计时器")
    timer.resize(450, 350)

    # ====== 外部信号处理示例 ======
    def external_handler():
        """外部自定义处理函数"""
        print("外部处理：倒计时已完成！")
        # 这里可以添加任何自定义逻辑
        # 例如：播放声音、发送通知、记录日志等

    # 连接信号到外部函数
    timer.finished.connect(external_handler)

    # 也可以使用lambda表达式
    timer.finished.connect(lambda: print("简洁写法：计时结束回调"))

    timer.show()
    app.exec()