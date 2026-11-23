import sys

from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
from PyQt5.QtWidgets import QWidget, QApplication


class SwitchButton(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, color,parent=None):
        super().__init__(parent)
        # 默认配置
        self._on = False
        self._animation_duration = 100
        self._bg_radius = 15
        self._slider_radius = 15
        self._slider_margin = 2

        # 颜色配置

        self._bg_color_off = QColor(255, 255, 255,50)
        self._bg_color_on = self.string_to_qcolor(color)
        self._current_bg_color = self._bg_color_off
        self._slider_color = QColor(255, 255, 255)

        # 初始化UI
        self.setFixedSize(60, 30)
        self._slider_pos = 0
        self._init_animations()

    def _init_animations(self):
        # 滑块位置动画
        self._pos_anim = QPropertyAnimation(self, b"sliderPosition")
        self._pos_anim.setDuration(self._animation_duration)
        self._pos_anim.finished.connect(self._animation_finished)

        # 背景颜色动画
        self._color_anim = QPropertyAnimation(self, b"backgroundColor")
        self._color_anim.setDuration(self._animation_duration)

    def string_to_qcolor(self,rgb_str):
        rgb_str = rgb_str.replace(" ", "")  # 去掉所有空格
        r, g, b = map(int, rgb_str.split(','))
        return QColor(r, g, b)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        bg_rect = self.rect()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._current_bg_color))
        p.drawRoundedRect(bg_rect, self._bg_radius, self._bg_radius)

        # 绘制滑块
        slider_size = self.height() - 2 * self._slider_margin
        slider_rect = QRect(self._slider_pos, self._slider_margin,
                            slider_size, slider_size)
        p.setBrush(QBrush(self._slider_color))
        p.drawRoundedRect(slider_rect, self._slider_radius, self._slider_radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()

    def toggle(self, animate=True):
        if animate:
            self._start_animations()
        else:
            self._on = not self._on
            self._update_slider_position()
            self._update_background_color()
            self.toggled.emit(self._on)

    def _start_animations(self):
        # 停止所有动画
        self._pos_anim.stop()
        self._color_anim.stop()

        # 设置滑块位置动画
        end_pos = self.width() - self.height() + self._slider_margin if not self._on else 0
        self._pos_anim.setStartValue(self._slider_pos)
        self._pos_anim.setEndValue(end_pos)

        # 设置背景颜色动画
        end_color = self._bg_color_on if not self._on else self._bg_color_off
        self._color_anim.setStartValue(self._current_bg_color)
        self._color_anim.setEndValue(end_color)

        # 启动动画
        self._pos_anim.start()
        self._color_anim.start()

    def _animation_finished(self):
        self._on = not self._on
        self.toggled.emit(self._on)
        self.update()

    def _update_slider_position(self):
        self._slider_pos = self.width() - self.height() + self._slider_margin if self._on else 0
        self.update()

    def _update_background_color(self):
        self._current_bg_color = self._bg_color_on if self._on else self._bg_color_off
        self.update()

    @pyqtProperty(int)
    def sliderPosition(self):
        return self._slider_pos

    @sliderPosition.setter
    def sliderPosition(self, pos):
        self._slider_pos = pos
        self.update()

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._current_bg_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._current_bg_color = color
        self.update()

    # 配置方法
    def setColors(self, on_bg=None, off_bg=None, slider=None, text=None):
        if on_bg: self._bg_color_on = QColor(on_bg)
        if off_bg: self._bg_color_off = QColor(off_bg)
        if slider: self._slider_color = QColor(slider)
        self.update()

    def setDuration(self, ms):
        self._animation_duration = ms
        self._anim.setDuration(ms)

    def isOn(self):
        return self._on

    def setOn(self, state, animate=True):
        if self._on != state:
            self.toggle(animate)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    switch = SwitchButton("30,200,150")
    switch.toggled.connect(lambda s: print(s))
    switch.show()
    sys.exit(app.exec())
