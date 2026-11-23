from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import QObject, QTimer, QEvent
from PyQt5.QtGui import QFont


class HoverToolTip(QObject):
    def __init__(self, widget, text="", delay_ms=500):
        """
        初始化悬停提示工具

        Args:
            widget: 要添加提示的控件
            text: 提示文本内容，默认为空
            delay_ms: 鼠标悬停多少毫秒后显示提示，默认500毫秒（0.5秒）
        """
        super().__init__(widget)  # 父对象设为widget确保自动释放
        self.widget = widget
        self.tip_text = text
        self.delay_ms = delay_ms  # 改名为更清晰的 delay_ms（毫秒）

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # 单次触发
        self.timer.timeout.connect(self.show_tip)

        # 设置提示字体（可选）
        QToolTip.setFont(QFont("微软雅黑", 10))

        # 安装事件过滤器，监听鼠标进入/离开
        self.widget.installEventFilter(self)

    def setText(self, text):
        """设置提示文本内容"""
        self.tip_text = text

    def setDelay(self, delay_ms):
        """设置提示显示的延迟时间（毫秒）"""
        self.delay_ms = delay_ms

    def eventFilter(self, obj, event):
        if obj == self.widget:
            if event.type() == QEvent.Enter:  # 鼠标进入
                self.timer.start(self.delay_ms)  # 使用设置的延迟时间
            elif event.type() == QEvent.Leave:  # 鼠标离开
                self.timer.stop()  # 停止计时器
                QToolTip.hideText()  # 隐藏提示
        return super().eventFilter(obj, event)

    def show_tip(self):
        """显示提示文本"""
        if self.tip_text:
            # 提示位置：控件底部左侧（可按需调整）
            pos = self.widget.mapToGlobal(self.widget.rect().bottomLeft())
            QToolTip.showText(pos, self.tip_text, self.widget)