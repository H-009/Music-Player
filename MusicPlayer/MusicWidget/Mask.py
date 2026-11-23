from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class SizeFittingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
        """)

        layout = QVBoxLayout(self)
        label = QLabel("", self) # 留空标签让widget自动渲染
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)