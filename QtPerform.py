import random

from PyQt5.QtCore import QObject, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget


class ColorAnimator(QObject):
    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget = widget
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def get_color(self) -> QColor:
        return self.widget.palette().color(self.widget.backgroundRole())

    def set_color(self, color: QColor):
        # 获取当前颜色的alpha值
        current_alpha = self.get_color().alpha()

        # 如果新颜色没有设置alpha（alpha=255），则使用当前alpha值
        if color.alpha() == 255:
            color.setAlpha(current_alpha)

        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), color)
        self.widget.setPalette(palette)
        self.widget.setAutoFillBackground(True)

    color = pyqtProperty(QColor, fget=get_color, fset=set_color)

    def fade_in_out(self, color: QColor = None, duration: int = 1000, alpha: int = None):
        """淡入淡出颜色动画（保留透明度）

        Args:
            color: 目标颜色，如果不传则使用随机颜色
            duration: 动画持续时间(毫秒)
            alpha: 指定透明度（0-255），如果不传则保持当前透明度
        """
        if color is None:
            # 生成随机颜色（保留透明度）
            current_alpha = self.get_color().alpha()
            color = QColor(random.randint(0, 255),
                           random.randint(0, 255),
                           random.randint(0, 255),
                           current_alpha if alpha is None else alpha)
        elif alpha is not None:
            # 如果指定了alpha参数，覆盖颜色的alpha值
            color.setAlpha(alpha)

        # 停止当前动画
        self.animation.stop()

        # 设置动画参数
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.get_color())
        self.animation.setEndValue(color)

        # 开始动画
        self.animation.start()

class HighlightAnimator(QObject):
    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget = widget
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._is_fading_out = True  # 标记当前是淡出还是淡入
        self._duration = 200  # 默认持续时间

    def get_color(self) -> QColor:
        return self.widget.palette().color(self.widget.backgroundRole())

    def set_color(self, color: QColor):
        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), color)
        self.widget.setPalette(palette)
        self.widget.setAutoFillBackground(True)

    color = pyqtProperty(QColor, fget=get_color, fset=set_color)

    def fade_in_out(self, duration: int = 200):
        """自动淡入淡出动画（透明度在0和255之间循环变化）

        Args:
            duration: 单次动画持续时间(毫秒)
        """
        self._duration = duration

        # 获取当前颜色
        current_color = self.get_color()

        # 创建目标颜色（根据当前状态决定是淡入还是淡出）
        target_color = QColor(current_color)
        if self._is_fading_out:
            target_color.setAlpha(0)  # 淡出到透明
        else:
            target_color.setAlpha(255)  # 淡入到不透明

        # 停止当前动画
        self.stop()  # 使用我们定义的stop方法

        # 设置动画参数
        self.animation.setDuration(self._duration)
        self.animation.setStartValue(current_color)
        self.animation.setEndValue(target_color)

        # 动画结束时切换状态并重新开始
        self.animation.finished.connect(self._toggle_fade_direction)

        # 开始动画
        self.animation.start()

    def _toggle_fade_direction(self):
        """切换淡入淡出方向"""
        self._is_fading_out = not self._is_fading_out
        self.animation.finished.disconnect(self._toggle_fade_direction)
        self.fade_in_out(self._duration)  # 使用相同的持续时间再次开始动画

    def stop(self):
        """停止淡入淡出动画"""
        self.animation.stop()
        try:
            self.animation.finished.disconnect(self._toggle_fade_direction)
        except TypeError:
            # 如果没有连接，忽略错误
            pass