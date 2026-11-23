import ctypes
import sys
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtWidgets import QApplication, QMainWindow
import ReverberatorUI
import ReverberatorService


class Reverberator:
    def __init__(self):

        self.app = QApplication(sys.argv)
        self.Main = QMainWindow()
        self.st = None
        self.com = 1

        # 创建UI实例
        self.ui = ReverberatorUI.Ui_From()
        # 创建一个QWidget作为容器
        central_widget = QWidget()
        self.central_widget = central_widget
        # 将UI设置到这个widget上
        self.ui.setupUi(central_widget)
        # 设置为主窗口的中央部件
        self.Main.setCentralWidget(central_widget)

        # 连接下拉列表并初始化界面设置
        self.ui.comboBox.currentIndexChanged.connect(self.update_com)  # 直接连接，默认传递int参数
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.horizontalSlider.setValue(5)
        self.ui.num_label_1.setText("0.5")

        #绑定滑动条
        self.ui.horizontalSlider.valueChanged.connect(lambda :self.update_label(1))
        self.ui.horizontalSlider_2.valueChanged.connect(lambda: self.update_label(2))
        self.ui.horizontalSlider_3.valueChanged.connect(lambda: self.update_label(3))
        self.ui.horizontalSlider_4.valueChanged.connect(lambda: self.update_label(4))
        self.ui.horizontalSlider_5.valueChanged.connect(lambda: self.update_label(5))
        self.ui.horizontalSlider_6.valueChanged.connect(lambda: self.update_label(6))
        self.ui.horizontalSlider_7.valueChanged.connect(lambda: self.update_label(7))
        self.ui.horizontalSlider_8.valueChanged.connect(lambda: self.update_label(8))
        self.ui.horizontalSlider_9.valueChanged.connect(lambda: self.update_label(9))

        self.ui.horizontalSlider_10.valueChanged.connect(lambda: self.update_label(10))
        self.ui.horizontalSlider_11.valueChanged.connect(lambda: self.update_label(11))
        self.ui.horizontalSlider_12.valueChanged.connect(lambda: self.update_label(12))
        self.ui.horizontalSlider_13.valueChanged.connect(lambda: self.update_label(13))
        self.ui.horizontalSlider_17.valueChanged.connect(lambda: self.update_label(14))
        self.ui.horizontalSlider_15.valueChanged.connect(lambda: self.update_label(15))
        self.ui.horizontalSlider_14.valueChanged.connect(lambda: self.update_label(16))

        self.ui.horizontalSlider_18.valueChanged.connect(lambda: self.update_label(17))
        self.ui.horizontalSlider_19.valueChanged.connect(lambda: self.update_label(18))
        self.ui.horizontalSlider_16.valueChanged.connect(lambda: self.update_label(19))

        self.ui.horizontalSlider_22.valueChanged.connect(lambda: self.update_label(20))
        self.ui.horizontalSlider_23.valueChanged.connect(lambda: self.update_label(21))
        self.ui.horizontalSlider_21.valueChanged.connect(lambda: self.update_label(22))
        self.ui.horizontalSlider_20.valueChanged.connect(lambda: self.update_label(23))

        self.ui.horizontalSlider_26.valueChanged.connect(lambda: self.update_label(24))
        self.ui.horizontalSlider_24.valueChanged.connect(lambda: self.update_label(25))
        self.ui.horizontalSlider_25.valueChanged.connect(lambda: self.update_label(26))

        self.ui.horizontalSlider_29.valueChanged.connect(lambda: self.update_label(27))
        self.ui.horizontalSlider_31.valueChanged.connect(lambda: self.update_label(28))
        self.ui.horizontalSlider_28.valueChanged.connect(lambda: self.update_label(29))
        self.ui.horizontalSlider_27.valueChanged.connect(lambda: self.update_label(30))
        self.ui.horizontalSlider_30.valueChanged.connect(lambda: self.update_label(31))

        self.ui.radioButton.clicked.connect(lambda:self.state(1))
        self.ui.radioButton_2.clicked.connect(lambda: self.state(2))
        self.ui.radioButton_3.clicked.connect(lambda: self.state(3))

        self.ui.pushButton.clicked.connect(self.apply)

        self.Main.setMinimumSize(650, 610)  # 设置窗口最小尺寸
        self.Main.setMaximumSize(650, 610)  # 设置窗口最大尺寸

        self.app.setWindowIcon(QIcon("ReverberatorIco.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("混响器")
        self.Main.setWindowTitle("混响器")

        self.Main.show()

        with open("../../Config/Local/select music.amc", "r", encoding="UTF-8") as f:
            self.path_music = f.read()
        with open("../../Config/Local/select playlist.amc", "r", encoding="UTF-8") as f:
            self.path_playlist = f.read()

        self.path = f"../../Play List/{self.path_playlist}/{self.path_music}.mp3"
        self.out_path = self.out_path = f"../../Play List/混响/{self.path_music} v1.mp3"
        self.ui.label_34.setText(self.path_music+'.mp3')

        sys.exit(self.app.exec())

    def state(self,m):
        if m == 1:
            self.st = None
        elif m == 2:
            self.st = "nature"
        elif m == 3:
            self.st = "urban"

    #更新标签
    def update_label(self,model):
        if model == 1:
            num = self.ui.horizontalSlider.value()
            self.ui.num_label_1.setText(str(num/10))
        elif model == 2:
            num = self.ui.horizontalSlider_2.value()
            self.ui.num_label_2.setText(str(num/10))
        elif model == 3:
            num = self.ui.horizontalSlider_3.value()
            self.ui.num_label_3.setText(str(num/10))
        elif model == 4:
            num = self.ui.horizontalSlider_4.value()
            self.ui.num_label_4.setText(str(num/10))
        elif model == 5:
            num = self.ui.horizontalSlider_5.value()
            self.ui.num_label_5.setText(str(num/10))
        elif model == 6:
            num = self.ui.horizontalSlider_6.value()
            self.ui.num_label_6.setText(str(num))
        elif model == 7:
            num = self.ui.horizontalSlider_7.value()
            self.ui.num_label_7.setText(str(num/10))
        elif model == 8:
            num = self.ui.horizontalSlider_8.value()
            self.ui.num_label_8.setText(str(num/10))
        elif model == 9:
            num = self.ui.horizontalSlider_9.value()
            self.ui.num_label_9.setText(str(num/10))
        elif model == 10:
            num = self.ui.horizontalSlider_10.value()
            self.ui.num_label_12.setText(str(num/10))
        elif model == 11:
            num = self.ui.horizontalSlider_11.value()
            self.ui.num_label_11.setText(str(num/10))
        elif model == 12:
            num = self.ui.horizontalSlider_12.value()
            self.ui.num_label_13.setText(str(num/10))
        elif model == 13:
            num = self.ui.horizontalSlider_13.value()
            self.ui.num_label_10.setText(str(num/10))
        elif model == 14:
            num = self.ui.horizontalSlider_17.value()
            self.ui.num_label_14.setText(str(num/10))
        elif model == 15:
            num = self.ui.horizontalSlider_15.value()
            self.ui.num_label_15.setText(str(num))
        elif model == 16:
            num = self.ui.horizontalSlider_14.value()
            self.ui.num_label_16.setText(str(num/10))
        elif model == 17:
            num = self.ui.horizontalSlider_18.value()
            self.ui.num_label_17.setText(str(num/10))
        elif model == 18:
            num = self.ui.horizontalSlider_19.value()
            self.ui.num_label_19.setText(str(num/10))
        elif model == 19:
            num = self.ui.horizontalSlider_16.value()
            self.ui.num_label_18.setText(str(num/10))

        elif model == 20:
            num = self.ui.horizontalSlider_22.value()
            self.ui.num_label_20.setText(str(num/10))
        elif model == 21:
            num = self.ui.horizontalSlider_23.value()
            self.ui.num_label_23.setText(str(num/10))
        elif model == 22:
            num = self.ui.horizontalSlider_21.value()
            self.ui.num_label_22.setText(str(num/10))
        elif model == 23:
            num = self.ui.horizontalSlider_20.value()
            self.ui.num_label_21.setText(str(num/10))

        elif model == 24:
            num = self.ui.horizontalSlider_26.value()
            self.ui.num_label_25.setText("-"+str(num/10))
        elif model == 25:
            num = self.ui.horizontalSlider_24.value()
            self.ui.num_label_26.setText(str(num*10))
        elif model == 26:
            num = self.ui.horizontalSlider_25.value()
            self.ui.num_label_24.setText(str(num*10))

        elif model == 27:
            num = self.ui.horizontalSlider_29.value()
            self.ui.num_label_28.setText("-"+str(num))
        elif model == 28:
            num = self.ui.horizontalSlider_31.value()
            self.ui.num_label_31.setText("-"+str(num))
        elif model == 29:
            num = self.ui.horizontalSlider_28.value()
            self.ui.num_label_30.setText(str(num*10))
        elif model == 30:
            num = self.ui.horizontalSlider_27.value()
            self.ui.num_label_29.setText(str(num/10))
        elif model == 31:
            num = self.ui.horizontalSlider_30.value()
            self.ui.num_label_27.setText(str(num))

    #更新界面
    def update_com(self, text):
        if text == "混响v1 重复音":
            self.com = 1
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.horizontalSlider.setValue(5)
        elif text == "混响v2 延音":
            self.com = 2
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.horizontalSlider_2.setValue(3)
            self.ui.horizontalSlider_3.setValue(5)
            self.ui.horizontalSlider_5.setValue(3)
            self.ui.horizontalSlider_4.setValue(7)
            self.ui.horizontalSlider_6.setValue(6)
            self.ui.horizontalSlider_7.setValue(10)
        if text == "混响v3 室内音":
            self.com = 3
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.horizontalSlider_8.setValue(4)
        elif text == "混响v4 远回音":
            self.com = 4
            self.ui.stackedWidget.setCurrentIndex(3)
            self.ui.horizontalSlider_9.setValue(3)
        if text == "混响v5 长延音":
            self.com = 5
            self.ui.stackedWidget.setCurrentIndex(4)
            self.ui.horizontalSlider_13.setValue(3)
            self.ui.horizontalSlider_11.setValue(5)
            self.ui.horizontalSlider_10.setValue(3)
            self.ui.horizontalSlider_12.setValue(7)
            self.ui.horizontalSlider_17.setValue(1)
            self.ui.horizontalSlider_15.setValue(6)
            self.ui.horizontalSlider_14.setValue(10)
            self.ui.radioButton.setChecked(True)
        elif text == "混响v6 室内隔断音":
            self.com = 6
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.horizontalSlider_18.setValue(5)
            self.ui.horizontalSlider_19.setValue(7)
            self.ui.horizontalSlider_16.setValue(4)
        if text == "混响v7 现场音":
            self.com = 7
            self.ui.stackedWidget.setCurrentIndex(6)
            self.ui.horizontalSlider_22.setValue(3)
            self.ui.horizontalSlider_23.setValue(5)
            self.ui.horizontalSlider_21.setValue(3)
            self.ui.horizontalSlider_20.setValue(7)
        elif text == "混响v8 室内回音":
            self.com = 8
            self.ui.stackedWidget.setCurrentIndex(7)
            self.ui.horizontalSlider_26.setValue(6)
            self.ui.horizontalSlider_24.setValue(5)#500
            self.ui.horizontalSlider_25.setValue(10)#100
        elif text == "混响v9 高级混响":
            self.com = 9
            self.ui.stackedWidget.setCurrentIndex(8)
            self.ui.horizontalSlider_29.setValue(3)#-3
            self.ui.horizontalSlider_31.setValue(12)#-12
            self.ui.horizontalSlider_28.setValue(15)#150
            self.ui.horizontalSlider_27.setValue(7)#0.7
            self.ui.horizontalSlider_30.setValue(3)

    # 应用修改
    def apply(self):
        ReverberatorService.ensure_folder_exists(self.path)
        try:
            if self.com == 1:
                self.out_path = f"../../Play List/混响/{self.path_music} v1.mp3"
                ReverberatorService.reverberation_1(self.path,self.out_path,float(self.ui.num_label_1.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v1.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v1.mp3")

            elif self.com == 2:
                self.out_path = f"../../Play List/混响/{self.path_music} v2.mp3"
                ReverberatorService.reverberation_2(self.path,self.out_path,
                                                    delay=float(self.ui.num_label_2.text()),
                                                    decay=float(self.ui.num_label_3.text()),
                                                    wet_level=float(self.ui.num_label_5.text()),
                                                    dry_level=float(self.ui.num_label_4.text()),
                                                    reverb_strength=float(self.ui.num_label_7.text()),
                                                    num_echoes=int(self.ui.num_label_6.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v2.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v2.mp3")

            elif self.com == 3:
                self.out_path = f"../../Play List/混响/{self.path_music} v3.mp3"
                ReverberatorService.reverberation_3(self.path,self.out_path,float(self.ui.num_label_8.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v3.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v3.mp3")

            elif self.com == 4:
                self.out_path = f"../../Play List/混响/{self.path_music} v4.mp3"
                ReverberatorService.reverberation_4(self.path,self.out_path,float(self.ui.num_label_9.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v4.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v4.mp3")

            elif self.com == 5:
                self.out_path = f"../../Play List/混响/{self.path_music} v5.mp3"
                ReverberatorService.reverberation_5(self.path,self.out_path,
                                                    delay=float(self.ui.num_label_10.text()),
                                                    decay=float(self.ui.num_label_11.text()),
                                                    wet_level=float(self.ui.num_label_12.text()),
                                                    dry_level=float(self.ui.num_label_13.text()),
                                                    reverb_strength=float(self.ui.num_label_14.text()),
                                                    num_echoes=int(self.ui.num_label_15.text()),
                                                    env_noise=self.st,
                                                    noise_intensity=float(self.ui.num_label_16.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v5.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v5.mp3")

            elif self.com == 6:
                self.out_path = f"../../Play List/混响/{self.path_music} v6.mp3"
                ReverberatorService.reverberation_6(self.path,self.out_path,
                                                    intensity=float(self.ui.num_label_17.text()),
                                                    room_size=float(self.ui.num_label_19.text()),
                                                    feedback=float(self.ui.num_label_18.text()),)
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v6.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v6.mp3")

            elif self.com == 7:
                self.out_path = f"../../Play List/混响/{self.path_music} v7.mp3"
                ReverberatorService.reverberation_7(self.path,self.out_path,
                                                    delay=float(self.ui.num_label_20.text()),
                                                    decay=float(self.ui.num_label_23.text()),
                                                    wet_level=float(self.ui.num_label_22.text()),
                                                    dry_level=float(self.ui.num_label_21.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v7.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v7.mp3")

            elif self.com == 8:
                self.out_path = f"../../Play List/混响/{self.path_music} v8.mp3"
                ReverberatorService.reverberation_8(self.path,self.out_path,
                                                    wet_gain=float(self.ui.num_label_25.text()),
                                                    delay_ms=int(self.ui.num_label_26.text()),
                                                    overlay_position=int(self.ui.num_label_24.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v8.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v8.mp3")

            elif self.com == 9:
                self.out_path = f"../../Play List/混响/{self.path_music} v9.mp3"
                ReverberatorService.reverberation_9(self.path,self.out_path,
                                                    dry_gain=int(self.ui.num_label_28.text()),
                                                    wet_gain=int(self.ui.num_label_31.text()),
                                                    delay_ms=int(self.ui.num_label_30.text()),
                                                    decay=float(self.ui.num_label_29.text()),
                                                    iterations=int(self.ui.num_label_27.text()))
                self.Box = QMessageBox()
                self.Box.setWindowTitle("混响完成")
                self.Box.setText(f"混响文件已保存至 Play List/混响/{self.path_music} v9.mp3")
                self.Box.setIcon(QMessageBox.Information)
                self.Box.exec()
                os.startfile(f"..\\..\\Play List\\混响\\{self.path_music} v9.mp3")

        except FileNotFoundError as e:
            self.Box = QMessageBox()
            self.Box.setWindowTitle("混响失败")
            self.Box.setText(f"混响器发生错误\n{e}\n发生当前错误可能是因为您的电脑上缺失FFmpeg解码器\n如果您刚安装了FFmpeg解码器 您可以重启程序再试一次")
            self.Box.setIcon(QMessageBox.Critical)
            self.Box.exec()
            print(e)
        except Exception as a:
            self.Box = QMessageBox()
            self.Box.setWindowTitle("混响失败")
            self.Box.setText(f"混响器发生错误\n{a}")
            self.Box.setIcon(QMessageBox.Critical)
            self.Box.exec()
            print(a)


if __name__ == "__main__":
    Reverberator()
