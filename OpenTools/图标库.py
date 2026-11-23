import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    CardWidget, LineEdit, PushButton,
    InfoBar, BodyLabel, CaptionLabel,
    FluentIcon, TextEdit, setTheme, Theme
)


class IconCard(CardWidget):
    """单个 Fluent 图标卡片"""
    clicked_icon = pyqtSignal(str, QIcon)

    def __init__(self, name: str, icon: QIcon, parent=None):
        super().__init__(parent)
        self.name = name
        self.icon = icon

        self.setFixedSize(120, 110)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(36, 36))
        icon_label.setAlignment(Qt.AlignCenter)

        name_label = CaptionLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

    def mousePressEvent(self, event):
        self.clicked_icon.emit(self.name, self.icon)


class FluentIconViewer(FluentWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FluentIcon 图标浏览器")
        self.resize(1300, 800)

        setTheme(Theme.LIGHT)

        self.icon_data = {}

        self._create_home_page()
        self._create_detail_page()
        self._load_icons()

    # ------------------ 主页 ------------------
    def _create_home_page(self):
        self.home_page = QWidget()
        self.home_page.setObjectName("homePage")

        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(20, 20, 20, 20)

        # 搜索栏
        top_bar = QHBoxLayout()
        self.search_box = LineEdit()
        self.search_box.setPlaceholderText("搜索图标名称...")
        self.search_box.textChanged.connect(self._filter_icons)

        refresh_btn = PushButton("刷新", self, FluentIcon.SYNC)
        refresh_btn.clicked.connect(self._load_icons)

        top_bar.addWidget(self.search_box)
        top_bar.addWidget(refresh_btn)

        self.stats_label = BodyLabel("正在加载图标...")

        # 图标区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.icon_container = QWidget()
        self.icon_grid = QGridLayout(self.icon_container)
        self.icon_grid.setSpacing(15)

        scroll.setWidget(self.icon_container)

        layout.addLayout(top_bar)
        layout.addWidget(self.stats_label)
        layout.addWidget(scroll)

        self.addSubInterface(
            self.home_page,
            FluentIcon.EMOJI_TAB_SYMBOLS,
            "图标列表"
        )

    # ------------------ 详情页 ------------------
    def _create_detail_page(self):
        self.detail_page = QWidget()
        self.detail_page.setObjectName("detailPage")

        layout = QVBoxLayout(self.detail_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.detail_icon_label = QLabel()
        self.detail_icon_label.setAlignment(Qt.AlignCenter)
        self.detail_icon_label.setFixedSize(96, 96)

        self.detail_name_label = BodyLabel()
        self.detail_name_label.setAlignment(Qt.AlignCenter)

        self.code_edit = TextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setFixedHeight(160)

        copy_btn = PushButton("复制示例代码", self, FluentIcon.COPY)
        copy_btn.clicked.connect(self._copy_code)

        layout.addWidget(self.detail_icon_label)
        layout.addWidget(self.detail_name_label)
        layout.addWidget(self.code_edit)
        layout.addWidget(copy_btn, alignment=Qt.AlignLeft)

        self.addSubInterface(
            self.detail_page,
            FluentIcon.INFO,
            "图标详情",
            parent=self.home_page
        )

    # ------------------ 图标加载 ------------------
    def _load_icons(self):
        self.icon_data.clear()
        self._clear_grid()

        attrs = sorted(
            attr for attr in dir(FluentIcon) if not attr.startswith("_")
        )

        row, col = 0, 0
        max_cols = 8

        for name in attrs:
            try:
                value = getattr(FluentIcon, name)
                if not isinstance(value, FluentIcon):
                    continue

                icon = value.icon()
                if icon.isNull():
                    continue

                card = IconCard(name, icon, self)
                card.clicked_icon.connect(self.show_icon_detail)

                self.icon_data[name] = card
                self.icon_grid.addWidget(card, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception:
                pass

        self.stats_label.setText(
            f"共加载 {len(self.icon_data)} 个 FluentIcon 图标"
        )

    # ------------------ 交互 ------------------
    def show_icon_detail(self, name: str, icon: QIcon):
        self.detail_icon_label.setPixmap(icon.pixmap(96, 96))
        self.detail_name_label.setText(f"<h3>{name}</h3>")

        code = f"""from qfluentwidgets import FluentIcon

icon = FluentIcon.{name}.icon()
"""
        self.code_edit.setPlainText(code)

        self.switchTo(self.detail_page)

    def _copy_code(self):
        QApplication.clipboard().setText(self.code_edit.toPlainText())
        InfoBar.success(
            title="已复制",
            content="示例代码已复制到剪贴板",
            duration=1500,
            parent=self
        )

    def _filter_icons(self):
        text = self.search_box.text().lower()
        for name, card in self.icon_data.items():
            card.setVisible(text in name.lower())

    def _clear_grid(self):
        while self.icon_grid.count():
            item = self.icon_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()


# ------------------ main ------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = FluentIconViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()