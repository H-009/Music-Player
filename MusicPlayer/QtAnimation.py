import re
from PyQt5.QtCore import (QEasingCurve, pyqtProperty,
                          Qt, QObject, QPoint, QParallelAnimationGroup, pyqtSlot, QTimer, QElapsedTimer, QPointF,
                          QTimeLine, QRegularExpression, QEvent, QPropertyAnimation, QSize)
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QCursor, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QScrollArea, QListWidget, QSlider, QStyledItemDelegate


# 按钮动画
class ButtonColorAnimator(QObject):
    def __init__(self, button):
        """
        按钮淡入淡出动画

        参数:
            button: 要应用动画效果的QPushButton
        """
        super().__init__()
        self.button = button

        # 从按钮的QSS中提取颜色和边框样式
        self._normal_color, self._hover_color, self._pressed_color, self._disabled_color = \
            self.extract_colors_from_qss(button)
        self._border_radius = self.extract_border_radius_from_qss(button)

        # 设置默认颜色(如果无法从QSS中提取)
        self._set_default_colors_if_needed()

        # 设置默认圆角半径(如果无法提取)
        if self._border_radius is None:
            self._border_radius = 4  # 默认圆角半径

        # 当前颜色和透明度状态
        self._current_color = self._normal_color
        self._current_opacity = 1.0  # 1.0表示完全不透明，0.0表示完全透明

        # 设置初始样式
        self.set_button_style()

        # 创建动画对象
        self._create_animations()

        # 初始化状态
        self._state = "normal"  # 可能的状态: normal, hover, pressed, disabled
        self._mouse_pressed_on_button = False

        # 保存原始事件处理程序并连接新事件
        self._save_and_connect_events()

    def _set_default_colors_if_needed(self):
        """如果无法从QSS中提取颜色，则设置默认颜色"""
        if self._normal_color is None:
            self._normal_color = QColor(52, 152, 219)  # 默认正常状态 - 蓝色
        if self._hover_color is None:
            self._hover_color = QColor(41, 128, 185)  # 默认悬停状态 - 深蓝色
        if self._pressed_color is None:
            print("无法从QSS中提取按下状态的颜色，使用默认颜色")
            self._pressed_color = QColor(28, 110, 164)  # 默认按下状态 - 更深的蓝色
        if self._disabled_color is None:
            print("无法从QSS中提取禁用状态的颜色，使用默认颜色")
            self._disabled_color = QColor(189, 195, 199)  # 默认禁用状态 - 浅灰色

    def _create_animations(self):
        """创建颜色和透明度动画对象"""
        # 创建颜色动画(用于非悬停状态)
        self.color_animation = QPropertyAnimation(self, b"currentColor")  # 淡出
        self.color_animation.setDuration(200)  # 200毫秒的动画持续时间
        self.color_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑的缓动曲线

        # 创建独立的悬停颜色动画(使用单独的持续时间)
        self._hover_color_animation = QPropertyAnimation(self, b"currentColor")  # 淡入
        self._hover_color_animation.setDuration(25)  # 使用独立的持续时间
        self._hover_color_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑的缓动曲线

        # 创建独立的按下颜色动画(使用单独的持续时间)
        self._pressed_color_animation = QPropertyAnimation(self, b"currentColor")  # 按下
        self._pressed_color_animation.setDuration(50)  # 默认150毫秒的动画持续时间
        self._pressed_color_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑的缓动曲线

        # 创建新的独立动画用于按下释放状态
        self._pressed_release_color_animation = QPropertyAnimation(self, b"currentColor") # 释放
        self._pressed_release_color_animation.setDuration(150)  # 使用150毫秒持续时间
        self._pressed_release_color_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑的缓动曲线

        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"currentOpacity")
        self.opacity_animation.setDuration(100)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def _save_and_connect_events(self):
        """保存原始事件处理程序并连接新的事件处理程序"""
        # 保存原始事件处理程序
        self._original_enter_event = self.button.enterEvent
        self._original_leave_event = self.button.leaveEvent
        self._original_press_event = self.button.mousePressEvent
        self._original_release_event = self.button.mouseReleaseEvent
        self._original_set_disabled = self.button.setEnabled  # 保存原始的setEnabled方法

        # 连接按钮事件到我们的处理程序
        self.button.enterEvent = self.handle_enter_event
        self.button.leaveEvent = self.handle_leave_event
        self.button.mousePressEvent = self.handle_press_event
        self.button.mouseReleaseEvent = self.handle_release_event

        # 覆盖setEnabled方法以处理禁用状态的颜色变化
        def wrapped_setEnabled(enabled):
            self._original_set_disabled(enabled)
            self.set_disabled_state(not enabled)

        self.button.setEnabled = wrapped_setEnabled

    def extract_border_radius_from_qss(self, button):
        """
        从按钮的QSS样式表中提取边框圆角半径

        参数:
            button: QPushButton对象

        返回:
            边框圆角半径(像素)，如果无法提取则返回None
        """
        qss = button.styleSheet()
        if not qss:
            return None

        # 定义正则表达式模式来匹配border-radius
        pattern = r'QPushButton\s*\{[^}]*border-radius\s*:\s*(\d+)px;'

        # 查找匹配项
        match = re.search(pattern, qss)
        if match:
            try:
                radius = int(match.group(1))
                return radius
            except ValueError:
                return None

        return None

    @pyqtProperty(QColor)
    def currentColor(self):
        """当前颜色的属性getter"""
        return self._current_color

    @currentColor.setter
    def currentColor(self, value):
        """当前颜色的属性setter"""
        self._current_color = value
        self.set_button_style()

    @pyqtProperty(float)
    def currentOpacity(self):
        """当前透明度的属性getter"""
        return self._current_opacity

    @currentOpacity.setter
    def currentOpacity(self, value):
        """当前透明度的属性setter"""
        self._current_opacity = value
        self.set_button_style()

    def set_button_style(self):
        """
        设置按钮的颜色和透明度样式

        通过样式表应用当前颜色和透明度，同时保持圆角半径不变
        不再在QSS中定义:hover、:pressed和:disabled状态的背景颜色，
        而是完全通过代码控制这些状态的颜色变化
        """
        # 将QColor转换为rgba字符串，结合当前透明度
        r, g, b, a = self._current_color.red(), self._current_color.green(), self._current_color.blue(), self._current_color.alpha()
        # 结合颜色本身的alpha和当前透明度
        combined_alpha = a / 255.0 * self._current_opacity
        rgba_str = f"rgba({r}, {g}, {b}, {combined_alpha})"

        # 构建新的QSS，只定义正常状态的背景颜色，其他状态的颜色由代码控制
        new_qss = f"""
        QPushButton {{
            background-color: {rgba_str};
            border-radius: {self._border_radius}px;
        }}
        """
        # 应用新的QSS
        self.button.setStyleSheet(new_qss)

    def rgba_to_string(self, color):
        """
        将QColor转换为rgba字符串

        参数:
            color: QColor对象

        返回:
            rgba格式的字符串，如果color为None则返回"transparent"
        """
        if color is None:
            return "transparent"
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        return f"rgba({r}, {g}, {b}, {a / 255.0})"

    def handle_enter_event(self, event):
        """
        处理鼠标进入事件

        修正: 在禁用状态下不处理任何状态变化或动画
        """
        if self._state == "disabled":
            # 如果按钮已禁用，直接传递事件，不做任何处理
            self._original_enter_event(event)
            return

        if not self._mouse_pressed_on_button and self._state != "disabled":
            if self._state != "hover":  # 只有状态变化时才触发动画
                self._state = "hover"
                # 使用独立的悬停颜色动画
                self.start_hover_color_animation(self._current_color, self._hover_color)
                # 确保透明度为1.0
                if self._current_opacity < 1.0:
                    self.start_opacity_animation(self._current_opacity, 1.0)
        self._original_enter_event(event)

    def handle_leave_event(self, event):
        """
        处理鼠标离开事件

        修正: 在禁用状态下不处理任何状态变化或动画
        """
        if self._state == "disabled":
            # 如果按钮已禁用，直接传递事件，不做任何处理
            self._original_leave_event(event)
            return

        if not self._mouse_pressed_on_button and self._state != "disabled":
            if self._state != "normal":
                self._state = "normal"
                # 离开时使用主颜色动画(保持一致性)
                self.start_color_animation(self._current_color, self._normal_color)
                # 确保透明度为1.0
                if self._current_opacity < 1.0:
                    self.start_opacity_animation(self._current_opacity, 1.0)
        self._original_leave_event(event)

    def handle_press_event(self, event):
        """
        处理鼠标按下事件

        修正: 在禁用状态下不处理任何状态变化或动画
        """
        if self._state == "disabled":
            # 如果按钮已禁用，直接传递事件，不做任何处理
            self._original_press_event(event)
            return

        if event.button() == Qt.LeftButton and self._state != "disabled":
            if self._state != "pressed":
                self._state = "pressed"
                self._mouse_pressed_on_button = True
                # 按下时使用专门的按下颜色动画
                self.start_pressed_color_animation(self._current_color, self._pressed_color)
                # 确保透明度为1.0
                if self._current_opacity < 1.0:
                    self.start_opacity_animation(self._current_opacity, 1.0)
        self._original_press_event(event)

    def handle_release_event(self, event):
        """
        处理鼠标释放事件

        修正: 在禁用状态下不处理任何状态变化或动画
        """
        if self._state == "disabled":
            # 如果按钮已禁用，直接传递事件，不做任何处理
            self._original_release_event(event)
            return

        if event.button() == Qt.LeftButton and self._state != "disabled":
            self._mouse_pressed_on_button = False
            if self.button.underMouse():
                if self._state != "hover":
                    # 从按下状态直接过渡到悬停状态
                    self._state = "hover"
                    # 使用独立的悬停颜色动画，但使用我们新增的按下释放动画持续时间
                    self._pressed_release_color_animation.stop()
                    self._pressed_release_color_animation.setStartValue(self._current_color)
                    self._pressed_release_color_animation.setEndValue(self._hover_color)
                    self._pressed_release_color_animation.start()

                    # 确保透明度为1.0
                    if self._current_opacity < 1.0:
                        self.start_opacity_animation(self._current_opacity, 1.0)
            else:
                if self._state != "normal":
                    # 从按下状态直接过渡到正常状态
                    self._state = "normal"
                    # 使用颜色动画，但使用我们新增的按下释放动画持续时间
                    self.color_animation.stop()
                    self.color_animation.setStartValue(self._current_color)
                    self.color_animation.setEndValue(self._normal_color)
                    self.color_animation.start()

                    # 确保透明度为1.0
                    if self._current_opacity < 1.0:
                        self.start_opacity_animation(self._current_opacity, 1.0)
        self._original_release_event(event)

    def set_disabled_state(self, disabled):
        """
        设置按钮的禁用状态并更新颜色
        """
        if disabled:
            self._state = "disabled"
            self.start_color_animation(self._current_color, self._disabled_color)
            # 确保透明度为1.0
            if self._current_opacity < 1.0:
                self.start_opacity_animation(self._current_opacity, 1.0)
        else:
            # 如果从禁用状态恢复，根据鼠标状态决定使用什么颜色
            if self._mouse_pressed_on_button:
                self._state = "pressed"
                self.start_pressed_color_animation(self._current_color, self._pressed_color)
            elif self.button.underMouse():
                self._state = "hover"
                self.start_hover_color_animation(self._current_color, self._hover_color)
            else:
                self._state = "normal"
                self.start_color_animation(self._current_color, self._normal_color)

            # 确保透明度为1.0
            if self._current_opacity < 1.0:
                self.start_opacity_animation(self._current_opacity, 1.0)

    def start_color_animation(self, start_color, end_color):
        """
        启动颜色动画(用于非悬停状态)

        参数:
            start_color: QColor, 动画开始颜色
            end_color: QColor, 动画结束颜色
        """
        self.color_animation.stop()
        self.color_animation.setStartValue(start_color)
        self.color_animation.setEndValue(end_color)
        self.color_animation.start()
        # 断开之前的finished信号连接，避免多次连接
        try:
            self.color_animation.finished.disconnect()
        except TypeError:
            pass  # 如果没有连接，忽略错误

    def start_hover_color_animation(self, start_color, end_color):
        """
        启动悬停状态的颜色动画(使用独立的持续时间)

        参数:
            start_color: QColor, 动画开始颜色
            end_color: QColor, 动画结束颜色
        """
        self._hover_color_animation.stop()
        self._hover_color_animation.setStartValue(start_color)
        self._hover_color_animation.setEndValue(end_color)
        self._hover_color_animation.start()
        # 断开之前的finished信号连接，避免多次连接
        try:
            self._hover_color_animation.finished.disconnect()
        except TypeError:
            pass  # 如果没有连接，忽略错误

    def start_pressed_color_animation(self, start_color, end_color):
        """
        启动按下状态的颜色动画(使用独立的持续时间)

        参数:
            start_color: QColor, 动画开始颜色
            end_color: QColor, 动画结束颜色
        """
        self._pressed_color_animation.stop()
        self._pressed_color_animation.setStartValue(start_color)
        self._pressed_color_animation.setEndValue(end_color)
        self._pressed_color_animation.start()
        # 断开之前的finished信号连接
        try:
            self._pressed_color_animation.finished.disconnect()
        except TypeError:
            pass  # 如果没有连接，忽略错误

    def start_opacity_animation(self, start_opacity, end_opacity):
        """
        启动透明度动画

        参数:
            start_opacity: float, 动画开始透明度(0.0-1.0)
            end_opacity: float, 动画结束透明度(0.0-1.0)
        """
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(start_opacity)
        self.opacity_animation.setEndValue(end_opacity)
        self.opacity_animation.start()
        # 断开之前的finished信号连接
        try:
            self.opacity_animation.finished.disconnect()
        except TypeError:
            pass  # 如果没有连接，忽略错误

    def extract_colors_from_qss(self, button):
        """
        从按钮的QSS样式表中提取颜色值

        参数:
            button: QPushButton对象

        返回:
            元组包含4个QColor对象:
            (normal_color, hover_color, pressed_color, disabled_color)
        """
        qss = button.styleSheet()
        if not qss:
            return None, None, None, None

        # 改进的正则表达式模式，更加灵活地匹配背景颜色
        # 特别改进了:pressed状态的匹配模式
        normal_pattern = r'QPushButton\s*\{[^}]*background(-color)?\s*:\s*([^;]+);'
        hover_pattern = r'QPushButton\s*:hover\s*\{[^}]*background(-color)?\s*:\s*([^;]+);'
        # 关键改进: 更灵活地匹配:pressed状态，考虑可能有多个冒号或::的情况
        pressed_pattern = r'QPushButton\s*(?::+|::)pressed\s*\{[^}]*background(-color)?\s*:\s*([^;]+);'
        disabled_pattern = r'QPushButton\s*:disabled\s*\{[^}]*background(-color)?\s*:\s*([^;]+);'

        # 查找匹配项
        normal_match = re.search(normal_pattern, qss)
        hover_match = re.search(hover_pattern, qss)
        pressed_match = re.search(pressed_pattern, qss)
        disabled_match = re.search(disabled_pattern, qss)

        # 提取颜色值
        def parse_color(color_str):
            """
            解析颜色字符串为QColor对象

            参数:
                color_str: 颜色字符串

            返回:
                QColor对象，如果无法解析则返回None
            """
            if not color_str:
                return None

            # 去除可能的空白字符
            color_str = color_str.strip()

            # 处理可能的rgb()或rgba()或#RRGGBB或#RRGGBBAA格式
            if color_str.startswith('rgba'):
                # rgba(r, g, b, a)格式
                values = re.findall(r'\d+\.?\d*', color_str)
                if len(values) >= 4:
                    return QColor(
                        int(float(values[0])),
                        int(float(values[1])),
                        int(float(values[2])),
                        int(float(values[3]) * 255)  # 将0-1的alpha转换为0-255
                    )
            elif color_str.startswith('rgb'):
                # rgb(r, g, b)格式
                values = re.findall(r'\d+\.?\d*', color_str)
                if len(values) >= 3:
                    if len(values) == 4:
                        # 非标准rgb格式，最后一个值作为alpha
                        return QColor(
                            int(values[0]),
                            int(values[1]),
                            int(values[2]),
                            int(float(values[3]) * 255)
                        )
                    else:
                        # 标准rgb格式
                        return QColor(
                            int(values[0]),
                            int(values[1]),
                            int(values[2])
                        )
            elif color_str.startswith('#'):
                # 处理#RRGGBB或#RRGGBBAA格式
                hex_color = color_str[1:]
                if len(hex_color) == 8:
                    # #RRGGBBAA格式
                    return QColor(
                        int(hex_color[0:2], 16),
                        int(hex_color[2:4], 16),
                        int(hex_color[4:6], 16),
                        int(hex_color[6:8], 16)
                    )
                elif len(hex_color) == 6:
                    # #RRGGBB格式
                    return QColor(
                        int(hex_color[0:2], 16),
                        int(hex_color[2:4], 16),
                        int(hex_color[4:6], 16)
                    )
            # 如果无法解析，返回None
            return None

        normal_color = parse_color(normal_match.group(2)) if normal_match else None
        hover_color = parse_color(hover_match.group(2)) if hover_match else None
        pressed_color = parse_color(pressed_match.group(2)) if pressed_match else None
        disabled_color = parse_color(disabled_match.group(2)) if disabled_match else None

        return normal_color, hover_color, pressed_color, disabled_color

    def restart_animator(self):
        """
        重新启动动画器，重新从按钮的QSS中提取颜色和样式
        用于在按钮样式动态改变后更新动画器的颜色配置
        """
        # 停止所有正在运行的动画
        self.color_animation.stop()
        self._hover_color_animation.stop()
        self._pressed_color_animation.stop()
        self._pressed_release_color_animation.stop()
        self.opacity_animation.stop()

        # 重新从按钮的QSS中提取颜色和边框样式
        self._normal_color, self._hover_color, self._pressed_color, self._disabled_color = \
            self.extract_colors_from_qss(self.button)
        self._border_radius = self.extract_border_radius_from_qss(self.button)

        # 设置默认颜色(如果无法从QSS中提取)
        self._set_default_colors_if_needed()

        # 设置默认圆角半径(如果无法提取)
        if self._border_radius is None:
            self._border_radius = 4  # 默认圆角半径

        # 重置当前颜色和状态
        self._current_color = self._normal_color
        self._current_opacity = 1.0

        # 根据当前状态设置正确的颜色
        if self._state == "disabled":
            self._current_color = self._disabled_color
        elif self._state == "hover":
            self._current_color = self._hover_color
        elif self._state == "pressed":
            self._current_color = self._pressed_color
        else:
            self._current_color = self._normal_color

        # 立即应用新的样式
        self.set_button_style()

# 按钮图标
class ButtonIconColorAnimator(QObject):
    def __init__(self, button):
        super().__init__()
        self.button = button

        # 初始化状态变量
        self._state = "normal"
        self._mouse_pressed_on_button = False
        self._current_opacity = 1.0
        self._current_darken_factor = 0.0

        # 动画状态跟踪
        self._pending_animation = None  # 待执行的动画状态
        self._animation_in_progress = False  # 动画是否正在进行中
        self._last_mouse_position = None  # 记录最后鼠标位置

        # 创建延迟状态检查定时器
        self._state_check_timer = QTimer()
        self._state_check_timer.setSingleShot(True)
        self._state_check_timer.timeout.connect(self._check_final_state)

        # 保存原始图标和样式
        self._original_icon = button.icon()
        self._original_style = button.styleSheet()

        # 创建动画对象
        self._create_animations()

        # 保存原始事件处理程序并连接新事件
        self._save_and_connect_events()

        # 设置初始样式
        self.update_button_appearance()

    def _create_animations(self):
        """创建动画对象"""
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"currentOpacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 创建变暗因子动画
        self.darken_animation = QPropertyAnimation(self, b"currentDarkenFactor")
        self.darken_animation.setDuration(150)
        self.darken_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 连接动画完成信号
        self.darken_animation.finished.connect(self._on_darken_animation_finished)
        self.opacity_animation.finished.connect(self._on_opacity_animation_finished)

    def _on_darken_animation_finished(self):
        """变暗动画完成后的处理"""
        self._animation_in_progress = False

        # 动画完成后检查最终状态
        self._state_check_timer.start(50)  # 50ms后检查最终状态

        # 检查是否有待执行的动画
        if self._pending_animation is not None:
            target_state, target_darken = self._pending_animation
            self._pending_animation = None
            self._state = target_state
            self.start_darken_animation(target_darken)
        else:
            self.update_button_appearance()

    def _on_opacity_animation_finished(self):
        """透明度动画完成后的处理"""
        self.update_button_appearance()

    def _check_final_state(self):
        """检查并应用最终状态，确保状态同步"""
        # 如果鼠标不在按钮上且没有按下，应该是normal状态
        if (not self._mouse_pressed_on_button and
                not self._is_mouse_over_button() and
                self._state != "normal"):
            self._state = "normal"
            target_darken = self.get_target_darken_factor()
            # 只有在当前值不同时才启动动画
            if abs(self._current_darken_factor - target_darken) > 0.01:
                self.start_darken_animation(target_darken)

    def _is_mouse_over_button(self):
        """更可靠的鼠标位置检测"""
        try:
            # 获取全局鼠标位置
            global_pos = QCursor.pos()
            # 转换到按钮的局部坐标
            local_pos = self.button.mapFromGlobal(global_pos)
            # 检查鼠标是否在按钮区域内
            return self.button.rect().contains(local_pos)
        except:
            # 如果出现异常，使用默认方法
            return self.button.underMouse()

    def _save_and_connect_events(self):
        """保存原始事件处理程序并连接新的事件处理程序"""
        # 保存原始事件处理程序
        self._original_enter_event = self.button.enterEvent
        self._original_leave_event = self.button.leaveEvent
        self._original_press_event = self.button.mousePressEvent
        self._original_release_event = self.button.mouseReleaseEvent
        self._original_set_disabled = self.button.setEnabled
        self._original_set_icon = self.button.setIcon

        # 连接按钮事件到我们的处理程序
        self.button.enterEvent = self.handle_enter_event
        self.button.leaveEvent = self.handle_leave_event
        self.button.mousePressEvent = self.handle_press_event
        self.button.mouseReleaseEvent = self.handle_release_event

        # 覆盖setEnabled方法
        def wrapped_setEnabled(enabled):
            self._original_set_disabled(enabled)
            self.set_disabled_state(not enabled)

        self.button.setEnabled = wrapped_setEnabled

        # 覆盖setIcon方法
        def wrapped_setIcon(icon):
            # 更新原始图标引用
            self._original_icon = icon
            self._original_set_icon(icon)
            # 立即更新外观
            self.update_button_appearance()

        self.button.setIcon = wrapped_setIcon

    @pyqtProperty(float)
    def currentOpacity(self):
        return self._current_opacity

    @currentOpacity.setter
    def currentOpacity(self, value):
        self._current_opacity = max(0.0, min(1.0, value))
        self.update_button_appearance()

    @pyqtProperty(float)
    def currentDarkenFactor(self):
        return self._current_darken_factor

    @currentDarkenFactor.setter
    def currentDarkenFactor(self, value):
        self._current_darken_factor = max(0.0, min(1.0, value))
        self.update_button_appearance()

    def update_button_appearance(self):
        """更新按钮的外观"""
        icon = self._original_icon
        if icon.isNull():
            self._original_set_icon(QIcon())
            return

        self.apply_icon_animation(icon)

    def apply_icon_animation(self, icon):
        """对图标应用动画效果"""
        icon_size = self.button.iconSize()
        if icon_size.isEmpty():
            icon_size = QSize(16, 16)

        try:
            pixmap = icon.pixmap(icon_size)
            if pixmap.isNull():
                pixmap = icon.pixmap(QSize(16, 16))
                if pixmap.isNull():
                    return

            # 应用变暗效果
            if self._current_darken_factor > 0:
                pixmap = self.darken_pixmap(pixmap, self._current_darken_factor)

            # 应用透明度效果
            if self._current_opacity < 1.0:
                pixmap = self.apply_opacity_to_pixmap(pixmap, self._current_opacity)

            new_icon = QIcon(pixmap)
            self._original_set_icon(new_icon)
            self.button.setIconSize(icon_size)

        except Exception as e:
            print(f"应用图标动画时出错: {e}")
            self._original_set_icon(icon)

    def get_target_darken_factor(self):
        """根据当前状态返回目标变暗因子"""
        if self._state == "disabled":
            return 0.6
        elif self._state == "pressed":
            return 0.3
        elif self._state == "hover":
            return 0.15
        else:
            return 0.0

    def start_darken_animation(self, target_darken_factor):
        """启动变暗因子动画 - 修复版本，避免动画中断"""
        # 如果目标值已经等于当前值，不需要启动动画
        if abs(self._current_darken_factor - target_darken_factor) < 0.01:
            return

        # 如果动画正在进行中，保存待执行的动画
        if self._animation_in_progress:
            self._pending_animation = (self._state, target_darken_factor)
            return

        self._animation_in_progress = True
        self.darken_animation.stop()
        self.darken_animation.setStartValue(self._current_darken_factor)
        self.darken_animation.setEndValue(target_darken_factor)
        self.darken_animation.start()

    def start_opacity_animation(self, target_opacity):
        """启动透明度动画"""
        if abs(self._current_opacity - target_opacity) < 0.01:
            return

        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self._current_opacity)
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.start()

    def handle_enter_event(self, event):
        """处理鼠标进入事件"""
        if self._state == "disabled":
            self._original_enter_event(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        # 如果当前是normal状态，才切换到hover状态
        if self._state == "normal" and not self._mouse_pressed_on_button:
            self._state = "hover"
            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            if self._current_opacity < 1.0:
                self.start_opacity_animation(1.0)

        self._original_enter_event(event)

    def handle_leave_event(self, event):
        """处理鼠标离开事件"""
        if self._state == "disabled":
            self._original_leave_event(event)
            return

        # 只有在hover或pressed状态且没有按下时才计划切换到normal状态
        if (self._state in ["hover", "pressed"] and
                not self._mouse_pressed_on_button):
            # 使用定时器延迟状态检查，避免快速移动时的状态抖动
            self._state_check_timer.start(10)  # 10ms后检查最终状态

        self._original_leave_event(event)

    def handle_press_event(self, event):
        """处理鼠标按下事件"""
        if self._state == "disabled":
            self._original_press_event(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        if event.button() == Qt.LeftButton:
            self._state = "pressed"
            self._mouse_pressed_on_button = True
            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            if self._current_opacity < 1.0:
                self.start_opacity_animation(1.0)

        self._original_press_event(event)

    def handle_release_event(self, event):
        """处理鼠标释放事件"""
        if self._state == "disabled":
            self._original_release_event(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        if event.button() == Qt.LeftButton:
            self._mouse_pressed_on_button = False

            # 立即检查鼠标位置来确定状态
            if self._is_mouse_over_button():
                self._state = "hover"
            else:
                self._state = "normal"

            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)

        self._original_release_event(event)

    def set_disabled_state(self, disabled):
        """设置按钮的禁用状态"""
        # 取消状态检查定时器
        self._state_check_timer.stop()

        if disabled:
            self._state = "disabled"
            self.start_darken_animation(0.6)
            self.start_opacity_animation(0.7)
        else:
            if self._is_mouse_over_button():
                self._state = "hover"
            else:
                self._state = "normal"

            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            self.start_opacity_animation(1.0)

    def darken_pixmap(self, pixmap, factor):
        """对QPixmap应用变暗效果"""
        if factor <= 0:
            return pixmap
        if factor >= 1.0:
            factor = 0.9

        image = pixmap.toImage()
        result_image = QImage(image.size(), QImage.Format_ARGB32_Premultiplied)

        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                if color.alpha() > 0:
                    r = int(color.red() * (1 - factor))
                    g = int(color.green() * (1 - factor))
                    b = int(color.blue() * (1 - factor))
                    a = color.alpha()

                    darkened_color = QColor(r, g, b, a)
                    result_image.setPixelColor(x, y, darkened_color)
                else:
                    result_image.setPixelColor(x, y, color)

        return QPixmap.fromImage(result_image)

    def apply_opacity_to_pixmap(self, pixmap, opacity):
        """对QPixmap应用透明度效果"""
        if opacity >= 1.0:
            return pixmap

        result_pixmap = QPixmap(pixmap.size())
        result_pixmap.fill(Qt.transparent)

        painter = QPainter(result_pixmap)
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result_pixmap

    def darken_hex_color(self, hex_color, factor):
        """对十六进制颜色应用变暗效果"""
        if factor == 0:
            return hex_color

        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return f"#{r:02x}{g:02x}{b:02x}"

    def lighten_hex_color(self, hex_color, factor):
        """对十六进制颜色应用变亮效果"""
        if factor == 0:
            return hex_color

        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _extract_base_color_from_style(self):
        """从原始样式中提取基础颜色"""
        if not self._original_style:
            return None

        patterns = [
            r'background-color:\s*([^;]+);',
            r'background:\s*([^;]+);',
            r'color:\s*([^;]+);'
        ]

        for pattern in patterns:
            match = re.search(pattern, self._original_style)
            if match:
                color_str = match.group(1).strip()
                if color_str.startswith(('#', 'rgb', 'rgba')):
                    return color_str
        return None

# 堆叠窗口动画
class StackedWidgetAnimator(QObject):
    """
    为QStackedWidget添加动画切换效果的封装类，优化了滚动区域显示问题
    支持快速响应动画：当快速连续切换时，会重置动画时间而不是直接停止动画，
    确保透明页面不会出现残留问题
    """

    def __init__(self, stacked_widget, time):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.animation_duration = time  # 动画持续时间(毫秒)
        self.current_animation = None  # 跟踪当前动画
        self.previous_index = -1  # 记录上一页索引
        self.pending_index = None  # 存储待处理的索引
        self.fast_response_enabled = True  # 是否启用快速响应模式

        # 保存原始的setCurrentIndex方法
        self._original_set_current_index = self.stacked_widget.setCurrentIndex

        # 替换为我们的动画版本
        self.stacked_widget.setCurrentIndex = self._animated_set_current_index

        # 滚动区域相关状态保存
        self._saved_hscroll_value = 0
        self._saved_vscroll_value = 0
        self._original_horizontal_policy = None
        self._original_vertical_policy = None

        # 用于跟踪当前活动的页面及其效果
        self.active_widgets_effects = {}  # 存储当前有动画效果的widget及其效果对象

    def _animated_set_current_index(self, index):
        """替换原始setCurrentIndex方法的实现，添加动画效果"""
        if index == self.stacked_widget.currentIndex():
            return

        # 如果启用了快速响应模式，并且有正在进行的动画
        if self.fast_response_enabled and self.current_animation is not None:
            # 重置动画时间而不是停止动画
            self.current_animation.setCurrentTime(0)
            self.current_animation = None

            # 清理所有活动的widget效果
            self._cleanup_active_widgets_effects()

            # 直接切换到目标索引，不执行动画
            # 注意：这里我们仍然执行动画，但通过重置时间来实现快速响应
            # 所以不需要直接调用_original_set_current_index
            # 而是继续执行动画逻辑
            direction = 'right' if index > self.stacked_widget.currentIndex() else 'left'

            # 确定动画方向后，执行动画
            self._perform_animation(index, direction)
            return

        # 如果没有启用快速响应模式或者没有正在进行的动画
        # 确定动画方向
        direction = 'right' if index > self.stacked_widget.currentIndex() else 'left'

        # 处理动画队列
        if self.current_animation is not None:
            if self.pending_index is None:
                self.pending_index = index
            return

        # 执行带动画的切换
        self._perform_animation(index, direction)

    def _cleanup_active_widgets_effects(self):
        """清理所有活动的widget效果，防止残留"""
        for widget, effect in self.active_widgets_effects.items():
            if widget and widget.graphicsEffect() == effect:
                widget.setGraphicsEffect(None)
        self.active_widgets_effects.clear()

    def _perform_animation(self, index, direction='right'):
        """执行实际的动画切换过程，优化滚动区域处理"""
        # 安全检查
        if not 0 <= index < self.stacked_widget.count():
            self._original_set_current_index(index)
            self._check_pending_index()
            return

        current_widget = self.stacked_widget.currentWidget()
        new_widget = self.stacked_widget.widget(index)

        if not current_widget or not new_widget:
            self._original_set_current_index(index)
            self._check_pending_index()
            return

        # 获取滚动区域并保存状态
        scroll_area = self._find_scroll_area()
        self._save_scroll_state(scroll_area)

        # 准备动画环境
        self._prepare_animation_environment(scroll_area, current_widget, new_widget)

        # 设置动画初始状态
        if direction == 'right':
            new_widget.move(self.stacked_widget.width(), 0)
        else:
            new_widget.move(-self.stacked_widget.width(), 0)

        # 透明度效果 - 使用字典跟踪效果对象以便后续清理
        new_opacity_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(new_opacity_effect)
        self.active_widgets_effects[new_widget] = new_opacity_effect
        new_opacity_effect.setOpacity(0.0)

        old_opacity_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(old_opacity_effect)
        self.active_widgets_effects[current_widget] = old_opacity_effect
        old_opacity_effect.setOpacity(1.0)

        # 创建位置动画
        new_pos_animation = QPropertyAnimation(new_widget, b"pos")
        new_pos_animation.setDuration(self.animation_duration)
        new_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        old_pos_animation = QPropertyAnimation(current_widget, b"pos")
        old_pos_animation.setDuration(self.animation_duration)
        old_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        if direction == 'right':
            new_pos_animation.setStartValue(QPoint(self.stacked_widget.width(), 0))
            new_pos_animation.setEndValue(QPoint(0, 0))
            old_pos_animation.setStartValue(QPoint(0, 0))
            old_pos_animation.setEndValue(QPoint(-self.stacked_widget.width(), 0))
        else:
            new_pos_animation.setStartValue(QPoint(-self.stacked_widget.width(), 0))
            new_pos_animation.setEndValue(QPoint(0, 0))
            old_pos_animation.setStartValue(QPoint(0, 0))
            old_pos_animation.setEndValue(QPoint(self.stacked_widget.width(), 0))

        # 透明度动画
        old_opacity_animation = QPropertyAnimation(old_opacity_effect, b"opacity")
        old_opacity_animation.setDuration(self.animation_duration)
        old_opacity_animation.setStartValue(1.0)
        old_opacity_animation.setEndValue(0.0)

        new_opacity_animation = QPropertyAnimation(new_opacity_effect, b"opacity")
        new_opacity_animation.setDuration(self.animation_duration)
        new_opacity_animation.setStartValue(0.0)
        new_opacity_animation.setEndValue(1.0)

        # 动画组
        main_animation_group = QParallelAnimationGroup()
        main_animation_group.addAnimation(new_pos_animation)
        main_animation_group.addAnimation(old_pos_animation)
        main_animation_group.addAnimation(new_opacity_animation)
        main_animation_group.addAnimation(old_opacity_animation)

        # 动画结束处理 - 添加清理效果的回调
        def animation_finished_callback():
            self._on_animation_finished(
                index, current_widget, new_widget, scroll_area
            )
            # 动画完成后从活动效果字典中移除
            if current_widget in self.active_widgets_effects:
                del self.active_widgets_effects[current_widget]
            if new_widget in self.active_widgets_effects:
                del self.active_widgets_effects[new_widget]

        main_animation_group.finished.connect(animation_finished_callback)

        self.current_animation = main_animation_group
        main_animation_group.start()

    def _find_scroll_area(self):
        """查找堆叠窗口所在的滚动区域"""
        parent = self.stacked_widget.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None

    def _save_scroll_state(self, scroll_area):
        """保存滚动区域的状态（滚动位置和滚动条策略）"""
        if scroll_area:
            # 保存滚动位置
            self._saved_hscroll_value = scroll_area.horizontalScrollBar().value()
            self._saved_vscroll_value = scroll_area.verticalScrollBar().value()

            # 保存滚动条策略
            self._original_horizontal_policy = scroll_area.horizontalScrollBarPolicy()
            self._original_vertical_policy = scroll_area.verticalScrollBarPolicy()

    def _prepare_animation_environment(self, scroll_area, current_widget, new_widget):
        """准备动画环境，优化滚动区域显示"""
        # 确保两个widget都有相同的大小
        new_widget.setFixedSize(current_widget.size())

        # 显示新页面并置于顶层
        new_widget.show()
        new_widget.raise_()

        # 处理滚动区域
        if scroll_area:
            # 禁用滚动条
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # 暂时固定滚动区域大小，防止动画期间尺寸变化
            scroll_area.setFixedSize(scroll_area.size())

            # 强制更新
            self._update_scroll_area(scroll_area)

    def _update_scroll_area(self, scroll_area):
        """增强滚动区域的更新机制"""
        if scroll_area:
            # 强制更新视口和布局
            scroll_area.viewport().update()
            scroll_area.updateGeometry()
            scroll_area.adjustSize()

            # 更新内容组件
            content_widget = scroll_area.widget()
            if content_widget:
                content_widget.updateGeometry()
                content_widget.adjustSize()
                # 如果有布局，强制更新布局
                layout = content_widget.layout()
                if layout:
                    layout.update()

    @pyqtSlot()
    def _on_animation_finished(self, index, current_widget, new_widget, scroll_area):
        """动画结束时的清理和恢复工作"""
        try:
            # 清理透明度效果 - 虽然已经在回调中移除了，但这里再次确保
            if current_widget and current_widget in self.active_widgets_effects:
                current_widget.setGraphicsEffect(None)
                del self.active_widgets_effects[current_widget]

            if new_widget and new_widget in self.active_widgets_effects:
                new_widget.setGraphicsEffect(None)
                del self.active_widgets_effects[new_widget]

            # 恢复原始位置（防止布局错乱）
            current_widget.move(0, 0)
            new_widget.move(0, 0)

            # 切换到目标索引
            self._original_set_current_index(index)
            self.previous_index = index

            # 恢复滚动区域状态
            if scroll_area:
                # 恢复滚动条策略
                scroll_area.setHorizontalScrollBarPolicy(self._original_horizontal_policy)
                scroll_area.setVerticalScrollBarPolicy(self._original_vertical_policy)

                # 恢复滚动位置
                scroll_area.horizontalScrollBar().setValue(self._saved_hscroll_value)
                scroll_area.verticalScrollBar().setValue(self._saved_vscroll_value)

                # 恢复大小限制
                scroll_area.setMinimumSize(0, 0)
                scroll_area.setMaximumSize(16777215, 16777215)  # Qt默认最大值

                # 强制更新
                self._update_scroll_area(scroll_area)

        except Exception as e:
            print(f"动画完成处理时出错: {e}")
        finally:
            # 重置动画状态并检查待处理索引
            self.current_animation = None
            self._check_pending_index()

    def _check_pending_index(self):
        """检查是否有待处理的索引，如果有则执行动画"""
        if self.pending_index is not None:
            pending_index = self.pending_index
            self.pending_index = None
            self._perform_animation(pending_index)

    def enable_fast_response(self, enabled=True):
        """
        启用或禁用快速响应模式
        :param enabled: True启用快速响应，False禁用
        """
        self.fast_response_enabled = enabled

# 滑动条动画
class SliderAnimator(QObject):
    """
    为QSlider添加动画效果的封装类

    支持:
    1. 滑动动画 - 当用户拖动滑块时平滑移动
    2. 值设置动画 - 当通过代码设置值时平滑过渡
    3. 快速响应 - 当快速连续设置值时，正确处理所有设置请求
    """

    def __init__(self, slider, animation_duration=200):
        """
        初始化滑块动画器

        参数:
            slider: 要应用动画效果的QSlider
            animation_duration: 动画持续时间(毫秒)，默认为200ms
        """
        super().__init__()
        self.slider = slider
        self.animation_duration = animation_duration  # 动画持续时间(毫秒)

        # 当前动画状态
        self.current_animation_timer = None  # 跟踪当前动画定时器
        self.pending_values = []  # 存储待处理的值设置请求队列
        self.fast_response_enabled = True  # 是否启用快速响应模式

        # 动画相关变量
        self.animation_start_value = 0
        self.animation_target_value = 0
        self.elapsed_timer = QElapsedTimer()  # 用于精确测量时间

        # 保存原始的setValue方法
        self._original_set_value = self.slider.setValue

        # 替换为我们的动画版本
        self.slider.setValue = self._animated_set_value

        # 初始化状态
        self._state = "idle"  # 可能的状态: idle, dragging, animating
        self._user_dragging = False  # 用户是否正在拖动滑块

        # 连接滑块事件
        self._save_and_connect_events()

    def _save_and_connect_events(self):
        """保存原始事件处理程序并连接新的事件处理程序"""
        # 保存原始事件处理程序
        self._original_slider_change_event = self.slider.valueChanged

        # 连接滑块值改变事件
        self.slider.valueChanged.connect(self.handle_value_changed)

        # 连接滑块滑动开始事件
        self.slider.sliderPressed.connect(self.handle_slider_pressed)

        # 连接滑块滑动结束事件
        self.slider.sliderReleased.connect(self.handle_slider_released)

    def handle_value_changed(self, value):
        """
        处理滑块值改变事件
        """
        # 这个信号会在用户拖动和程序设置值时都触发
        # 我们不需要在这里做任何特殊处理，因为动画逻辑在其他方法中处理
        pass

    def handle_slider_pressed(self):
        """
        处理滑块按下事件
        """
        self._user_dragging = True
        self._state = "dragging"
        # 用户开始拖动时，停止任何正在进行的动画
        if self.current_animation_timer is not None:
            self.current_animation_timer.stop()
            self.current_animation_timer = None

    def handle_slider_released(self):
        """
        处理滑块释放事件
        """
        self._user_dragging = False
        self._state = "idle"
        # 用户释放滑块后，如果有待处理的值设置请求，开始处理它们
        if self.pending_values and not self.current_animation_timer:
            self._process_next_pending_value()

    def _animated_set_value(self, value):
        """
        替换原始setValue方法的实现，添加动画效果
        """
        # 将请求的值添加到待处理队列
        if value not in self.pending_values:
            self.pending_values.append(value)

        # 如果用户正在拖动滑块，直接设置值而不使用动画
        if self._user_dragging:
            self._original_set_value(value)
            self._check_pending_values()
            return

        # 如果正在动画中且启用了快速响应
        if self.fast_response_enabled and self.current_animation_timer is not None:
            # 停止当前动画
            self.current_animation_timer.stop()
            self.current_animation_timer = None

            # 直接设置值(不使用动画)，但添加到队列以便后续可能的动画
            # 注意: 这里我们直接设置值，但仍然添加到队列
            # 这样当动画完成后，如果有新的值设置请求，可以继续动画
            self._original_set_value(value)
            self.pending_values.append(value)  # 将新值添加到队列
            self._check_pending_values()  # 立即处理队列
            return

        # 如果没有正在进行的动画，开始处理队列中的第一个值
        if self.current_animation_timer is None and self.pending_values:
            self._process_next_pending_value()

    def _process_next_pending_value(self):
        """
        处理队列中的下一个待处理值
        """
        if not self.pending_values:
            return

        # 获取队列中的第一个值
        next_value = self.pending_values.pop(0)

        # 执行带动画的值设置
        self._perform_value_animation(next_value)

    def _perform_value_animation(self, target_value):
        """
        执行实际的值动画过程，使用定时器逐步更新值
        """
        # 安全检查
        if not isinstance(target_value, int):
            self._original_set_value(target_value)
            self._check_pending_values()
            return

        current_value = self.slider.value()

        # 如果目标值和当前值相同，不需要动画
        if current_value == target_value:
            self._check_pending_values()
            return

        # 确定动画方向
        direction = 'up' if target_value > current_value else 'down'

        # 设置动画参数
        self.animation_start_value = current_value
        self.animation_target_value = target_value
        self.elapsed_timer.start()  # 记录动画开始时间

        # 创建并配置动画定时器
        self.current_animation_timer = QTimer(self)
        self.current_animation_timer.setInterval(16)  # 约60fps的更新间隔
        self.current_animation_timer.timeout.connect(self._animation_step)

        # 启动动画定时器
        self.current_animation_timer.start()

    def _animation_step(self):
        """
        动画的一步，逐步更新滑块值并发射sliderMoved信号
        """
        elapsed_time = self.elapsed_timer.elapsed()  # 获取自开始以来经过的时间(毫秒)

        if elapsed_time >= self.animation_duration:
            # 动画完成
            self._original_set_value(self.animation_target_value)
            self.slider.sliderReleased.emit()  # 发射释放信号
            self.current_animation_timer.stop()
            self.current_animation_timer = None
            self._check_pending_values()
            return

        # 计算动画进度(0.0到1.0)
        progress = elapsed_time / self.animation_duration

        # 使用缓动曲线计算插值因子
        easing_factor = self._ease_out_cubic(progress)
        current_value = self._interpolate_values(
            self.animation_start_value,
            self.animation_target_value,
            easing_factor
        )

        # 设置滑块值并发射信号
        int_value = int(current_value)
        self._original_set_value(int_value)
        self.slider.sliderMoved.emit(int_value)  # 发射当前值信号

    def enable_click_to_seek(self, slider: QSlider):
        """
        使滑动条支持点击跳转功能
        修改点：点击时发射sliderMoved信号
        """
        original_mouse_press = slider.mousePressEvent

        def custom_mouse_press(event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                # 计算点击位置对应的值
                if slider.orientation() == Qt.Horizontal:
                    ratio = event.pos().x() / slider.width()
                else:
                    ratio = (slider.height() - event.pos().y()) / slider.height()

                target_value = int(slider.minimum() + ratio * (slider.maximum() - slider.minimum()))

                # 设置值并发射信号
                slider.blockSignals(True)
                slider.setValue(target_value)
                slider.blockSignals(False)

                # 发射两个信号
                slider.valueChanged.emit(target_value)
                slider.sliderMoved.emit(target_value)  # 新增
                return

            original_mouse_press(event)

        slider.mousePressEvent = custom_mouse_press

    def _ease_out_cubic(self, t):
        """
        OutCubic缓动函数
        t: 0.0到1.0的进度值
        返回: 缓动后的进度值
        """
        return 1.0 - (1.0 - t) ** 3

    def _interpolate_values(self, start_value, end_value, factor):
        """
        在两个值之间进行插值

        参数:
            start_value: 起始值
            end_value: 结束值
            factor: 插值因子(0.0到1.0)

        返回: 插值后的值
        """
        return start_value + (end_value - start_value) * factor

    def _check_pending_values(self):
        """
        检查是否有待处理的值，如果有则执行动画
        """
        self._process_next_pending_value()

    def set_value_with_animation(self, value):
        """
        公开方法: 设置滑块值并使用动画效果

        参数:
            value: 要设置的滑块值
        """
        # 使用我们重写的setValue方法，它会自动处理动画
        self.slider.setValue(value)

    def enable_fast_response(self, enabled=True):
        """
        启用或禁用快速响应模式

        参数:
            enabled: True启用快速响应，False禁用
        """
        self.fast_response_enabled = enabled

    def set_animation_duration(self, duration):
        """
        设置动画持续时间

        参数:
            duration: 动画持续时间(毫秒)
        """
        self.animation_duration = duration

# 滚动区域 滚动条动画
class ElasticScrollAnimator(QObject):
    """
    为QScrollArea添加弹性滚动效果的封装类

    特性:
    1. 当用户滚动超过内容边界时，会产生弹性效果
    2. 快速滚动时会累积动量，实现惯性滚动
    3. 当释放滚动后，如果仍在边界外，会产生回弹动画
    4. 到达顶部或底部时有平滑的动画效果，不会出现无法滚动的情况
    5. 到达边界时不会继续同方向的滚动动画
    """

    def __init__(self, scroll_area):
        """
        初始化弹性滚动动画器

        参数:
            scroll_area: 要添加弹性滚动效果的QScrollArea
        """
        super().__init__()

        # 保存滚动画布引用
        self.scroll_area = scroll_area

        # 弹性滚动相关变量
        self._elastic_enabled = True  # 是否启用弹性效果
        self._momentum = QPointF(0, 0)  # 当前动量
        self._is_dragging = False  # 是否正在拖动
        self._is_animating = False  # 是否正在执行动画
        self._velocity = QPointF(0, 0)  # 当前速度
        self._last_pos = QPointF(0, 0)  # 上一次的位置
        self._last_time = 0  # 上一次的时间戳

        # 弹性参数
        self._elastic_factor = 0.05  # 弹性系数，控制回弹速度
        self._momentum_factor = 0.8  # 动量衰减因子
        self._drag_resistance = 0.9  # 拖动阻力，控制拖动时的减速

        # 动画定时器
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.setInterval(16)  # 约60fps

        # 使用QElapsedTimer来精确测量时间
        self._elapsed_timer = QElapsedTimer()
        self._elapsed_timer.start()

        # 初始化状态
        self._last_animation_time = 0

        # 给水平滚动条和垂直滚动条安装事件过滤器
        h_scroll = self.scroll_area.horizontalScrollBar()
        v_scroll = self.scroll_area.verticalScrollBar()

        if h_scroll:
            h_scroll.installEventFilter(self)
        if v_scroll:
            v_scroll.installEventFilter(self)

        # 连接滚动画布的事件
        self._connect_scroll_area_events()

    def _connect_scroll_area_events(self):
        """连接滚动画布的事件处理函数"""
        # 使用事件过滤器来接收鼠标事件
        self.scroll_area.viewport().installEventFilter(self)

        # 保存原始的wheelEvent方法
        if not hasattr(self.scroll_area, '_original_wheel_event'):
            self.scroll_area._original_wheel_event = self.scroll_area.wheelEvent

        # 重写滚轮事件处理
        self.scroll_area.wheelEvent = self._wrapped_wheel_event

    def _wrapped_wheel_event(self, event):
        """包装滚轮事件处理函数"""
        if not self._elastic_enabled:
            # 如果弹性效果禁用，调用原始的wheelEvent
            if hasattr(self.scroll_area, '_original_wheel_event'):
                self.scroll_area._original_wheel_event(event)
            else:
                # 如果没有保存原始方法，直接调用基类方法
                super(QScrollArea, self.scroll_area).wheelEvent(event)
            return

        # 获取滚轮增量
        delta = event.angleDelta().y() / 120  # 标准化滚轮增量

        # 应用滚轮增量到动量
        self._momentum.setY(self._momentum.y() - delta * 10)  # 调整系数以获得合适的滚动速度

        # 无论是否正在动画，都开始动画
        self._start_animation()

        # 接受事件，防止进一步传播
        event.accept()

    def _start_animation(self):
        """开始弹性动画"""
        if not self._is_animating:
            self._is_animating = True
            self._last_animation_time = self._elapsed_timer.elapsed()
            self._animation_timer.start()

    def _stop_animation(self):
        """停止弹性动画"""
        if self._is_animating:
            self._animation_timer.stop()
            self._is_animating = False

    def _animate(self):
        """执行弹性动画"""
        if not self._elastic_enabled:
            self._stop_animation()
            return

        # 计算时间增量(秒)
        current_time = self._elapsed_timer.elapsed()
        delta_time = (current_time - self._last_animation_time) / 1000.0  # 转换为秒
        self._last_animation_time = current_time

        # 如果时间增量过大，限制它以避免不稳定
        if delta_time > 0.1:
            delta_time = 0.1

        # 获取滚动条
        h_scroll = self.scroll_area.horizontalScrollBar()
        v_scroll = self.scroll_area.verticalScrollBar()

        # 应用动量到滚动条
        new_h_value = h_scroll.value() + self._momentum.x() * delta_time * 100
        new_v_value = v_scroll.value() + self._momentum.y() * delta_time * 100

        # 检查水平边界
        max_h = h_scroll.maximum()
        min_h = h_scroll.minimum()
        over_h = False

        if new_h_value > max_h:
            over_h = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_h_value = max_h
        elif new_h_value < min_h:
            over_h = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_h_value = min_h
        else:
            # 如果没有超过边界，水平动量衰减
            self._momentum.setX(self._momentum.x() * self._momentum_factor)
            if abs(self._momentum.x()) < 0.1:
                self._momentum.setX(0)

        # 改进垂直边界的处理 - 关键修改点
        max_v = v_scroll.maximum()
        min_v = v_scroll.minimum()
        over_v = False

        if new_v_value > max_v:
            over_v = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_v_value = max_v
        elif new_v_value < min_v:
            over_v = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_v_value = min_v
        else:
            # 如果没有超过边界，垂直动量衰减
            self._momentum.setY(self._momentum.y() * self._momentum_factor)
            if abs(self._momentum.y()) < 0.1:
                self._momentum.setY(0)

        # 设置新的滚动位置
        current_h_value = h_scroll.value()
        current_v_value = v_scroll.value()

        # 只有当值发生变化时才更新滚动条
        if new_h_value != current_h_value:
            h_scroll.setValue(int(new_h_value))
        if new_v_value != current_v_value:
            v_scroll.setValue(int(new_v_value))

        # 关键修改点：如果超过边界，继续动画以实现回弹效果
        # 但不再应用同方向的动量
        if over_h or over_v:
            # 当超过边界时，应用弹性效果
            # 这里我们不再修改new_h_value和new_v_value，因为已经在上面限制了
            # 而是让动画继续运行，通过动量衰减来实现回弹
            # 但由于我们已经限制了位置，所以实际上不会有同方向的动画
            # 只会有动量衰减导致的缓慢回弹
            pass
        elif not self._momentum.isNull():
            # 如果没有超过边界但有动量，继续动画
            pass
        else:
            # 如果没有动量且没有超过边界，停止动画
            self._stop_animation()

        # 新增：如果超过边界，施加一个轻微的反向力以实现回弹效果
        # 但不像之前那样直接反转动量
        if over_h or over_v:
            # 施加一个非常轻微的反向力，让滚动条缓慢回弹
            # 这个力足够小，不会导致明显的"弹回"效果，但足以让滚动条回到边界内
            if over_h: #禁用反向力 0.1
                self._momentum.setX(-self._momentum.x() * 0)  # 非常轻微的反向力
            if over_v:
                self._momentum.setY(-self._momentum.y() * 0)  # 非常轻微的反向力

    def setElasticEnabled(self, enabled):
        """设置是否启用弹性效果"""
        self._elastic_enabled = enabled
        if not enabled and self._is_animating:
            self._stop_animation()

    def setElasticFactor(self, factor):
        """设置弹性系数"""
        self._elastic_factor = factor

    def setMomentumFactor(self, factor):
        """设置动量衰减因子"""
        self._momentum_factor = factor

    def setDragResistance(self, resistance):
        """设置拖动阻力"""
        self._drag_resistance = resistance

    def eventFilter(self, obj, event):
        """事件过滤器，用于处理鼠标事件"""
        # 对于鼠标事件，我们不需要做任何特殊处理，因为QScrollArea已经处理了拖动
        # 我们只需要让事件继续传递
        return False

# 列表 滚动条动画
class ElasticListWidgetScrollAnimator(QObject):
    """
    为QListWidget添加弹性滚动效果的封装类

    特性:
    1. 当用户滚动超过内容边界时，会产生弹性效果
    2. 快速滚动时会累积动量，实现惯性滚动
    3. 当释放滚动后，如果仍在边界外，会产生回弹动画
    4. 到达顶部或底部时有平滑的动画效果，不会出现无法滚动的情况
    5. 到达边界时不会继续同方向的滚动动画
    """

    def __init__(self, ListWidget):
        """
        初始化弹性滚动动画器

        参数:
            scroll_area: 要添加弹性滚动效果的QScrollArea
        """
        super().__init__()

        # 保存引用
        self.scroll_area = ListWidget
        # 禁用自身的动画
        self.scroll_area.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.scroll_area.setHorizontalScrollMode(QListWidget.ScrollPerPixel)

        # 弹性滚动相关变量
        self._elastic_enabled = True  # 是否启用弹性效果
        self._momentum = QPointF(0, 0)  # 当前动量
        self._is_dragging = False  # 是否正在拖动
        self._is_animating = False  # 是否正在执行动画
        self._velocity = QPointF(0, 0)  # 当前速度
        self._last_pos = QPointF(0, 0)  # 上一次的位置
        self._last_time = 0  # 上一次的时间戳

        # 弹性参数
        self._elastic_factor = 0.05  # 弹性系数，控制回弹速度
        self._momentum_factor = 0.8  # 动量衰减因子
        self._drag_resistance = 0.9  # 拖动阻力，控制拖动时的减速

        # 动画定时器
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.setInterval(16)  # 约60fps

        # 使用QElapsedTimer来精确测量时间
        self._elapsed_timer = QElapsedTimer()
        self._elapsed_timer.start()

        # 初始化状态
        self._last_animation_time = 0

        # 连接滚动画布的事件
        self._connect_scroll_area_events()

    def _connect_scroll_area_events(self):
        """连接滚动画布的事件处理函数"""
        # 使用事件过滤器来接收鼠标事件
        self.scroll_area.viewport().installEventFilter(self)

        # 保存原始的wheelEvent方法
        if not hasattr(self.scroll_area, '_original_wheel_event'):
            self.scroll_area._original_wheel_event = self.scroll_area.wheelEvent

        # 重写滚轮事件处理
        self.scroll_area.wheelEvent = self._wrapped_wheel_event

    def _wrapped_wheel_event(self, event):
        """包装滚轮事件处理函数"""
        if not self._elastic_enabled:
            # 如果弹性效果禁用，调用原始的wheelEvent
            if hasattr(self.scroll_area, '_original_wheel_event'):
                self.scroll_area._original_wheel_event(event)
            else:
                # 如果没有保存原始方法，直接调用基类方法
                super(QScrollArea, self.scroll_area).wheelEvent(event)
            return

        # 获取滚轮增量
        delta = event.angleDelta().y() / 120  # 标准化滚轮增量

        # 应用滚轮增量到动量
        self._momentum.setY(self._momentum.y() - delta * 10)  # 调整系数以获得合适的滚动速度

        # 无论是否正在动画，都开始动画
        self._start_animation()

        # 接受事件，防止进一步传播
        event.accept()

    def _start_animation(self):
        """开始弹性动画"""
        if not self._is_animating:
            self._is_animating = True
            self._last_animation_time = self._elapsed_timer.elapsed()
            self._animation_timer.start()

    def _stop_animation(self):
        """停止弹性动画"""
        if self._is_animating:
            self._animation_timer.stop()
            self._is_animating = False

    def _animate(self):
        """执行弹性动画"""
        if not self._elastic_enabled:
            self._stop_animation()
            return

        # 计算时间增量(秒)
        current_time = self._elapsed_timer.elapsed()
        delta_time = (current_time - self._last_animation_time) / 1000.0  # 转换为秒
        self._last_animation_time = current_time

        # 如果时间增量过大，限制它以避免不稳定
        if delta_time > 0.1:
            delta_time = 0.1

        # 获取滚动条
        h_scroll = self.scroll_area.horizontalScrollBar()
        v_scroll = self.scroll_area.verticalScrollBar()

        # 应用动量到滚动条
        new_h_value = h_scroll.value() + self._momentum.x() * delta_time * 100
        new_v_value = v_scroll.value() + self._momentum.y() * delta_time * 100

        # 检查水平边界
        max_h = h_scroll.maximum()
        min_h = h_scroll.minimum()
        over_h = False

        if new_h_value > max_h:
            over_h = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_h_value = max_h
        elif new_h_value < min_h:
            over_h = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_h_value = min_h
        else:
            # 如果没有超过边界，水平动量衰减
            self._momentum.setX(self._momentum.x() * self._momentum_factor)
            if abs(self._momentum.x()) < 0.1:
                self._momentum.setX(0)

        # 改进垂直边界的处理 - 关键修改点
        max_v = v_scroll.maximum()
        min_v = v_scroll.minimum()
        over_v = False

        if new_v_value > max_v:
            over_v = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_v_value = max_v
        elif new_v_value < min_v:
            over_v = True
            # 关键修改点：到达边界时不继续同方向动画，直接限制在边界
            new_v_value = min_v
        else:
            # 如果没有超过边界，垂直动量衰减
            self._momentum.setY(self._momentum.y() * self._momentum_factor)
            if abs(self._momentum.y()) < 0.1:
                self._momentum.setY(0)

        # 设置新的滚动位置
        current_h_value = h_scroll.value()
        current_v_value = v_scroll.value()

        # 只有当值发生变化时才更新滚动条
        if new_h_value != current_h_value:
            h_scroll.setValue(int(new_h_value))
        if new_v_value != current_v_value:
            v_scroll.setValue(int(new_v_value))

        # 关键修改点：如果超过边界，继续动画以实现回弹效果
        # 但不再应用同方向的动量
        if over_h or over_v:
            # 当超过边界时，应用弹性效果
            # 这里我们不再修改new_h_value和new_v_value，因为已经在上面限制了
            # 而是让动画继续运行，通过动量衰减来实现回弹
            # 但由于我们已经限制了位置，所以实际上不会有同方向的动画
            # 只会有动量衰减导致的缓慢回弹
            pass
        elif not self._momentum.isNull():
            # 如果没有超过边界但有动量，继续动画
            pass
        else:
            # 如果没有动量且没有超过边界，停止动画
            self._stop_animation()

        # 新增：如果超过边界，施加一个轻微的反向力以实现回弹效果
        # 但不像之前那样直接反转动量
        if over_h or over_v:
            # 施加一个非常轻微的反向力，让滚动条缓慢回弹
            # 这个力足够小，不会导致明显的"弹回"效果，但足以让滚动条回到边界内
            if over_h: #禁用反向力
                self._momentum.setX(-self._momentum.x() * 0)  # 非常轻微的反向力
            if over_v:
                self._momentum.setY(-self._momentum.y() * 0)  # 非常轻微的反向力

    def setElasticEnabled(self, enabled):
        """设置是否启用弹性效果"""
        self._elastic_enabled = enabled
        if not enabled and self._is_animating:
            self._stop_animation()

    def setElasticFactor(self, factor):
        """设置弹性系数"""
        self._elastic_factor = factor

    def setMomentumFactor(self, factor):
        """设置动量衰减因子"""
        self._momentum_factor = factor

    def setDragResistance(self, resistance):
        """设置拖动阻力"""
        self._drag_resistance = resistance

    def eventFilter(self, obj, event):
        """事件过滤器，用于处理鼠标事件"""
        # 对于鼠标事件，我们不需要做任何特殊处理，因为QScrollArea已经处理了拖动
        # 我们只需要让事件继续传递
        return False

# 下拉列表动画
class ComboBoxAnimator(QObject):
    def __init__(self, combo_box):
        """
        QComboBox 悬停动画管理器（仅保留悬停淡入淡出，无点击动画）

        参数:
            combo_box: 要应用动画的 QComboBox 控件
            hover_in_duration: int, 悬停进入动画时长（毫秒），默认 150ms
            hover_out_duration: int, 悬停离开动画时长（毫秒），默认 250ms
        """
        super().__init__()
        self.combo_box = combo_box

        # 从 QSS 中尝试提取颜色和 border-radius
        self._normal_color, self._hover_color, _, self._disabled_color = \
            self.extract_colors_from_qss(combo_box)
        self._border_radius = self.extract_border_radius_from_qss(combo_box)

        # 若无法提取，则设置默认颜色
        self._set_default_colors_if_needed()

        # 若无法提取圆角，则设置默认圆角
        if self._border_radius is None:
            self._border_radius = 6  # 默认圆角

        # 当前颜色与透明度
        self._current_color = self._normal_color
        self._current_opacity = 1.0  # 1.0 = 不透明

        # 设置初始样式
        self.set_combo_style()

        # 创建动画对象（仅 hover 淡入淡出）
        self._create_hover_animations()

        # 初始状态
        self._state = "normal"  # normal, hover
        self._mouse_pressed_on_combo = False  # 保留但不再使用

        # 保存原始事件并绑定新事件（仅 enter / leave）
        self._save_and_connect_events()

    def _set_default_colors_if_needed(self):
        if self._normal_color is None:
            self._normal_color = QColor(52, 152, 219)  # 蓝色
        if self._hover_color is None:
            self._hover_color = QColor(41, 128, 185)  # 深蓝
        if self._disabled_color is None:
            self._disabled_color = QColor(189, 195, 199)  # 浅灰

    def _create_hover_animations(self):
        # 悬停进入动画（hover in）
        self.hover_in_animation = QPropertyAnimation(self, b"currentColor")
        self.hover_in_animation.setDuration(100)
        self.hover_in_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 悬停离开动画（hover out）
        self.hover_out_animation = QPropertyAnimation(self, b"currentColor")
        self.hover_out_animation.setDuration(150)
        self.hover_out_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 透明度动画（共用，也可单独设置）
        self.opacity_animation = QPropertyAnimation(self, b"currentOpacity")
        self.opacity_animation.setDuration(150)  # 可调
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def _save_and_connect_events(self):
        # 保存原始事件
        self._original_enter_event = self.combo_box.enterEvent
        self._original_leave_event = self.combo_box.leaveEvent

        # 绑定新事件
        self.combo_box.enterEvent = self.handle_enter_event
        self.combo_box.leaveEvent = self.handle_leave_event

    def extract_border_radius_from_qss(self, combo):
        qss = combo.styleSheet()
        if not qss:
            return None
        pattern = r'QComboBox\s*\{[^}]*border-radius\s*:\s*(\d+)px;'
        match = re.search(pattern, qss)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    def extract_colors_from_qss(self, combo):
        qss = combo.styleSheet()
        if not qss:
            return None, None, None, None

        def find_color(pattern):
            match = re.search(pattern, qss)
            if match:
                color_str = match.group(1).strip()
                return self.parse_color_string(color_str)
            return None

        normal_color = find_color(r'QComboBox\s*\{[^}]*background-color\s*:\s*([^;]+);')
        hover_color = find_color(r'QComboBox\s*:hover\s*\{[^}]*background-color\s*:\s*([^;]+);')
        disabled_color = find_color(r'QComboBox\s*:disabled\s*\{[^}]*background-color\s*:\s*([^;]+);')

        return normal_color, hover_color, None, disabled_color

    def parse_color_string(self, color_str):
        if not color_str:
            return None
        color_str = color_str.strip()
        if color_str.startswith('rgba'):
            values = re.findall(r'\d+\.?\d*', color_str)
            if len(values) >= 3:
                a = float(values[3]) if len(values) > 3 else 1.0
                return QColor(
                    int(float(values[0])),
                    int(float(values[1])),
                    int(float(values[2])),
                    int(a * 255)
                )
        elif color_str.startswith('rgb'):
            values = re.findall(r'\d+', color_str)
            if len(values) >= 3:
                return QColor(int(values[0]), int(values[1]), int(values[2]))
        elif color_str.startswith('#'):
            hex_color = color_str[1:]
            if len(hex_color) == 6:
                return QColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
            elif len(hex_color) == 8:
                return QColor(
                    int(hex_color[0:2], 16),
                    int(hex_color[2:4], 16),
                    int(hex_color[4:6], 16),
                    int(hex_color[6:8], 16)
                )
        return None

    @pyqtProperty(QColor)
    def currentColor(self):
        return self._current_color

    @currentColor.setter
    def currentColor(self, color):
        self._current_color = color
        self.set_combo_style()

    @pyqtProperty(float)
    def currentOpacity(self):
        return self._current_opacity

    @currentOpacity.setter
    def currentOpacity(self, opacity):
        self._current_opacity = opacity
        self.set_combo_style()

    def set_combo_style(self):
        r, g, b, a = self._current_color.red(), self._current_color.green(), self._current_color.blue(), self._current_color.alpha()
        combined_alpha = int((a / 255.0) * self._current_opacity * 255)
        rgba = f"rgba({r}, {g}, {b}, {combined_alpha / 255.0})"
        style = f"""
        QComboBox {{
            background-color: {rgba};
            border-radius: {self._border_radius}px;
        }}
        """
        self.combo_box.setStyleSheet(style)

    def handle_enter_event(self, event):
        if self._state == "disabled":
            self._original_enter_event(event)
            return
        if self._state != "hover":
            self._state = "hover"
            self.start_hover_in_animation()
        self._original_enter_event(event)

    def handle_leave_event(self, event):
        if self._state == "disabled":
            self._original_leave_event(event)
            return
        if self._state != "normal":
            self._state = "normal"
            self.start_hover_out_animation()
        self._original_leave_event(event)

    def start_hover_in_animation(self):
        # 悬停进入：切换到 hover 色
        self.hover_in_animation.stop()
        self.hover_in_animation.setStartValue(self._current_color)
        self.hover_in_animation.setEndValue(self._hover_color)
        self.hover_in_animation.start()

        # 可选：同时淡入透明度
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self._current_opacity)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def start_hover_out_animation(self):
        # 悬停离开：切换回 normal 色
        self.hover_out_animation.stop()
        self.hover_out_animation.setStartValue(self._current_color)
        self.hover_out_animation.setEndValue(self._normal_color)
        self.hover_out_animation.start()

        # 可选：同时淡入透明度
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self._current_opacity)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def restart_animator(self):
        """
        重新启动动画器，重新从QComboBox的QSS中提取颜色和样式
        用于在控件样式动态改变后更新动画器的颜色配置
        """
        # 停止所有正在运行的动画
        self.hover_in_animation.stop()
        self.hover_out_animation.stop()
        self.opacity_animation.stop()

        # 重新从QSS中提取颜色和边框样式
        self._normal_color, self._hover_color, _, self._disabled_color = \
            self.extract_colors_from_qss(self.combo_box)
        self._border_radius = self.extract_border_radius_from_qss(self.combo_box)

        # 设置默认颜色(如果无法从QSS中提取)
        self._set_default_colors_if_needed()

        # 设置默认圆角半径(如果无法提取)
        if self._border_radius is None:
            self._border_radius = 6  # 默认圆角半径

        # 重置当前颜色和状态
        self._current_color = self._normal_color
        self._current_opacity = 1.0

        # 根据当前状态设置正确的颜色
        if self._state == "hover":
            self._current_color = self._hover_color
        else:
            self._current_color = self._normal_color

        # 立即应用新的样式
        self.set_combo_style()


# 列表动画委托
class HoverDelegate(QStyledItemDelegate):
    """
    列表动画委托
    自定义修改原列表控件并添加动画
    """
    def __init__(self, animator):
        super().__init__(animator.list_widget)
        self.animator = animator

    def paint(self, painter, option, index):

        # 获取当前项的矩形区域
        rect = option.rect

        # 检查是否是悬停项或按下项
        is_hover = index.row() == self.animator.current_hover
        is_pressed = index.row() == self.animator.current_pressed

        # 绘制悬停效果
        if is_hover and self.animator.hoverOpacity > 0:
            hover_color = self.animator.hover_color
            hover_color.setAlphaF(0.2)
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(hover_color)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)  # 确保支持透明度
            painter.drawRoundedRect(rect, 5, 5)
            painter.restore()

        # 绘制按下效果
        if is_pressed and self.animator.pressedOpacity > 0:
            pressed_color = self.animator.pressed_color
            pressed_color.setAlphaF(0.3)
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(pressed_color)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawRoundedRect(rect, 5, 5)
            painter.restore()

        # 先调用父类绘制基本内容
        super().paint(painter, option, index)

# 列表项动画
class ListItemAnimator(QObject):
    """
    为现有的ListWidget
    添加列表委托并设置项动画
    悬停淡入动画 悬停淡出动画
    按下淡入动画 按下淡出动画
    可以改为自定义Item动画控件
    来代替修改
    """
    def __init__(self, list_widget):
        super().__init__(list_widget)
        self.list_widget = list_widget
        self.current_hover = -1
        self.current_pressed = -1

        # 使用属性动画控制透明度
        self._hover_opacity = 0.0
        self._pressed_opacity = 0.0

        # 设置默认颜色
        self.normal_color = QColor(68, 68, 68, 0)
        self.hover_color = QColor(78, 78, 78, 50)
        self.pressed_color = QColor(58, 58, 58, 50)

        # 从 QSS 中提取颜色
        self._extract_colors_from_qss()

        # 创建独立的动画
        self.hover_in_anim = self._create_animation("hoverOpacity", 250)  # 淡入动画100ms
        self.hover_out_anim = self._create_animation("hoverOpacity", 300)  # 淡出动画150ms
        self.press_in_anim = self._create_animation("pressedOpacity", 200)  # 按下动画50ms
        self.press_out_anim = self._create_animation("pressedOpacity", 250)  # 释放动画100ms

        # 使用更快的缓动曲线
        self.hover_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.hover_out_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.press_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.press_out_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # 设置事件过滤器
        self.list_widget.setMouseTracking(True)
        self.list_widget.viewport().installEventFilter(self)
        self.list_widget.setItemDelegate(HoverDelegate(self))

    def _create_animation(self, pyqtProperty_name, duration):
        """创建属性动画"""
        anim = QTimeLine(duration, self)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.valueChanged.connect(lambda v: setattr(self, pyqtProperty_name, v))
        return anim

    def _extract_colors_from_qss(self):
        """从 QSS 样式表中提取颜色"""
        qss = self.list_widget.styleSheet()
        if not qss:
            return

        # 修正后的正则表达式，匹配 QListWidget 而不是 QListView
        hover_re = QRegularExpression(
            r"QListWidget::item:hover\s*{[^}]*background(?:-color)?:\s*(rgba?\([^)]+\)|[^;}\s]+)[;\s}]"
        )
        pressed_re = QRegularExpression(
            r"QListWidget::item:selected\s*{[^}]*background(?:-color)?:\s*(rgba?\([^)]+\)|[^;}\s]+)[;\s}]"
        )
        normal_re = QRegularExpression(
            r"QListWidget::item\s*{[^}]*background(?:-color)?:\s*(rgba?\([^)]+\)|[^;}\s]+)[;\s}]"
        )

        # 提取悬停颜色
        match = hover_re.match(qss)
        if match.hasMatch():
            color_str = match.captured(1).strip()
            self.hover_color = self._parse_color(color_str, self.hover_color)

        # 提取按下/选中颜色
        match = pressed_re.match(qss)
        if match.hasMatch():
            color_str = match.captured(1).strip()
            self.pressed_color = self._parse_color(color_str, self.pressed_color)

        # 提取普通状态颜色
        match = normal_re.match(qss)
        if match.hasMatch():
            color_str = match.captured(1).strip()
            self.normal_color = self._parse_color(color_str, self.normal_color)

    def _parse_color(self, color_str, default):
        """改进的颜色解析方法，支持更多格式"""
        color_str = color_str.strip()

        # 处理 rgba() 格式
        if color_str.startswith("rgba("):
            try:
                parts = color_str[5:-1].split(',')
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                a = float(parts[3].strip()) * 255  # 将 0-1 的 alpha 转换为 0-255
                return QColor(r, g, b, int(a))
            except (ValueError, IndexError):
                return default

        # 处理 rgb() 格式
        elif color_str.startswith("rgb("):
            try:
                parts = color_str[4:-1].split(',')
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                return QColor(r, g, b)
            except (ValueError, IndexError):
                return default

        # 处理十六进制格式 (#RRGGBB 或 #RRGGBBAA)
        elif color_str.startswith("#"):
            if len(color_str) == 7:  # #RRGGBB
                return QColor(color_str)
            elif len(color_str) == 9:  # #RRGGBBAA
                return QColor(color_str)
            else:
                return default

        # 处理颜色名称 (如 "red", "blue")
        elif QColor.isValidColor(color_str):
            return QColor(color_str)

        return default

    @pyqtProperty(float)
    def hoverOpacity(self):
        return self._hover_opacity

    @hoverOpacity.setter
    def hoverOpacity(self, value):
        if self._hover_opacity != value:
            self._hover_opacity = value
            if self.current_hover >= 0:
                self.list_widget.viewport().update(
                    self.list_widget.visualItemRect(self.list_widget.item(self.current_hover))
                )

    @pyqtProperty(float)
    def pressedOpacity(self):
        return self._pressed_opacity

    @pressedOpacity.setter
    def pressedOpacity(self, value):
        if self._pressed_opacity != value:
            self._pressed_opacity = value
            if self.current_pressed >= 0:
                self.list_widget.viewport().update(
                    self.list_widget.visualItemRect(self.list_widget.item(self.current_pressed))
                )

    def eventFilter(self, source, event):
        if source is self.list_widget.viewport():
            if event.type() == QEvent.MouseMove:
                index = self.list_widget.indexAt(event.pos())
                self._handle_hover(index.row())
            elif event.type() == event.Leave:
                self._handle_hover(-1)
            elif event.type() == event.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    index = self.list_widget.indexAt(event.pos())
                    self._handle_press(index.row())
            elif event.type() == event.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self._handle_release()
        return super().eventFilter(source, event)

    def _handle_hover(self, row):
        """处理悬停状态变化"""
        if row == self.current_hover:
            return

        # 停止所有悬停动画
        self.hover_in_anim.stop()
        self.hover_out_anim.stop()

        # 更新当前悬停项
        prev_hover = self.current_hover
        self.current_hover = row

        # 启动适当的动画
        if row >= 0:
            # 立即开始淡入动画
            self.hover_in_anim.start()

            # 如果之前有悬停项，立即将其透明度设为0
            if prev_hover >= 0:
                self.hoverOpacity = 0.0
                self.list_widget.viewport().update(
                    self.list_widget.visualItemRect(self.list_widget.item(prev_hover))
                )
        else:
            # 开始淡出动画
            self.hover_out_anim.start()

    def _handle_press(self, row):
        """处理按下状态变化"""
        if row == self.current_pressed:
            return

        # 停止所有按下动画
        self.press_in_anim.stop()
        self.press_out_anim.stop()

        # 更新当前按下项
        self.current_pressed = row

        if row >= 0:
            # 立即开始按下动画
            self.press_in_anim.start()

    def _handle_release(self):
        """处理释放事件"""
        if self.current_pressed == -1:
            return

        # 停止所有按下动画
        self.press_in_anim.stop()
        self.press_out_anim.stop()

        # 开始释放动画
        self.press_out_anim.start()

        # 重置按下项
        self.current_pressed = -1

    def restart_animator(self):
        """
        重新启动动画器，重新从QSS中提取颜色配置
        用于在列表控件样式动态改变后更新动画器的颜色配置
        """
        # 停止所有正在运行的动画
        self.hover_in_anim.stop()
        self.hover_out_anim.stop()
        self.press_in_anim.stop()
        self.press_out_anim.stop()

        # 重置透明度状态
        self._hover_opacity = 0.0
        self._pressed_opacity = 0.0

        # 重新从QSS中提取颜色
        self._extract_colors_from_qss()

        # 重置当前状态
        self.current_hover = -1
        self.current_pressed = -1

        # 强制刷新视图
        self.list_widget.viewport().update()

# 堆叠窗口动画 上下方向
class StackedWidgetAnimatorUpDown(QObject):
    """
    为QStackedWidget添加上下滑动动画切换效果的封装类
    """

    def __init__(self, stacked_widget, time):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.animation_duration = time
        self.current_animation = None
        self.previous_index = -1
        self.pending_index = None
        self.fast_response_enabled = True

        # 保存原始方法
        self._original_set_current_index = self.stacked_widget.setCurrentIndex
        self.stacked_widget.setCurrentIndex = self._animated_set_current_index

        # 滚动区域相关
        self._saved_hscroll_value = 0
        self._saved_vscroll_value = 0
        self._original_horizontal_policy = None
        self._original_vertical_policy = None

        # 活动效果跟踪
        self.active_widgets_effects = {}

    def _animated_set_current_index(self, index):
        """动画切换实现"""
        if index == self.stacked_widget.currentIndex():
            return

        if self.fast_response_enabled and self.current_animation is not None:
            self.current_animation.setCurrentTime(0)
            self.current_animation = None
            self._cleanup_active_widgets_effects()

            direction = 'down' if index > self.stacked_widget.currentIndex() else 'up'
            self._perform_animation(index, direction)
            return

        direction = 'down' if index > self.stacked_widget.currentIndex() else 'up'

        if self.current_animation is not None:
            if self.pending_index is None:
                self.pending_index = index
            return

        self._perform_animation(index, direction)

    def _cleanup_active_widgets_effects(self):
        """清理效果"""
        for widget, effect in self.active_widgets_effects.items():
            if widget and widget.graphicsEffect() == effect:
                widget.setGraphicsEffect(None)
        self.active_widgets_effects.clear()

    def _perform_animation(self, index, direction='down'):
        """执行上下滑动动画"""
        if not 0 <= index < self.stacked_widget.count():
            self._original_set_current_index(index)
            self._check_pending_index()
            return

        current_widget = self.stacked_widget.currentWidget()
        new_widget = self.stacked_widget.widget(index)

        if not current_widget or not new_widget:
            self._original_set_current_index(index)
            self._check_pending_index()
            return

        # 准备动画环境
        scroll_area = self._find_scroll_area()
        self._save_scroll_state(scroll_area)
        self._prepare_animation_environment(scroll_area, current_widget, new_widget)

        # 设置初始位置
        if direction == 'down':
            new_widget.move(0, self.stacked_widget.height())
        else:
            new_widget.move(0, -self.stacked_widget.height())

        # 透明度效果
        new_opacity_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(new_opacity_effect)
        self.active_widgets_effects[new_widget] = new_opacity_effect
        new_opacity_effect.setOpacity(0.0)

        old_opacity_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(old_opacity_effect)
        self.active_widgets_effects[current_widget] = old_opacity_effect
        old_opacity_effect.setOpacity(1.0)

        # 创建位置动画 - 只修改Y坐标
        new_pos_animation = QPropertyAnimation(new_widget, b"pos")
        new_pos_animation.setDuration(self.animation_duration)
        new_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        old_pos_animation = QPropertyAnimation(current_widget, b"pos")
        old_pos_animation.setDuration(self.animation_duration)
        old_pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        if direction == 'down':
            new_pos_animation.setStartValue(QPoint(0, self.stacked_widget.height()))
            new_pos_animation.setEndValue(QPoint(0, 0))
            old_pos_animation.setStartValue(QPoint(0, 0))
            old_pos_animation.setEndValue(QPoint(0, -self.stacked_widget.height()))
        else:
            new_pos_animation.setStartValue(QPoint(0, -self.stacked_widget.height()))
            new_pos_animation.setEndValue(QPoint(0, 0))
            old_pos_animation.setStartValue(QPoint(0, 0))
            old_pos_animation.setEndValue(QPoint(0, self.stacked_widget.height()))

        # 透明度动画
        old_opacity_animation = QPropertyAnimation(old_opacity_effect, b"opacity")
        old_opacity_animation.setDuration(self.animation_duration)
        old_opacity_animation.setStartValue(1.0)
        old_opacity_animation.setEndValue(0.0)

        new_opacity_animation = QPropertyAnimation(new_opacity_effect, b"opacity")
        new_opacity_animation.setDuration(self.animation_duration)
        new_opacity_animation.setStartValue(0.0)
        new_opacity_animation.setEndValue(1.0)

        # 动画组
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(new_pos_animation)
        animation_group.addAnimation(old_pos_animation)
        animation_group.addAnimation(new_opacity_animation)
        animation_group.addAnimation(old_opacity_animation)

        def animation_finished():
            self._on_animation_finished(index, current_widget, new_widget, scroll_area)
            if current_widget in self.active_widgets_effects:
                del self.active_widgets_effects[current_widget]
            if new_widget in self.active_widgets_effects:
                del self.active_widgets_effects[new_widget]

        animation_group.finished.connect(animation_finished)
        self.current_animation = animation_group
        animation_group.start()

    def _find_scroll_area(self):
        """查找滚动区域"""
        parent = self.stacked_widget.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None

    def _save_scroll_state(self, scroll_area):
        """保存滚动状态"""
        if scroll_area:
            self._saved_hscroll_value = scroll_area.horizontalScrollBar().value()
            self._saved_vscroll_value = scroll_area.verticalScrollBar().value()
            self._original_horizontal_policy = scroll_area.horizontalScrollBarPolicy()
            self._original_vertical_policy = scroll_area.verticalScrollBarPolicy()

    def _prepare_animation_environment(self, scroll_area, current_widget, new_widget):
        """准备动画环境"""
        new_widget.setFixedSize(current_widget.size())
        new_widget.show()
        new_widget.raise_()

        if scroll_area:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setFixedSize(scroll_area.size())
            self._update_scroll_area(scroll_area)

    def _update_scroll_area(self, scroll_area):
        """更新滚动区域"""
        if scroll_area:
            scroll_area.viewport().update()
            scroll_area.updateGeometry()
            scroll_area.adjustSize()
            content_widget = scroll_area.widget()
            if content_widget:
                content_widget.updateGeometry()
                content_widget.adjustSize()
                if content_widget.layout():
                    content_widget.layout().update()

    @pyqtSlot()
    def _on_animation_finished(self, index, current_widget, new_widget, scroll_area):
        """动画完成处理"""
        try:
            if current_widget in self.active_widgets_effects:
                current_widget.setGraphicsEffect(None)
            if new_widget in self.active_widgets_effects:
                new_widget.setGraphicsEffect(None)

            current_widget.move(0, 0)
            new_widget.move(0, 0)

            self._original_set_current_index(index)
            self.previous_index = index

            if scroll_area:
                scroll_area.setHorizontalScrollBarPolicy(self._original_horizontal_policy)
                scroll_area.setVerticalScrollBarPolicy(self._original_vertical_policy)
                scroll_area.horizontalScrollBar().setValue(self._saved_hscroll_value)
                scroll_area.verticalScrollBar().setValue(self._saved_vscroll_value)
                scroll_area.setMinimumSize(0, 0)
                scroll_area.setMaximumSize(16777215, 16777215)
                self._update_scroll_area(scroll_area)

        except Exception as e:
            print(f"动画完成处理错误: {e}")
        finally:
            self.current_animation = None
            self._check_pending_index()

    def _check_pending_index(self):
        """检查待处理索引"""
        if self.pending_index is not None:
            pending_index = self.pending_index
            self.pending_index = None
            self._perform_animation(pending_index)

    def enable_fast_response(self, enabled=True):
        """启用/禁用快速响应"""
        self.fast_response_enabled = enabled