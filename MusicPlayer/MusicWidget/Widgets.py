from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
from PyQt5.QtWidgets import QPushButton, QLabel

# 图像按钮
class ImageButton(QPushButton):
    def __init__(self, size=(50, 50), radius=5, parent=None):
        super().__init__(parent)

        self.radius = radius
        self.setFixedSize(*size)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
        """)

        # ===== 图片 =====
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setGeometry(0, 0, *size)

        # ===== 透明度效果 =====
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        self.opacity_effect = QGraphicsOpacityEffect(self.image_label)
        self.opacity_effect.setOpacity(1.0)
        self.image_label.setGraphicsEffect(self.opacity_effect)

        # ===== 动画 =====
        self.anim = QPropertyAnimation(
            self.opacity_effect, b"opacity", self
        )
        self.anim.setDuration(100)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

    # ---------- 图片切换 ----------
    def set_image(self, image_path):
        pixmap = QPixmap(image_path).scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        rounded = self.rounded_pixmap(pixmap, self.radius)
        self.image_label.setPixmap(rounded)

    # ---------- Hover ----------
    def enterEvent(self, event):
        self._start_opacity_anim(0.8)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._start_opacity_anim(1.0)
        super().leaveEvent(event)

    # ---------- Press ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_opacity_anim(0.7)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_opacity_anim(0.8)
        super().mouseReleaseEvent(event)

    # ---------- 动画封装 ----------
    def _start_opacity_anim(self, target):
        self.anim.stop()
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(target)
        self.anim.start()

    @staticmethod
    def rounded_pixmap(pixmap, radius):
        """生成圆角 QPixmap"""
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        path = QPainterPath()
        path.addRoundedRect(
            0, 0,
            pixmap.width(),
            pixmap.height(),
            radius,
            radius
        )

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded