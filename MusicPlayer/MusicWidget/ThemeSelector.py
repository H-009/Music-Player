from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QFrame, QApplication, QSpinBox, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import sys


class ColorPickerDialog(QDialog):
    colorSelected = pyqtSignal(QColor)  # 新增信号，当颜色被选择时发射

    def __init__(self, title="颜色选择器", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 250)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.color = QColor(255, 0, 0)
        self.initUI()
        self.updateColorPreview()

    def initUI(self):
        self.color_preview = QFrame()
        self.color_preview.setFixedHeight(50)
        self.color_preview.setStyleSheet("background-color: rgb(255, 0, 0); border: 1px solid #999;")
        self.main_layout.addWidget(self.color_preview)

        self.red_slider = self.createColorSlider("红:", 255)
        self.green_slider = self.createColorSlider("绿:", 0)
        self.blue_slider = self.createColorSlider("蓝:", 0)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.onOkClicked)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(button_layout)

    def createColorSlider(self, label_text, default_value):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 255)
        slider.setValue(default_value)
        slider.valueChanged.connect(self.updateColorFromSliders)
        layout.addWidget(slider)

        spin_box = QSpinBox()
        spin_box.setRange(0, 255)
        spin_box.setValue(default_value)
        spin_box.valueChanged.connect(lambda v: slider.setValue(v))
        slider.valueChanged.connect(spin_box.setValue)
        layout.addWidget(spin_box)

        self.main_layout.addLayout(layout)
        return slider

    def updateColorFromSliders(self):
        r = max(0, min(255, self.red_slider.value()))
        g = max(0, min(255, self.green_slider.value()))
        b = max(0, min(255, self.blue_slider.value()))
        self.color = QColor(r, g, b)
        self.updateColorPreview()

    def updateColorPreview(self):
        self.color_preview.setStyleSheet(
            f"background-color: rgb({self.color.red()}, {self.color.green()}, "
            f"{self.color.blue()}); border: 1px solid #999;"
        )

    def onOkClicked(self):
        self.colorSelected.emit(self.color)  # 发射信号
        self.accept()

    def getColor(self):
        return self.color if self.color.isValid() else QColor(255, 0, 0)

    def setColor(self, color):
        if color.isValid():
            self.color = color
            self.red_slider.setValue(color.red())
            self.green_slider.setValue(color.green())
            self.blue_slider.setValue(color.blue())
            self.updateColorPreview()


class MainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题编辑器")
        self.setFixedSize(500, 300)

        self.first_color = QColor(30, 200, 150)
        self.second_color = QColor(30, 30, 30)
        self.filename = ""

        self.initUI()

        # 自动显示对话框
        self.show()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 文件名输入
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("包名称:"))
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("包名称不能为空")
        filename_layout.addWidget(self.filename_edit)
        self.main_layout.addLayout(filename_layout)

        # 第一个颜色选择按钮和预览
        first_color_layout = QHBoxLayout()
        self.first_color_btn = QPushButton("选择主题色")
        self.first_color_btn.clicked.connect(self.selectFirstColor)
        first_color_layout.addWidget(self.first_color_btn)

        self.first_color_preview = QFrame()
        self.first_color_preview.setFixedSize(50, 30)
        self.first_color_preview.setStyleSheet("background-color: rgb(30, 200, 150); border: 1px solid #999;")
        first_color_layout.addWidget(self.first_color_preview)
        self.main_layout.addLayout(first_color_layout)

        # 第二个颜色选择按钮和预览
        second_color_layout = QHBoxLayout()
        self.second_color_btn = QPushButton("选择背景色")
        self.second_color_btn.clicked.connect(self.selectSecondColor)
        second_color_layout.addWidget(self.second_color_btn)

        self.second_color_preview = QFrame()
        self.second_color_preview.setFixedSize(50, 30)
        self.second_color_preview.setStyleSheet("background-color: rgb(30, 30, 30); border: 1px solid #999;")
        second_color_layout.addWidget(self.second_color_preview)
        self.main_layout.addLayout(second_color_layout)

        # 确定和取消按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.validateAndAccept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout)

    def selectFirstColor(self):
        dialog = ColorPickerDialog("选择主题色", self)
        dialog.setColor(self.first_color)
        dialog.colorSelected.connect(self.updateFirstColor)  # 连接信号
        dialog.exec()

    def selectSecondColor(self):
        dialog = ColorPickerDialog("选择背景色", self)
        dialog.setColor(self.second_color)
        dialog.colorSelected.connect(self.updateSecondColor)  # 连接信号
        dialog.exec()

    def updateFirstColor(self, color):
        self.first_color = color
        self.updateFirstColorPreview()

    def updateSecondColor(self, color):
        self.second_color = color
        self.updateSecondColorPreview()

    def updateFirstColorPreview(self):
        self.first_color_preview.setStyleSheet(
            f"background-color: rgb({self.first_color.red()}, {self.first_color.green()}, "
            f"{self.first_color.blue()}); border: 1px solid #999;"
        )

    def updateSecondColorPreview(self):
        self.second_color_preview.setStyleSheet(
            f"background-color: rgb({self.second_color.red()}, {self.second_color.green()}, "
            f"{self.second_color.blue()}); border: 1px solid #999;"
        )

    def validateAndAccept(self):
        self.filename = self.filename_edit.text().strip()
        if not self.filename:
            QMessageBox.warning(self, "警告", "包名称不能为空")
            return

        self.accept()

    def getResults(self):
        return (
            self.first_color if self.first_color.isValid() else QColor(30, 200, 150),
            self.second_color if self.second_color.isValid() else QColor(30, 30, 30),
            self.filename
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建并显示主对话框
    dialog = MainDialog()

    # 处理对话框结果
    if dialog.exec() == QDialog.Accepted:
        theme_color, bg_color, filename = dialog.getResults()
        print(f"主题色: RGB({theme_color.red()}, {theme_color.green()}, {theme_color.blue()})")
        print(f"背景色: RGB({bg_color.red()}, {bg_color.green()}, {bg_color.blue()})")
        print(f"文件名: {filename}.tsp")
    else:
        print("用户取消了操作")

    sys.exit(app.exec())