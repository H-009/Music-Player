from PyQt5.QtWidgets import (QVBoxLayout, QPushButton,
                             QLabel, QHBoxLayout, QWidget)
from PyQt5.QtGui import QFont, QKeySequence, QColor
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize, QEventLoop,
                          pyqtProperty)
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtCore import QRect

class KeyDisplayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_color = QColor("#4CAF50")
        self._bg_color = QColor("#f8f9fa")
        self._border_color = QColor("#4CAF50")
        self.setup_ui()

    def get_text_color(self):
        return self._text_color

    def set_text_color(self, value):
        self._text_color = value
        self.update_style()

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, value):
        self._bg_color = value
        self.update_style()

    def get_border_color(self):
        return self._border_color

    def set_border_color(self, value):
        self._border_color = value
        self.update_style()

    text_color = pyqtProperty(QColor, get_text_color, set_text_color)
    bg_color = pyqtProperty(QColor, get_bg_color, set_bg_color)
    border_color = pyqtProperty(QColor, get_border_color, set_border_color)

    def setup_ui(self):
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(250, 45)
        self.setFont(QFont("Consolas", 12, QFont.Bold))
        self.update_style()

        self.geo_anim = QPropertyAnimation(self, b"geometry")
        self.geo_anim.setDuration(200)
        self.geo_anim.setEasingCurve(QEasingCurve.OutBack)

        self.text_anim = QPropertyAnimation(self, b"text_color")
        self.text_anim.setDuration(400)

        self.bg_anim = QPropertyAnimation(self, b"bg_color")
        self.bg_anim.setDuration(400)

        self.border_anim = QPropertyAnimation(self, b"border_color")
        self.border_anim.setDuration(400)

    def update_style(self):
        self.setStyleSheet(f"""
            QLabel {{
                color: {self._text_color.name()};
                border: 2px solid {self._border_color.name()};
                border-radius: 6px;
                padding: 10px;
                background-color: {self._bg_color.name()};
            }}
        """)

    def show_key(self, key_text):
        self.setText(key_text if key_text else "未设置")

        self.geo_anim.setStartValue(self.geometry().adjusted(5, 5, -5, -5))
        self.geo_anim.setEndValue(self.geometry())

        self.text_anim.setStartValue(QColor("#2196F3"))
        self.text_anim.setKeyValueAt(0.5, QColor("#FF5722"))
        self.text_anim.setEndValue(QColor("#4CAF50"))

        self.bg_anim.setStartValue(QColor("#e3f2fd"))
        self.bg_anim.setKeyValueAt(0.5, QColor("#fff8e1"))
        self.bg_anim.setEndValue(QColor("#f8f9fa"))

        self.border_anim.setStartValue(QColor("#2196F3"))
        self.border_anim.setKeyValueAt(0.5, QColor("#FFC107"))
        self.border_anim.setEndValue(QColor("#4CAF50"))

        self.geo_anim.start()
        self.text_anim.start()
        self.bg_anim.start()
        self.border_anim.start()


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None, border_color="#4CAF50"):
        super().__init__(text, parent)
        self._border_color = QColor(border_color)
        self._bg_color = QColor("#f8f9fa")
        self._text_color = QColor("#333333")
        self._scale = 1.0
        self.setup_ui()

    def get_border_color(self):
        return self._border_color

    def set_border_color(self, value):
        self._border_color = value
        self.update_style()

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, value):
        self._bg_color = value
        self.update_style()

    def get_text_color(self):
        return self._text_color

    def set_text_color(self, value):
        self._text_color = value
        self.update_style()

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.resize(int(90 * value), int(30 * value))

    border_color = pyqtProperty(QColor, get_border_color, set_border_color)
    bg_color = pyqtProperty(QColor, get_bg_color, set_bg_color)
    text_color = pyqtProperty(QColor, get_text_color, set_text_color)
    scale = pyqtProperty(float, get_scale, set_scale)

    def setup_ui(self):
        self.setFixedSize(90, 30)
        self.setFont(QFont("Microsoft YaHei", 9))

        self.hover_anim = QPropertyAnimation(self, b"text_color")
        self.hover_anim.setDuration(400)

        self.bg_anim = QPropertyAnimation(self, b"bg_color")
        self.bg_anim.setDuration(400)

        self.border_anim = QPropertyAnimation(self, b"border_color")
        self.border_anim.setDuration(400)

        self.click_anim = QPropertyAnimation(self, b"scale")
        self.click_anim.setDuration(600)
        self.click_anim.setEasingCurve(QEasingCurve.OutElastic)

        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                color: {self._text_color.name()};
                border: 2px solid {self._border_color.name()};
                border-radius: 6px;
                padding: 5px;
                background-color: {self._bg_color.name()};
            }}
            QPushButton:hover {{
                background-color: #e3f2fd;
            }}
            QPushButton:pressed {{
                background-color: #bbdefb;
            }}
        """)

    def enterEvent(self, event):
        self.hover_anim.setStartValue(QColor("#333333"))
        self.hover_anim.setKeyValueAt(0.5, QColor("#FF5722"))
        self.hover_anim.setEndValue(QColor("#4CAF50"))
        self.hover_anim.start()

        self.bg_anim.setStartValue(QColor("#f8f9fa"))
        self.bg_anim.setKeyValueAt(0.5, QColor("#fff8e1"))
        self.bg_anim.setEndValue(QColor("#e3f2fd"))
        self.bg_anim.start()

        self.border_anim.setStartValue(QColor("#4CAF50"))
        self.border_anim.setKeyValueAt(0.5, QColor("#FFC107"))
        self.border_anim.setEndValue(QColor("#2196F3"))
        self.border_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.setStartValue(QColor("#4CAF50"))
        self.hover_anim.setKeyValueAt(0.5, QColor("#FF5722"))
        self.hover_anim.setEndValue(QColor("#333333"))
        self.hover_anim.start()

        self.bg_anim.setStartValue(QColor("#e3f2fd"))
        self.bg_anim.setKeyValueAt(0.5, QColor("#fff8e1"))
        self.bg_anim.setEndValue(QColor("#f8f9fa"))
        self.bg_anim.start()

        self.border_anim.setStartValue(QColor("#2196F3"))
        self.border_anim.setKeyValueAt(0.5, QColor("#FFC107"))
        self.border_anim.setEndValue(QColor("#4CAF50"))
        self.border_anim.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.click_anim.setStartValue(1.0)
        self.click_anim.setKeyValueAt(0.5, 1.2)
        self.click_anim.setEndValue(1.0)
        self.click_anim.start()
        super().mousePressEvent(event)


class FramelessDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None
        self._opacity = 1.0
        self._scale = 0.9
        self.show_anim_group = None

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.resize(self.initial_size * value)

    opacity = pyqtProperty(float, get_opacity, set_opacity)
    scale = pyqtProperty(float, get_scale, set_scale)

    def showEvent(self, event):
        """ 重写showEvent，添加显示动画 """
        self.initial_size = QSize(self.width(), self.height())

        # 创建并行动画组
        self.show_anim_group = QParallelAnimationGroup(self)

        # 透明度动画 (淡入)
        opacity_anim = QPropertyAnimation(self, b"opacity")
        opacity_anim.setDuration(150)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.InQuad)

        self.show_anim_group.addAnimation(opacity_anim)
        self.show_anim_group.start()

        super().showEvent(event)

    def hideEvent(self, event):
        """ 隐藏窗口时执行淡出动画 """
        # 创建淡出动画
        opacity_anim = QPropertyAnimation(self, b"opacity")
        opacity_anim.setDuration(150)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(QEasingCurve.OutQuad)

        # 动画结束后隐藏窗口
        opacity_anim.finished.connect(self.hideAfterAnimation)

        self.hide_anim_group = QParallelAnimationGroup(self)
        self.hide_anim_group.addAnimation(opacity_anim)
        self.hide_anim_group.start()

        # 阻止默认的隐藏行为
        event.ignore()

    def hideAfterAnimation(self):
        """ 动画结束后真正隐藏窗口 """
        super().hide()

    def closeEvent(self, event):
        """ 关闭窗口时执行淡出动画 """
        self.hideEvent(event)
        event.ignore()


class KeyPressWidget(FramelessDialog):
    def __init__(self, app, label, color, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.setup_ui()
        self.app = app
        self.key_sequence = ""
        self.has_valid_key = False
        self._result = None  # To store the result
        self._closed = False  # To track if widget was closed

    def paintEvent(self, event):
        """ 重绘事件，绘制圆角窗口 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        # 绘制圆角矩形背景
        brush = QBrush(QColor(30, 200, 150))

        painter.setBrush(brush)
        painter.drawRoundedRect(QRect(0, 0, self.width(), self.height()), 10, 10)  # 10px圆角

        painter.end()

    def setup_ui(self):
        self.setFixedSize(350, 200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        font = QFont(self.label.font())

        # 标题栏
        title_bar = QLabel("选择热键", self)
        title_bar.setFont(font)
        title_bar.setAlignment(Qt.AlignCenter)
        title_bar.setStyleSheet(f"""
            QLabel {{
                padding: 8px;
                border-bottom: 1px solid {self.color};
            }}
        """)
        main_layout.addWidget(title_bar)

        self.key_label = KeyDisplayLabel(self)
        main_layout.addWidget(self.key_label, alignment=Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.ok_btn = AnimatedButton("确定", self, "#4CAF50")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setFont(font)
        self.ok_btn.setEnabled(False)
        self.ok_btn.setFocusPolicy(Qt.NoFocus)

        self.cancel_btn = AnimatedButton("取消", self, "#4CAF50")
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setFont(font)
        self.cancel_btn.setFocusPolicy(Qt.NoFocus)

        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setFocusPolicy(Qt.StrongFocus)

    def showEvent(self, event):
        """ 重写showEvent，确保动画执行 """
        super().showEvent(event)
        self.activateWindow()  # 确保窗口获得焦点
        self.setFocus()  # 设置焦点，以便接收键盘事件

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        modifiers = []
        for mod, name in [
            (Qt.ShiftModifier, "Shift"),
            (Qt.ControlModifier, "Ctrl"),
            (Qt.AltModifier, "Alt"),
            (Qt.MetaModifier, "Meta")
        ]:
            if event.modifiers() & mod:
                modifiers.append(name)

        key = ""
        if event.key() == Qt.Key_Space:
            key = "Space"
        elif event.key() not in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta]:
            key = QKeySequence(event.key()).toString(QKeySequence.NativeText)

        if not key and not modifiers:
            self.key_sequence = ""
            self.has_valid_key = False
        elif not key and modifiers:
            self.key_sequence = "+".join(modifiers)
            self.has_valid_key = False
        else:
            self.key_sequence = "+".join(modifiers + [key]) if modifiers else key
            self.has_valid_key = bool(key)

        self.key_label.show_key(self.key_sequence)
        self.ok_btn.setEnabled(self.has_valid_key)

    def accept(self):
        """确定按钮点击处理"""
        self._result = self.key_sequence
        if self._event_loop and self._event_loop.isRunning():
            self._event_loop.quit()  # 退出事件循环
        super().close()

    def close(self):
        """关闭窗口"""
        self._closed = True
        if self._event_loop and self._event_loop.isRunning():
            self._event_loop.quit()  # 退出事件循环
        super().close()

    def exec_(self):
        """模拟QDialog.exec_()行为"""
        self._result = None
        self._closed = False
        self.show()

        # 创建事件循环
        loop = QEventLoop()
        self._event_loop = loop  # 保存引用
        self.destroyed.connect(loop.quit)
        loop.exec_()
        self._event_loop = None  # 清除引用

        return self._result


def hot_key(app, label, color):
    try:
        widget = KeyPressWidget(app, label, color)
        result = widget.exec_()
        return result
    except Exception as a:
        print(a)