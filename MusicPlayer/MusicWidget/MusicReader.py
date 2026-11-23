from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
                             QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon


class Notepad(QMainWindow):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)  # 必须首先调用父类初始化
        self._initialized = True  # 初始化标记
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.initUI(file_path)

    def initUI(self, file_path):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.textEdit = QTextEdit()
        font = QFont("微软雅黑", 12)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet("QTextEdit { border: none; }")
        self.textEdit.setTextInteractionFlags(Qt.NoTextInteraction)
        layout.addWidget(self.textEdit)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('阅读器')
        self.setWindowIcon(QIcon("MusicIco.ico"))

        if file_path:
            self.loadFile(file_path)
            self.textEdit.setReadOnly(True)

    def loadFile(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.textEdit.setPlainText(content)
                QTimer.singleShot(100, lambda:
                self.textEdit.verticalScrollBar().setValue(0))
        except Exception as e:
            QMessageBox.warning(self, '错误', f'无法打开文件: {str(e)}')


def show_notepad(file_path):
    notepad = Notepad(file_path)
    notepad.show()
    return notepad