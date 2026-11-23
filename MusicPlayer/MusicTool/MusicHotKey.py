import keyboard
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QShortcut
import threading


def bind_key_to_slot(widget, slot_function, key_sequence):
    """
    为指定的widget绑定一个快捷键，禁用自动重复功能。
    """
    shortcut = QShortcut(QKeySequence(key_sequence), widget)
    shortcut.setAutoRepeat(False)  # 关键设置，禁用自动重复
    shortcut.activated.connect(slot_function)

class KeyListener(QObject):
    def __init__(self, slot_function):
        super().__init__()
        self.slot_function = slot_function

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            key = event.key()
            self.slot_function(key)
        return super().eventFilter(obj, event)


def setup_global_key_listener(slot_function):
    app = QApplication.instance()
    listener = KeyListener(slot_function)
    app.installEventFilter(listener)
    return listener


class GlobalHotkeyManager(QObject):
    triggered = pyqtSignal()

    def __init__(self, hotkey):
        super().__init__()
        self.hotkey = hotkey
        self._key_pressed = False  # 跟踪按键状态
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        def listen():
            # 监听按键按下事件（而不是热键）
            keyboard.on_press_key(self._get_main_key(self.hotkey), self._on_key_press)
            keyboard.on_release_key(self._get_main_key(self.hotkey), self._on_key_release)
            keyboard.wait()

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()

    def _get_main_key(self, hotkey):
        """从组合键中提取主键（最后一个键）"""
        keys = hotkey.split('+')
        return keys[-1].strip()

    def _on_key_press(self, event):
        """处理按键按下事件"""
        if not self._key_pressed:
            # 检查是否所有修饰键都按下（对于组合键）
            if self._check_modifiers():
                self._key_pressed = True
                self.triggered.emit()

    def _on_key_release(self, event):
        """处理按键释放事件"""
        self._key_pressed = False

    def _check_modifiers(self):
        """检查修饰键（如Ctrl、Alt等）是否按下"""
        modifiers = self.hotkey.split('+')[:-1]
        for mod in modifiers:
            mod = mod.strip().lower()
            if mod == 'ctrl' and not keyboard.is_pressed('ctrl'):
                return False
            elif mod == 'alt' and not keyboard.is_pressed('alt'):
                return False
            elif mod == 'shift' and not keyboard.is_pressed('shift'):
                return False
            elif mod == 'win' and not keyboard.is_pressed('win'):
                return False
        return True