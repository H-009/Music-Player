from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QParallelAnimationGroup, QPoint, QSize
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QParallelAnimationGroup, QPoint, QSize
from PyQt5.QtCore import Qt, QTimer

# 抽屉控价
class DrawerHost:
    def __init__(self, parent_widget, drawer_widget, direction="bottom", margin=0):
        """
        抽屉组件，基于父控件内显示，但计算隐藏位置时使用自己的XY坐标

        Args:
            parent_widget: 父控件，抽屉显示在父控件内
            drawer_widget: 要作为抽屉的QWidget
            direction: 抽屉出现的方向 ("top", "bottom", "left", "right")
            margin: 距离父控件边缘的边距
        """
        self.parent = parent_widget
        self.drawer = drawer_widget
        self.drawer.setParent(parent_widget)  # 设置为父控件的子控件
        self.drawer.hide()

        # 记录抽屉的原始尺寸和位置
        self.original_rect = self.drawer.geometry()
        self.direction = direction
        self.margin = margin

        # 获取父控件的几何信息
        self.parent_rect = self.parent.geometry()

        # 获取抽屉的原始位置（相对于父控件）
        self.original_x = self.drawer.x()
        self.original_y = self.drawer.y()
        self.drawer_width = self.drawer.width()
        self.drawer_height = self.drawer.height()

        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.drawer)
        self.drawer.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)  # 初始透明

        # 创建动画组
        self.animation_group = QParallelAnimationGroup()

        # 位置动画
        self.position_animation = QPropertyAnimation(self.drawer, b"geometry")
        self.position_animation.setDuration(300)
        self.position_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(250)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.animation_group.addAnimation(self.position_animation)
        self.animation_group.addAnimation(self.opacity_animation)

        # 连接动画结束信号
        self.animation_group.finished.connect(self._on_animation_finished)

        # 初始化开始和结束位置
        self._calculate_positions()

        # 抽屉状态
        self.is_open = False

    def _calculate_positions(self):
        """计算抽屉的显示和隐藏位置，基于自己的XY坐标"""
        # 获取抽屉尺寸
        drawer_width = self.drawer_width
        drawer_height = self.drawer_height

        # 获取父控件尺寸
        parent_width = self.parent.width()
        parent_height = self.parent.height()

        # 使用抽屉的原始XY坐标
        x_pos = self.original_x
        y_pos = self.original_y

        # 根据方向计算位置
        if self.direction == "top":
            # 从上边滑入
            # 隐藏位置：在抽屉原始位置的上方
            self.hidden_rect = QRect(x_pos, -drawer_height, drawer_width, drawer_height)
            # 显示位置：在抽屉原始Y位置
            self.shown_rect = QRect(x_pos, y_pos, drawer_width, drawer_height)

        elif self.direction == "bottom":
            # 从下边滑入
            # 隐藏位置：在父控件的下方
            self.hidden_rect = QRect(x_pos, parent_height, drawer_width, drawer_height)
            # 显示位置：在抽屉原始Y位置
            target_y = y_pos
            if target_y + drawer_height > parent_height:
                target_y = parent_height - drawer_height - self.margin
            self.shown_rect = QRect(x_pos, target_y, drawer_width, drawer_height)

        elif self.direction == "left":
            # 从左边滑入
            # 隐藏位置：在抽屉原始位置的左侧
            self.hidden_rect = QRect(-drawer_width, y_pos, drawer_width, drawer_height)
            # 显示位置：在抽屉原始X位置
            self.shown_rect = QRect(x_pos, y_pos, drawer_width, drawer_height)

        elif self.direction == "right":
            # 从右边滑入
            # 隐藏位置：在父控件的右侧
            self.hidden_rect = QRect(parent_width, y_pos, drawer_width, drawer_height)
            # 显示位置：在抽屉原始X位置
            target_x = x_pos
            if target_x + drawer_width > parent_width:
                target_x = parent_width - drawer_width - self.margin
            self.shown_rect = QRect(target_x, y_pos, drawer_width, drawer_height)

        else:
            raise ValueError(f"Invalid direction: {self.direction}. Must be 'top', 'bottom', 'left', or 'right'")

    def _on_animation_finished(self):
        """动画完成后的处理"""
        if not self.is_open:
            # 关闭动画完成后隐藏抽屉
            self.drawer.hide()

    def toggle(self):
        """切换抽屉状态"""
        if self.is_open:
            self.close()
        else:
            self.open()

    def open(self):
        """打开抽屉"""
        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.stop()

        # 确保抽屉是可见的
        self.drawer.show()
        self.drawer.raise_()  # 提升到最上层

        # 重新计算位置（以防父控件尺寸变化）
        self._update_parent_rect()
        self._calculate_positions()

        # 设置位置动画
        self.position_animation.setStartValue(self.hidden_rect)
        self.position_animation.setEndValue(self.shown_rect)

        # 设置透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        # 开始动画
        self.animation_group.start()
        self.is_open = True

        # 返回动画组以便连接信号
        return self.animation_group

    def close(self, immediate=False):
        """关闭抽屉"""
        if immediate:
            # 立即关闭
            self.drawer.hide()
            self.opacity_effect.setOpacity(0.0)
            self.drawer.setGeometry(self.hidden_rect)
            self.is_open = False
            return None

        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.stop()

        # 设置位置动画
        self.position_animation.setStartValue(self.shown_rect)
        self.position_animation.setEndValue(self.hidden_rect)

        # 设置透明度动画
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)

        # 开始动画
        self.animation_group.start()
        self.is_open = False

        # 返回动画组以便连接信号
        return self.animation_group

    def _update_parent_rect(self):
        """更新父控件的几何信息"""
        self.parent_rect = self.parent.geometry()

    def set_position(self, x=None, y=None):
        """手动设置抽屉位置"""
        if x is not None:
            self.original_x = x
        if y is not None:
            self.original_y = y

        # 重新计算位置
        self._calculate_positions()

        # 如果当前是打开状态，移动到新位置
        if self.is_open:
            self.drawer.setGeometry(self.shown_rect)
        else:
            self.drawer.setGeometry(self.hidden_rect)

    def set_size(self, width=None, height=None):
        """设置抽屉大小"""
        if width is not None:
            self.drawer_width = width
        if height is not None:
            self.drawer_height = height

        self.drawer.resize(self.drawer_width, self.drawer_height)

        # 重新计算位置
        self._calculate_positions()

        # 更新到当前位置
        if self.is_open:
            self.drawer.setGeometry(self.shown_rect)
        else:
            self.drawer.setGeometry(self.hidden_rect)

    def set_direction(self, direction, margin=None):
        """改变抽屉方向"""
        if direction not in ["top", "bottom", "left", "right"]:
            raise ValueError(f"Invalid direction: {direction}")

        self.direction = direction
        if margin is not None:
            self.margin = margin

        # 重新计算位置
        self._calculate_positions()

        # 如果当前是打开状态，立即更新到新位置
        if self.is_open:
            self.drawer.setGeometry(self.shown_rect)

    def is_visible(self):
        """检查抽屉是否可见（包括正在动画中）"""
        return self.drawer.isVisible() or self.is_open

# 屏幕抽屉
class ScreenDrawerHost:
    def __init__(self, drawer_widget, direction="bottom", margin=0):
        """
        抽屉组件，不依赖父控件，只需要知道自己的位置和方向

        Args:
            drawer_widget: 要作为抽屉的QWidget
            direction: 抽屉出现的方向 ("top", "bottom", "left", "right")
            margin: 距离屏幕边缘的边距
        """
        self.drawer = drawer_widget
        self.drawer.hide()

        # 记录抽屉的原始尺寸和位置
        self.original_rect = self.drawer.geometry()
        self.direction = direction
        self.margin = margin

        # 计算屏幕尺寸
        screen = self.drawer.screen()  # 获取抽屉所在的屏幕
        if screen:
            self.screen_rect = screen.availableGeometry()
        else:
            # 如果没有屏幕对象，使用主屏幕
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            self.screen_rect = screen.availableGeometry()

        # 设置透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.drawer)
        self.drawer.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)  # 初始透明

        # 创建动画组
        self.animation_group = QParallelAnimationGroup()

        # 位置动画
        self.position_animation = QPropertyAnimation(self.drawer, b"geometry")
        self.position_animation.setDuration(300)
        self.position_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(250)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.animation_group.addAnimation(self.position_animation)
        self.animation_group.addAnimation(self.opacity_animation)

        # 连接动画结束信号
        self.animation_group.finished.connect(self._on_animation_finished)

        # 初始化开始和结束位置
        self._calculate_positions()

        # 抽屉状态
        self.is_open = False

        # 设置抽屉的窗口标志
        self.drawer.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def _calculate_positions(self):
        """计算抽屉的显示和隐藏位置"""
        # 获取抽屉尺寸
        drawer_width = self.drawer.width()
        drawer_height = self.drawer.height()

        # 根据方向计算位置
        if self.direction == "top":
            # 从上边滑入
            x_pos = self.original_rect.x()
            self.hidden_rect = QRect(x_pos, -drawer_height, drawer_width, drawer_height)
            self.shown_rect = QRect(x_pos, self.margin, drawer_width, drawer_height)

        elif self.direction == "bottom":
            # 从下边滑入
            x_pos = self.original_rect.x()
            screen_bottom = self.screen_rect.height()
            self.hidden_rect = QRect(x_pos, screen_bottom, drawer_width, drawer_height)
            self.shown_rect = QRect(x_pos, screen_bottom - drawer_height - self.margin, drawer_width, drawer_height)

        elif self.direction == "left":
            # 从左边滑入
            y_pos = self.original_rect.y()
            self.hidden_rect = QRect(-drawer_width, y_pos, drawer_width, drawer_height)
            self.shown_rect = QRect(self.margin, y_pos, drawer_width, drawer_height)

        elif self.direction == "right":
            # 从右边滑入
            y_pos = self.original_rect.y()
            screen_right = self.screen_rect.width()
            self.hidden_rect = QRect(screen_right, y_pos, drawer_width, drawer_height)
            self.shown_rect = QRect(screen_right - drawer_width - self.margin, y_pos, drawer_width, drawer_height)

        else:
            raise ValueError(f"Invalid direction: {self.direction}. Must be 'top', 'bottom', 'left', or 'right'")

    def _on_animation_finished(self):
        """动画完成后的处理"""
        if not self.is_open:
            # 关闭动画完成后隐藏抽屉
            self.drawer.hide()

    def toggle(self):
        """切换抽屉状态"""
        if self.is_open:
            self.close()
        else:
            self.open()

    def open(self):
        """打开抽屉"""
        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.stop()

        # 确保抽屉是可见的
        self.drawer.show()
        self.drawer.raise_()  # 提升到最上层

        # 重新计算位置（以防屏幕尺寸变化）
        self._calculate_positions()

        # 设置位置动画
        self.position_animation.setStartValue(self.hidden_rect)
        self.position_animation.setEndValue(self.shown_rect)

        # 设置透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        # 开始动画
        self.animation_group.start()
        self.is_open = True

        # 返回动画组以便连接信号
        return self.animation_group

    def close(self, immediate=False):
        """关闭抽屉"""
        if immediate:
            # 立即关闭
            self.drawer.hide()
            self.opacity_effect.setOpacity(0.0)
            self.drawer.setGeometry(self.hidden_rect)
            self.is_open = False
            return None

        if self.animation_group.state() == QParallelAnimationGroup.Running:
            self.animation_group.stop()

        # 设置位置动画
        self.position_animation.setStartValue(self.shown_rect)
        self.position_animation.setEndValue(self.hidden_rect)

        # 设置透明度动画
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)

        # 开始动画
        self.animation_group.start()
        self.is_open = False

        # 返回动画组以便连接信号
        return self.animation_group

    def set_position(self, x=None, y=None):
        """手动设置抽屉位置"""
        rect = self.drawer.geometry()
        if x is not None:
            rect.moveLeft(x)
        if y is not None:
            rect.moveTop(y)
        self.drawer.setGeometry(rect)

        # 重新计算位置
        self._calculate_positions()

        # 如果当前是打开状态，移动到新位置
        if self.is_open:
            self.drawer.setGeometry(self.shown_rect)

    def set_size(self, width=None, height=None):
        """设置抽屉大小"""
        if width is not None or height is not None:
            current_size = self.drawer.size()
            new_width = width if width is not None else current_size.width()
            new_height = height if height is not None else current_size.height()
            self.drawer.resize(new_width, new_height)

            # 重新计算位置
            self._calculate_positions()

            # 更新到当前位置
            if self.is_open:
                self.drawer.setGeometry(self.shown_rect)
            else:
                self.drawer.setGeometry(self.hidden_rect)

    def set_direction(self, direction, margin=None):
        """改变抽屉方向"""
        if direction not in ["top", "bottom", "left", "right"]:
            raise ValueError(f"Invalid direction: {direction}")

        self.direction = direction
        if margin is not None:
            self.margin = margin

        # 重新计算位置
        self._calculate_positions()

        # 如果当前是打开状态，立即更新到新位置
        if self.is_open:
            self.drawer.setGeometry(self.shown_rect)

    def is_visible(self):
        """检查抽屉是否可见（包括正在动画中）"""
        return self.drawer.isVisible() or self.is_open
