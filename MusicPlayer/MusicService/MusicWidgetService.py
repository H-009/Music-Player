from typing import List

from PyQt5.QtCore import Qt, QEvent, QObject, pyqtSignal, QPoint
from PyQt5.QtGui import QDoubleValidator, QMouseEvent
from PyQt5.QtWidgets import QListWidget, QPushButton, QScrollArea, QLineEdit, QWidget, \
    QListWidgetItem, QStyledItemDelegate, QStyle, QSlider


def toggle_buttons_all(button_list: List[QPushButton]):
    """
    禁用列表中的所有按钮

    参数:
        button_list: QPushButton对象列表
    """
    for btn in button_list:
        btn.setEnabled(False)

def toggle_buttons(button_list: List[QPushButton], disable_button: QPushButton):
    """
    禁用指定的按钮，同时启用列表中的其他所有按钮

    参数:
        button_list: QPushButton对象列表
        disable_button: 需要禁用的QPushButton对象
    """
    for btn in button_list:
        if btn is disable_button:
            btn.setEnabled(False)
        else:
            btn.setEnabled(True)

def get_current_item_text(list_widget: QListWidget) -> str:
    """
    获取QListWidget当前选中项的文本内容
    :param list_widget: QListWidget实例
    :return: 当前选中项的文本（若无选中则返回空字符串）
    """
    current_item = list_widget.currentItem()
    return current_item.text() if current_item else ""

def get_selected_or_first(list_widget: QListWidget) -> QListWidgetItem:
    """
    获取当前选中项，若无选中则返回第一项
    :param list_widget: QListWidget实例
    :return: 选中项或第一项的QListWidgetItem对象
    """
    selected = list_widget.selectedItems()
    if selected:
        return selected[0]  # 返回第一个选中项
    elif list_widget.count() > 0:
        list_widget.setCurrentRow(0)  # 自动选中第一项
        return list_widget.item(0)
    return None  # 列表为空时返回None

def set_button_text(button: QPushButton, text: str) -> None:
    """
    设置按钮的显示文本

    参数:
        button (QPushButton): 要设置文本的按钮对象
        text (str): 要设置的文本内容
    """
    button.setText(text)

def set_widgets_enabled(widgets, enabled=True):
    """
    设置一组控件的启用/禁用状态

    参数:
        widgets (list): QWidget 或其子类的控件列表
        enabled (bool): True 启用控件，False 禁用控件
    """
    for widget in widgets:
        if isinstance(widget, QWidget):
            widget.setEnabled(enabled)
        else:
            print(f"警告: {widget} 不是有效的 QWidget 控件")


def disable_button_keyboard_capture(widget):
    """
    递归禁用widget及其子控件中的QPushButton键盘捕捉能力
    参数:
        widget: QWidget及其子类实例
    特性:
        1. 仅影响QPushButton及其子类
        2. 保留其他控件的键盘交互能力
        3. 自动跳过非按钮控件
    """
    if not hasattr(widget, 'findChildren'):
        return

    # 递归处理所有按钮
    for button in widget.findChildren(QPushButton):
        button.setFocusPolicy(Qt.NoFocus)
        button.clearFocus()


def disable_horizontal_scroll_keys(scroll_area: QScrollArea):
    """禁用滚动区域的左右方向键功能
    Args:
        scroll_area: 需要禁用方向键的QScrollArea对象
    """

    def keyPressEvent(event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right,Qt.Key_Up,Qt.Key_Down):
            event.ignore()
        else:
            QScrollArea.keyPressEvent(scroll_area, event)

    scroll_area.keyPressEvent = keyPressEvent

def handle_slider_wheel_event(slider, event):
    """处理滑块滚轮事件，每次增减1"""
    current_value = slider.value()

    # 判断滚轮方向
    if event.angleDelta().y() > 0:  # 向上滚动
        new_value = min(current_value + 1, slider.maximum())
    else:  # 向下滚动
        new_value = max(current_value - 1, slider.minimum())

    # 使用动画方式设置新值（假设 slider 有动画方法）
    QSlider.setValue(slider, new_value)
    slider.sliderMoved.emit(new_value)
    slider.sliderReleased.emit()

    # 接受事件，防止继续传播
    event.accept()

def install_slider_filter(slider):
    """
    禁用滑动条方向键响应
    :param slider:
    :return:
    """
    def eventFilter(obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                return True
        return False
    slider.installEventFilter(slider)
    slider.eventFilter = eventFilter

def set_numeric_input(line_edit: QLineEdit):
    """配置行编辑框仅允许数字和小数点输入
    Args:
        line_edit: 需要限制输入的QLineEdit对象
    """
    validator = QDoubleValidator()
    validator.setNotation(QDoubleValidator.StandardNotation)
    line_edit.setValidator(validator)


def disable_slider_drag(slider):
    """禁用所有拖动相关信号"""
    slider.setTracking(False)  # 阻止拖动时实时触发valueChanged:ml-citation{ref="8" data="citationList"}
    try:
        slider.sliderMoved.disconnect()
        slider.sliderPressed.disconnect()
        slider.sliderReleased.disconnect()
    except TypeError:
        pass
    slider.setEnabled(False)  # 完全禁用交互

# 下拉列表优化
class FontDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 继承父控件字体
        option.font = self.parent().font()

        # 显式处理悬停状态
        if option.state & QStyle.State_MouseOver:
            option.state |= QStyle.State_MouseOver  # 强制激活悬停状态
            option.palette.setColor(option.palette.Highlight, Qt.transparent)  # 保留QSS样式

        super().paint(painter, option, index)

# 列表文件拖动
class ListWidgetDragDropHelper(QObject):
    """为QListWidget添加拖放功能的辅助类"""
    # 定义一个信号，当有文件被拖放时发射
    filesDropped = pyqtSignal(list)  # 参数是文件路径列表

    def __init__(self, list_widget):
        super().__init__()
        self.list_widget = list_widget
        self.setup_drag_drop()

    def setup_drag_drop(self):
        """设置拖放相关属性"""
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragDropMode(QListWidget.DropOnly)

        # 保存原始的事件处理函数（如果需要）
        self.original_dragEnterEvent = self.list_widget.dragEnterEvent
        self.original_dragMoveEvent = self.list_widget.dragMoveEvent
        self.original_dropEvent = self.list_widget.dropEvent

        # 重写事件处理函数
        self.list_widget.dragEnterEvent = self.dragEnterEvent
        self.list_widget.dragMoveEvent = self.dragMoveEvent
        self.list_widget.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_paths.append(url.toLocalFile())

            # 发射信号，传递文件路径列表
            self.filesDropped.emit(file_paths)
            event.acceptProposedAction()
        else:
            event.ignore()

#设置滑动条跳转
def enable_click_to_seek(slider: QSlider):
    """使滑动条支持点击跳转功能"""

    class ClickableSlider(QSlider):
        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                value = self._pos_to_value(event.pos())
                self.setValue(value)
            super().mousePressEvent(event)

        def _pos_to_value(self, pos: QPoint) -> int:
            """将点击位置转换为滑动条值"""
            if self.orientation() == Qt.Horizontal:
                ratio = pos.x() / self.width()
            else:
                ratio = (self.height() - pos.y()) / self.height()  # 垂直方向从下到上计算
            return int(self.minimum() + ratio * (self.maximum() - self.minimum()))

    # 动态替换原始滑动条的类（需确保父控件允许修改）
    slider.__class__ = ClickableSlider
