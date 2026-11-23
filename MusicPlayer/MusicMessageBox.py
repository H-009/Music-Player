from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit, QPushButton


class Box:
    def Critical_Box(self,title,text):
        self.Box = QMessageBox()
        self.Box.setWindowTitle(title)
        self.Box.setText(text)
        self.Box.setIcon(QMessageBox.Critical)
        self.Box.exec_()

    def Critical_Box2(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("验证错误")  # 标题栏文本
        self.Box.setText("发生错误：许可未激活 部分功能被限制 是否立即激活")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("激活", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("稍后激活", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌


        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def Logout(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("注销许可证")  # 标题栏文本
        self.Box.setText("注销当前许可证将会破坏全部许可信息")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("注销", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("取消", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌


        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def Activation(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("激活许可")  # 标题栏文本
        self.Box.setText("是否立即激活当前许可证")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("激活", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("稍后激活", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌


        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def Information_Box(self,title,text):
        self.Box = QMessageBox()
        self.Box.setWindowTitle(title)
        self.Box.setText(text)
        self.Box.setIcon(QMessageBox.Information)
        self.Box.exec_()

    def Warning_Box(self,title,text):
        self.Box = QMessageBox()
        self.Box.setWindowTitle(title)
        self.Box.setText(text)
        self.Box.setIcon(QMessageBox.Warning)
        self.Box.exec_()

    def Question_Box(self,title,text):
        self.Box = QMessageBox()
        self.Box.setWindowTitle(title)
        self.Box.setText(text)
        self.Box.setIcon(QMessageBox.Question)
        self.Box.exec_()

    def show_custom_dialog(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("风险操作确认")  # 标题栏文本
        self.Box.setText("此操作将删除所有歌单数据！(默认歌单除外)")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("确认删除", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("取消操作", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def show_st_dialog(self,key1,key2):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("数据风险操作确认")  # 标题栏文本
        self.Box.setText(f"是否归零您的播放次数和播放时间\n播放次数 {key1}\n播放时间 {key2}")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("确认删除", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("取消操作", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def show_custom_dialog_one(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("操作确认")  # 标题栏文本
        self.Box.setText("此操作将删除所有数据和缓存！")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("确认删除", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("取消操作", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def show_custom_dialog_two(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("二级操作确认")  # 标题栏文本
        self.Box.setText("再次确认是否删除全部数据！")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("再次确认删除", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("取消操作", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def del_song(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("删除歌曲")  # 标题栏文本
        self.Box.setText("是否删除选中的歌曲")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("是", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("否", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def del_playlist(self):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle("删除歌单")  # 标题栏文本
        self.Box.setText("是否删除选中的歌单")  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton("是", QMessageBox.YesRole)
        cancel_btn = self.Box.addButton("否", QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False

    def text_box(self,txt1,txt2,t3,t4):
        """显示自定义确认对话框‌"""
        self.Box = QMessageBox()

        self.Box.setWindowTitle(txt1)  # 标题栏文本
        self.Box.setText(txt2)  # 正文内容
        self.Box.setIcon(QMessageBox.Warning)  # 设置警告图标‌

        confirm_btn = self.Box.addButton(t3, QMessageBox.YesRole)
        cancel_btn = self.Box.addButton(t4, QMessageBox.NoRole)
        self.Box.setDefaultButton(cancel_btn)  # 默认选中安全选项‌

        self.Box.exec_()  # 模态显示对话框

        if self.Box.clickedButton() == confirm_btn:
            return True
        else:
            return False


    def run_Box(self):
        self.Box.exec_()

def Rename_Input(widget, title, text, current_name=""):
    input_dialog = QInputDialog(widget)

    # 基础配置
    input_dialog.setWindowTitle(title)
    input_dialog.setLabelText(text)
    input_dialog.setTextValue(current_name)
    input_dialog.setInputMode(QInputDialog.TextInput)

    # 窗口尺寸控制 (宽400px, 高200px)
    input_dialog.setFixedSize(400, 200)

    # 获取对话框内部组件引用
    line_edit = input_dialog.findChild(QLineEdit)
    ok_button = input_dialog.findChild(QPushButton, "okButton")
    cancel_button = input_dialog.findChild(QPushButton, "cancelButton")

    # 样式表增强
    input_dialog.setStyleSheet(f"""
    /* 主窗口样式 */
    QInputDialog {{
        background-color: rgb(84,84,84);
        font-family: "SimHei";
        font-size: 14pt;
    }}

    /* 输入框样式 */
    QLineEdit {{
        font-family: "SimHei";
        font-size: 14pt;
        min-width: 300px;
        min-height: 30px;
        border-radius: 5px;
        color: rgb(148,148,148);
        selection-color: rgba(84,84,84);
        selection-background-color: rgba(148,148,148);
        border: 2px solid rgb(148, 148, 148);
        font-size: 12pt;
        padding: 5px;
    }}

    /* 按钮基础样式 */
    QPushButton {{
        font-family: "SimHei";
        font-size: 14pt;
        min-width: 80px;
        min-height: 30px;
        background-color: rgb(84,84,84);
        color: rgb(148,148,148);
        border-radius: 5px;
        border: 2px solid rgb(148, 148, 148);
        font-size: 12pt;
        margin: 5px;
    }}

    /* 按钮悬停效果 */
    QPushButton:hover {{
        background-color: rgb(100,100,100);
    }}

    /* 按钮按下效果 */
    QPushButton:pressed {{
        background-color: rgb(0,0,0);
        color: rgb(200,200,200);
    }}

    /* 标签样式 */
    QLabel {{
        font-family: "SimHei";
        font-size: 14pt;
        color: rgb(148,148,148);
        background-color: transparent;
        font-size: 12pt;
        qproperty-alignment: AlignCenter;
    }}
    """)

    # 手动调整布局间距
    if line_edit and ok_button and cancel_button:
        layout = input_dialog.layout()
        if layout:
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

    if input_dialog.exec() == QInputDialog.Accepted:
        new_name = input_dialog.textValue().strip()
        if new_name:
            return new_name
    return None