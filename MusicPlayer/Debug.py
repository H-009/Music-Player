from PyQt5.QtWidgets import QWidget


# 输出当前点击的控件信息
def install_click_debug(widget: QWidget, enabled=True):
    if not enabled:
        return

    old_mouse_press = widget.mousePressEvent

    def wrapped_mouse_press(event):
        name = widget.objectName() or "(no name)"
        cls = widget.metaObject().className()
        print(f"[CLICK] {cls} -> {name}")
        old_mouse_press(event)

    widget.mousePressEvent = wrapped_mouse_press

    for child in widget.findChildren(QWidget):
        install_click_debug(child, enabled)