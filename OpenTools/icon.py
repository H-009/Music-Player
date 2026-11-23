import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qfluentwidgets import (
    FluentIcon, CardWidget, LineEdit, PushButton,
    BodyLabel, CaptionLabel, StrongBodyLabel,
    FluentStyleSheet, InfoBar, InfoBarPosition
)

import qfluentwidgets


class IconDetailPanel(QWidget):
    """右侧可折叠侧边栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(0)
        self._target_width = 320
        self._anim = None

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-left: 1px solid #ddd;
            }
        """)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedHeight(80)

        self.name_label = StrongBodyLabel()
        self.code_label = BodyLabel()
        self.code_label.setWordWrap(True)
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: white;
                border-radius: 6px;
            }
        """)

        self.version_label = CaptionLabel(
            f"qfluentwidgets 版本：{qfluentwidgets.__version__}"
        )
        self.version_label.setStyleSheet("color: #666; margin-top: 20px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.code_label)
        layout.addStretch(1)
        layout.addWidget(self.version_label)

    def set_icon(self, name, icon: QIcon):
        self.icon_label.setPixmap(icon.pixmap(64, 64))
        self.name_label.setText(name)
        self.code_label.setText(
            f"from qfluentwidgets import FluentIcon\n\n"
            f"icon = FluentIcon.{name}.icon()"
        )

    def toggle(self, visible: bool):
        target = self._target_width if visible else 0
        if self._anim:
            self._anim.stop()

        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(250)
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(target)
        self._anim.start()


class IconCard(CardWidget):
    clicked_icon = pyqtSignal(str, QIcon)

    def __init__(self, name, icon, parent=None):
        super().__init__(parent)
        self.name = name
        self.icon = icon
        self.setFixedSize(120, 110)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(icon.pixmap(36, 36))
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_name = CaptionLabel(name)
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setStyleSheet("color:#333;")

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_name)

    def mouseReleaseEvent(self, event):
        self.clicked_icon.emit(self.name, self.icon)
        super().mouseReleaseEvent(event)


class FluentIconViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fluent_icons = {}
        self.detail_panel = None
        self.init_ui()
        self.load_all_icons()

    def init_ui(self):
        self.setWindowTitle("FluentIcon 浏览器")
        self.resize(1400, 900)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 左侧主区域 =====
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("FluentIcon 所有可用图标")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#0078d4;")

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size:12px;color:#666;")

        self.filter_edit = LineEdit()
        self.filter_edit.setPlaceholderText("搜索图标名称")
        self.filter_edit.textChanged.connect(self.filter_icons)

        top = QHBoxLayout()
        top.addWidget(self.filter_edit)
        top.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.icons_container = QWidget()
        self.icons_layout = QGridLayout(self.icons_container)
        self.icons_layout.setContentsMargins(20, 20, 20, 20)
        self.icons_layout.setSpacing(20)
        scroll.setWidget(self.icons_container)

        left_layout.addWidget(title)
        left_layout.addWidget(self.stats_label)
        left_layout.addLayout(top)
        left_layout.addWidget(scroll)

        # ===== 右侧侧边栏 =====
        self.detail_panel = IconDetailPanel(self)

        main_layout.addWidget(left)
        main_layout.addWidget(self.detail_panel)

    # ===== 以下完全复用你原有逻辑 =====
    def load_all_icons(self):
        attrs = [a for a in dir(FluentIcon) if not a.startswith("_")]
        attrs.sort()

        row = col = 0
        max_cols = 6
        valid = []

        self.clear_layout(self.icons_layout)

        for name in attrs:
            try:
                obj = getattr(FluentIcon, name)
                icon = obj.icon() if hasattr(obj, "icon") else None
                if icon and not icon.isNull():
                    card = IconCard(name, icon)
                    card.clicked_icon.connect(self.show_detail)
                    self.icons_layout.addWidget(card, row, col)
                    valid.append(name)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            except:
                pass

        self.stats_label.setText(f"有效图标：{len(valid)} 个")

    def show_detail(self, name, icon):
        self.detail_panel.set_icon(name, icon)
        self.detail_panel.toggle(True)
        InfoBar.info(
            title="已选择",
            content=name,
            orient=Qt.Horizontal,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self
        )

    def filter_icons(self):
        text = self.filter_edit.text().lower()
        for i in range(self.icons_layout.count()):
            w = self.icons_layout.itemAt(i).widget()
            if w:
                lbl = w.findChild(QLabel)
                if lbl and text in lbl.text().lower():
                    w.show()
                else:
                    w.hide()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = FluentIconViewer()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()