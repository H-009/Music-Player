import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor


# ======================
# 歌词 Label
# ======================
class LyricLabel(QLabel):
    def __init__(self, text="桌面歌词", parent=None):
        super().__init__(text, parent)

        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.setStyleSheet("color: white;")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)

# ======================
# 内部透明容器 Widget
# ======================
class LyricWidget(QWidget):
    def __init__(self, text="桌面歌词", parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = LyricLabel(text, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.addWidget(self.label)

# ======================
# 独立桌面歌词窗口（可拖动）
# ======================
class DesktopLyricWindow(QWidget):
    def __init__(self, text="空闲中"):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        # ✅ 关键：让窗口始终参与命中检测
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")

        self.lyric_widget = LyricWidget(text, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lyric_widget)

        self.setFixedSize(600, 150)
        self._drag_pos = None

    def set_text(self,text):
        self.lyric_widget.label.setText(text)

    def resizeEvent(self, event):
        self.lyric_widget.setGeometry(self.rect())
        super().resizeEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        super().enterEvent(event)

    def leaveEvent(self, event):
        # ✅ 回到 1px alpha，而不是完全透明
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None