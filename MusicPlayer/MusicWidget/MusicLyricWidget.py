import re
import sys
import traceback

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QThread, QEasingCurve, QObject, QPointF, QElapsedTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QScrollArea,
                             QVBoxLayout, QLabel)

# 弹性动画 歌词滚动区域定制
class LyricElasticScrollAnimator(QObject):
    """
    为QScrollArea添加弹性滚动效果的封装类

    特性:
    1. 当用户滚动超过内容边界时，会产生弹性效果
    2. 快速滚动时会累积动量，实现惯性滚动
    3. 当释放滚动后，如果仍在边界外，会产生回弹动画
    4. 到达顶部或底部时有平滑的动画效果，不会出现无法滚动的情况
    5. 到达边界时不会继续同方向的滚动动画
    """

    def __init__(self, scroll_area,lyric_widget=None):
        """
        初始化弹性滚动动画器

        参数:
            scroll_area: 要添加弹性滚动效果的QScrollArea
        """
        super().__init__()
        self.lyric_widget = lyric_widget

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
        self._momentum_factor = 0.90  # 动量衰减因子
        self._drag_resistance = 0.9  # 拖动阻力，控制拖动时的减速

        self._scrolling_reset_timer = QTimer(self)
        self._scrolling_reset_timer.setSingleShot(True)  # 单次触发
        self._scrolling_reset_timer.setInterval(1000)  # 1000ms = 1秒
        self._scrolling_reset_timer.timeout.connect(self._on_scrolling_finished)


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
        if not self._elastic_enabled:
            if hasattr(self.scroll_area, '_original_wheel_event'):
                self.scroll_area._original_wheel_event(event)
            else:
                super(QScrollArea, self.scroll_area).wheelEvent(event)
            return

        # ✅ 检测到用户滚轮滚动，设置 LyricWidget 的滚动状态为 True
        if self.lyric_widget and hasattr(self.lyric_widget, '_user_is_scrolling'):
            self.lyric_widget._user_is_scrolling = True  # 标记用户正在手动滚轮滚动
            # ✅ 启动 1 秒定时器，到期后自动重置为 False
            self._scrolling_reset_timer.start()  # 1000ms 后调用 _on_scrolling_finished

        # 🔧 新增：用户开始手动滚动时，立即停止 LyricWidget 正在执行的自动滚动动画（防止冲突！）
        if self.lyric_widget and hasattr(self.lyric_widget, '_scroll_anim') and self.lyric_widget._scroll_anim:
            self.lyric_widget._scroll_anim.stop()

        # 处理弹性滚动的逻辑
        delta = event.angleDelta().y() / 120
        self._momentum.setY(self._momentum.y() - delta * 10)
        self._start_animation()
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

    def _on_scrolling_finished(self):
        if self.lyric_widget and hasattr(self.lyric_widget, '_user_is_scrolling'):
            self.lyric_widget._user_is_scrolling = False
            self.lyric_widget.highlight_current_line()

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


class TimeMonitorThread(QThread):
    # 信号：发射解析后的时间（单位：秒，类型 float）
    time_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._current_time_str = "0:00.000"
        self._running = True

    def run(self):
        try:
            while self._running:
                current_time_sec = self.parse_time()
                if current_time_sec is not None:
                    self.time_updated.emit(current_time_sec)
                self.msleep(1)
        except Exception as e:
            print(f"[TimeMonitorThread] 运行异常: {e}")

    def parse_time(self):
        try:
            match = re.match(r'^(\d+):(\d{2})\.(\d{3})$', self._current_time_str.strip())
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3))
                total_seconds = minutes * 60 + seconds + milliseconds / 1000.0
                return total_seconds
            else:
                print(f"[TimeMonitorThread] 时间格式不匹配，当前值: '{self._current_time_str}'")
        except Exception as e:
            print(f"[TimeMonitorThread] 解析时间出错: {e}")
        return None

    def update_time_string(self, time_str):
        self._current_time_str = time_str

    def stop(self):
        self._running = False
        self.wait()


class LyricWidget(QWidget):
    # 自定义信号：当检测到用户使用鼠标滚轮滚动时发射
    mouseWheelScrolled = pyqtSignal()  # 可以传递 delta 或其他信息
    lyricLineChanged = pyqtSignal(str)  # ✅ 当前高亮歌词行
    lyricChanged = pyqtSignal(str)
    def __init__(self, label,parent=None):
        super().__init__(parent)
        self.color = "30,200,150"
        self.lyrics = []  # [(时间秒数 float, 歌词 str), ...]
        self.current_line = 0
        self._fixed_width = 950
        self._fixed_height = 220
        self.none_sp = 0 #空白距离
        self.none_sp_init = 10 # 预冲距离
        self.monitor_thread = None
        self.line_height = 50
        self.init_ui()
        self._scroll_anim = None
        self._scale_anim = None
        self._user_is_scrolling = False
        self.label_font = label

        self.NORMAL_FONT_SIZE = 15
        self.HIGHLIGHT_FONT_SIZE = 20

    def init_line(self):
        max_newlines = 0
        for _, text in self.lyrics:
            newline_count = text.count('\n')
            if newline_count > max_newlines:
                max_newlines = newline_count

        if max_newlines == 1:  # 两行歌词
            self.layout.setSpacing(20)
            self.none_sp_init = 18
        elif max_newlines >= 2:  # 3行歌词
            self.layout.setSpacing(30)
            self.none_sp_init = 20

        elif max_newlines >= 3:  # 4行歌词
            self.layout.setSpacing(50)
            self.none_sp_init = 28

        else:  # 包括0和1个换行符的情况
            self.layout.setSpacing(0)
            self.none_sp_init = 15
        #self.line_height = 100

    def disable_horizontal_scroll_keys(self,scroll_area: QScrollArea):
        """禁用滚动区域的左右方向键功能
        Args:
            scroll_area: 需要禁用方向键的QScrollArea对象
        """

        def keyPressEvent(event):
            if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                event.ignore()
            else:
                QScrollArea.keyPressEvent(scroll_area, event)

        scroll_area.keyPressEvent = keyPressEvent

    def init_ui(self):
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(False)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setFixedSize(self._fixed_width, self._fixed_height)

        LyricElasticScrollAnimator(self.scroll, lyric_widget=self)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.container.setFixedWidth(self._fixed_width)

        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll.setWidget(self.container)

        self.disable_horizontal_scroll_keys(self.scroll)

    def bind_time_label(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
        self.monitor_thread = TimeMonitorThread()
        self.monitor_thread.time_updated.connect(self.update_lyric_position)
        self.monitor_thread.start()

    def update_current_time_str(self, time_str):
        if self.monitor_thread:
            self.monitor_thread.update_time_string(time_str)
        else:
            print("[LyricWidget] 警告：时间监控线程未启动，请先调用 bind_time_monitor()")

    def update_lyric_position(self, current_sec: float):
        try:
            if not self.lyrics:
                return

            new_line = 0
            for i, (time_sec, _) in enumerate(self.lyrics):
                if time_sec <= current_sec:
                    new_line = i
                else:
                    break

            if new_line != self.current_line:
                self.current_line = new_line
                self.highlight_current_line()

        except Exception as e:
            print("update_lyric_position 异常:", e)

    def highlight_current_line(self):
        try:

            # ====== 安全检查 1：必须有歌词和布局行 ======
            if not self.lyrics or self.layout.count() == 0:
                print("调试：无歌词或布局为空，不执行高亮")
                return

            total_lines = self.layout.count()
            if self.current_line < 0 or self.current_line >= total_lines:
                print(f"调试：current_line={self.current_line} 越界 [0, {total_lines - 1}]，不执行高亮")
                return

            # ====== 安全检查 2：获取当前行 QLabel，确保未销毁 ======
            current_item = self.layout.itemAt(self.current_line)
            if not current_item:
                print("警告：当前行的 item 不存在，current_line 可能越界")
                return
            current_label = current_item.widget()
            if not current_label:
                print("警告：当前行的 QLabel 已被删除")
                return

            # 强制刷新布局（确保 geometry 是最新的）
            self.container.updateGeometry()
            self.container.adjustSize()
            QApplication.processEvents()

            # 获取当前 label 的几何信息
            if current_label:
                label_geometry = current_label.geometry()
                label_top_in_container = label_geometry.top()
                label_height = label_geometry.height()
                label_center_y = label_top_in_container + label_height // 2

                # ====== 计算 viewport 中心 ======
                viewport = self.scroll.viewport()
                viewport_height = viewport.height()
                viewport_center_y = viewport_height // 2

                # 计算目标滚动位置：当前行中心 == viewport 中心
                target_scroll_y = label_center_y - viewport_center_y
                target_scroll_y = max(0, target_scroll_y)

                # ====== 滚动动画（仅当用户没有手动滚动时才执行）=====
                if not self._user_is_scrolling:
                    if self._scroll_anim:
                        self._scroll_anim.stop()

                    if not hasattr(self, '_scroll_anim') or self._scroll_anim is None:
                        self._scroll_anim = QPropertyAnimation(self.scroll.verticalScrollBar(), b"value")
                        self._scroll_anim.setEasingCurve(QEasingCurve.OutQuad)
                        self._scroll_anim.setDuration(400)

                    current_scroll = self.scroll.verticalScrollBar().value()
                    self._scroll_anim.setStartValue(current_scroll)
                    self._scroll_anim.setEndValue(target_scroll_y)
                    self._scroll_anim.start()

                # ====== 设置样式：高亮当前行，淡化其他行 ======


                for i in range(total_lines):
                    item = self.layout.itemAt(i)
                    if not item:
                        continue
                    label = item.widget()
                    if not label:
                        continue

                    if i == self.current_line:
                        label.setStyleSheet(f"font-size: 20px; color: rgba({self.color});"
                                            f"min-height: {self.line_height}px; background-color: rgba(0, 0, 0, 0);")
                    else:
                        label.setStyleSheet(f"font-size: 15px; color: rgba({self.color}, 0.5);"
                                            f"min-height: {self.line_height}px; background-color: rgba(0, 0, 0, 0);")

                    label.setFont(self.label_font.font())

            # ====== 发送当前高亮歌词信号 ======
            if self.lyrics and 0 <= self.current_line < len(self.lyrics):
                _, text = self.lyrics[self.current_line]

                # ✅ 只取第一行（防止多行歌词）
                single_line = text.split("\n")[0].strip()

                self.lyricLineChanged.emit(single_line)
                self.lyricChanged.emit(text)

        except Exception as a:
            # 获取错误追踪信息
            tb = traceback.extract_tb(sys.exc_info()[2])
            # 获取错误发生的行号
            line_number = tb[-1].lineno
            print("高亮错误", a, '所在', line_number)

    def highlight_line(self, line_number: int):
        """
        手动高亮指定行号的歌词（从0开始），不检查是否越界，强制尝试操作。
        同时滚动到该行，使其位于视口中央。

        Args:
            line_number (int): 指定要高亮的歌词行号（从0开始，可以超出实际行数）
        """
        try:
            total_lines = self.layout.count()

            # 强制刷新布局，确保控件位置正确
            self.container.updateGeometry()
            self.container.adjustSize()
            QApplication.processEvents()

            # 遍历所有行，设置样式 & 尝试滚动到目标行
            for i in range(total_lines):
                item = self.layout.itemAt(i)
                if not item:
                    continue
                label = item.widget()
                if not label:
                    continue

                if i == self.current_line:
                    label.setStyleSheet(f"font-size: 20px; color: rgba({self.color});"
                                        f"min-height: {self.line_height}px; background-color: rgba(0, 0, 0, 0);")
                else:
                    label.setStyleSheet(f"font-size: 15px; color: rgba({self.color}, 0.5);"
                                        f"min-height: {self.line_height}px; background-color: rgba(0, 0, 0, 0);")

                label.setFont(self.label_font.font())

            # 尝试滚动到指定行（即使 line_number 越界也尝试）
            if 0 <= line_number < total_lines:
                current_item = self.layout.itemAt(line_number)
                if current_item and current_item.widget():
                    current_label = current_item.widget()
                    label_geometry = current_label.geometry()
                    label_top_in_container = label_geometry.top()
                    label_height = label_geometry.height()
                    label_center_y = label_top_in_container + label_height // 2

                    # Viewport 信息
                    viewport = self.scroll.viewport()
                    viewport_height = viewport.height()
                    viewport_center_y = viewport_height // 2

                    # 目标滚动位置
                    target_scroll_y = label_center_y - viewport_center_y
                    target_scroll_y = max(0, target_scroll_y)

                    # 滚动动画
                    if self._scroll_anim:
                        self._scroll_anim.stop()

                    if not hasattr(self, '_scroll_anim') or self._scroll_anim is None:
                        self._scroll_anim = QPropertyAnimation(self.scroll.verticalScrollBar(), b"value")
                        self._scroll_anim.setEasingCurve(QEasingCurve.OutQuad)
                        self._scroll_anim.setDuration(400)

                    current_scroll = self.scroll.verticalScrollBar().value()
                    self._scroll_anim.setStartValue(current_scroll)
                    self._scroll_anim.setEndValue(target_scroll_y)
                    self._scroll_anim.start()

            # ====== 发送当前高亮歌词信号 ======
            if self.lyrics and 0 <= self.current_line < len(self.lyrics):
                _, text = self.lyrics[self.current_line]

                # ✅ 只取第一行（防止多行歌词）
                single_line = text.split("\n")[0].strip()

                self.lyricLineChanged.emit(single_line)
                self.lyricChanged.emit(text)

        except Exception as a:
            tb = traceback.extract_tb(sys.exc_info()[2])
            line_number_err = tb[-1].lineno
            print(f"[highlight_line] 异常: {a}, 行号: {line_number}, 错误发生在: {line_number_err}")

    def set_custom_size(self, width, height):
        self._fixed_width = width
        self._fixed_height = height
        self.setFixedSize(width, height)
        self.scroll.setFixedSize(width, height)
        self.container.setFixedWidth(width)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()  # 立刻对用户不可见（优化体验）
                widget.setParent(None)  # 可选，解除父子关系
                widget.deleteLater()  # 安全销毁

    def set_lyrics(self, lyrics, color):
        # 危险！清空布局并删除所有子 widgets！
        self.clear_layout()

        self.scroll.hide() # 后显示

        self.lyrics = lyrics
        self.current_line = 0

        self.none_sp = 600

        self.init_line()
        self.color = color

        total_height = 0
        for time_sec, text in self.lyrics:
            label = QLabel(text)
            label.setFixedHeight(100)
            label.setStyleSheet(f"font-size: 15px; color: rgba({color}, 0.5);"
                                f"min-height: {self.line_height}px; background-color: rgba(0, 0, 0, 0);")
            label.font_size = 15
            label.setAlignment(Qt.AlignCenter)
            total_height += 50
            total_height += self.layout.spacing() # 增加布局间隔
            self.none_sp += self.none_sp_init # 空白距离 预冲距离

            self.layout.addWidget(label)

            new_font = QFont(self.label_font.font())  # 复制原字体
            new_font.setPointSize(15)  # 修改字号
            label.setFont(new_font)  # 应用到目标控件


        # 7. （重要！）让布局和控件立即更新（可选，但有助于减少残留）
        self.container.updateGeometry()
        self.container.adjustSize()
        QApplication.processEvents()  # ⚠️ 谨慎使用，仅在必要时

        self.container.setFixedHeight(total_height+self.none_sp)
        self.scroll.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid rgba(0,0,0,0);")
        self.scroll.show() # 重新部署滚动画布 防止显示歌词密集排列

        self.highlight_line(1)
