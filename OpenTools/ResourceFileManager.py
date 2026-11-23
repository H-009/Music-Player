import sys
import json
import base64
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from qfluentwidgets import (
    FluentWindow,
    NavigationBar,
    PushButton,
    ScrollArea,
    FlowLayout, FluentIcon, NavigationItemPosition
)


# -----------------------------
# 单个资源卡片
# -----------------------------
class ImageCard(QWidget):
    def __init__(self, name: str, base64_str: str):
        super().__init__()

        self.setFixedSize(140, 160)
        self.setStyleSheet("background-color: white; border-radius: 8px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 图片
        label_img = QLabel()
        label_img.setAlignment(Qt.AlignCenter)
        label_img.setFixedSize(120, 120)

        try:
            img_data = base64.b64decode(base64_str)
            image = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(image).scaled(
                120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            label_img.setPixmap(pixmap)
        except Exception:
            label_img.setText("Invalid Image")

        # 名称
        label_name = QLabel(name)
        label_name.setAlignment(Qt.AlignCenter)
        label_name.setWordWrap(True)

        layout.addWidget(label_img)
        layout.addWidget(label_name)


# -----------------------------
# 主窗口
# -----------------------------
class ResourceManager(FluentWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JSON 资源管理器")
        self.resize(1000, 700)

        # ===== 左侧卡片区 =====
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.card_container = QWidget()
        self.flow_layout = FlowLayout(self.card_container, needAni=True)
        self.flow_layout.setContentsMargins(20, 20, 20, 20)
        self.flow_layout.setHorizontalSpacing(20)
        self.flow_layout.setVerticalSpacing(20)

        self.scroll_area.setWidget(self.card_container)

        # ===== 右侧控制台 =====
        self.sidebar = NavigationBar(self)

        self.sidebar.addItem(
            FluentIcon.FOLDER,
            "导入资源",
            "111",
            position=NavigationItemPosition.TOP
        )

        self.sidebar.addItem(
            FluentIcon.SAVE,
            "导出资源",
            "222",
            position=NavigationItemPosition.TOP
        )

        self.sidebar.addItem(
            FluentIcon.SYNC,
            "刷新视图",
            "333",
            position=NavigationItemPosition.TOP
        )

        # ===== 布局 =====
        # self.addSubInterface(
        #     self.scroll_area,
        #     text="资源视图",
        # )
        # self.addSubInterface(
        #     self.sidebar,
        #     text="控制台",
        # )

        # 初始化后打开文件选择
        self.load_resource_file()

    # -----------------------------
    # JSON 校验 & 加载
    # -----------------------------
    def load_resource_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择资源 JSON 文件",
            "",
            "JSON Files (*.json);;所有文件 (*.*)"
        )

        if not file_path:
            QMessageBox.warning(self, "提示", "未选择文件")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取 JSON 失败:\n{e}")
            return

        # 校验格式：{ "name": "base64..." }
        if not isinstance(data, dict):
            QMessageBox.warning(self, "校验失败", "JSON 根节点必须是对象")
            return

        for k, v in data.items():
            if not isinstance(k, str) or not isinstance(v, str):
                QMessageBox.warning(self, "校验失败", "资源格式不正确")
                return

        self.update_cards(data)

    # -----------------------------
    # 更新卡片组
    # -----------------------------
    def update_cards(self, resource_dict: dict):
        # 清空旧卡片
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 创建新卡片
        for name, b64 in resource_dict.items():
            card = ImageCard(name, b64)
            self.flow_layout.addWidget(card)


# -----------------------------
# 入口
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ResourceManager()
    w.show()
    sys.exit(app.exec_())