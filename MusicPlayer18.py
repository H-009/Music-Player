# 版权所有（C）[STD Studio][2025]
# 该软件使用PyQt5 PySide5（LGPL v3.0）作为GUI组件.
# PyQt5版权所有（C） Riverbank Computing Limited.
# 有关详细信息，请参阅发行版中的LICENSE.PyQt5.

import sys
from datetime import datetime

from MusicServicePlus import MusicVerifyer, MusicFileService
from MusicServicePlus import MusicMessageBox
import MusicBase

import MusicMain
import MusicTrial

class Door:
    def __init__(self):
        self.app_version = "Base"

        try:
            # 读取解码后的许可证
            self.file_lic = MusicVerifyer.Read(MusicFileService.FileService().amc_read("Config/license currently use.amc"))
        except FileNotFoundError:
            m = MusicBase.MainUI()
            m.MainWindow()
            key = MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                             "许可证损坏或丢失")
            m.Run()

        try:
            # 读取解码后的密钥
            self.file_keys = MusicVerifyer.read_2("Data/secret key.key")
        except FileNotFoundError:
            m = MusicBase.MainUI()
            m.MainWindow()
            key = MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                             "密钥损坏或丢失")
            if not key:
                sys.exit()
            m.Run()

        # 读取产品名称
        self.file_name = self.file_lic["ProductName"]
        # 读取产品版本
        self.file_version = self.file_lic["ProductVersion"]
        # 读取激活模式
        self.file_type = self.file_lic["LicenseType"]
        # 读取高级功能权限
        self.file_api = self.file_lic["Features"]

        # 读取UUID
        self.file_uuid = self.file_lic["UUID"]
        # 读取主板指纹
        self.file_uid = self.file_lic["MotherboardUID"]

        # 读取许可证编码
        self.file_id = self.file_lic["LicenseID"]
        # 读取加密密钥
        self.file_key = self.file_lic["LicenseKey"]
        # 读取时效类型
        self.file_date = self.file_lic["ValidityPeriodType"]
        # 读取签发时间戳
        self.file_begin_time = self.file_lic["IssuedDate"]
        # 读取有效时长
        self.file_end_time = self.file_lic["ValidityPeriod"]
        # 读取激活状态
        self.file_state = self.file_lic["Activation"]

        # 读取数字签名
        self.file_DigitalSignature = self.file_lic["DigitalSignature"]
        # 读取授权信息
        self.file_AuthorizationInformation = self.file_lic["AuthorizationInformation"]
        # 读取版权信息
        self.file_Copyright = self.file_lic["Copyright"]

        # 读取本机UID
        self.pc_uuid = MusicVerifyer.get_board_uuid()
        # 读取主板指纹
        self.pc_uid = MusicVerifyer.wmi_pc()
        # 读取当前时间
        self.pc_time = datetime.now().strftime("%Y-%#m-%#d")

        super().__init__()

    def update_base_data(self):
        # 如果产品名称不合规
        if self.file_name not in ["Music Player 18", "Music Player 18 Plus", "Music Player 18 Trial"]:
            print(0)
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无许可")
            print(101)
            m.Run()
        else:
            if self.file_name == "Music Player 18":
                self.app_version = "Trial"
            elif self.file_name == "Music Player 18 Plus":
                self.app_version = "Plus"
            elif self.file_name == "Music Player 18 Trial":
                self.app_version = "Trial"

        # 如果产品版本不合规
        if self.file_version not in ["1.3.18", "1.3.18 Plus", "1.3.18 Trial"]:
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无许可")
            print(202)
            m.Run()
        else:
            if self.file_version == "Music Player 18":
                self.app_version = "Trial"
            elif self.file_version == "Music Player 18 Plus":
                self.app_version = "Plus"
            elif self.file_version == "Music Player 18 Trial":
                self.app_version = "Trial"

        # 如果激活模式不合规
        if self.file_type not in ["Local", "Temporary"]:
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无许可")
            print(303)
            m.Run()

        # 如果高级功能权限不合规
        if self.file_api not in ["Trial,API", "Plus,API"]:
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无权限")
            print(404)
            m.Run()
        else:
            if self.file_api == "Trial,API":
                self.app_version = "Trial"
            elif self.file_api == "Plus,API":
                self.app_version = "Plus"

    # 更新身份验证
    def update_key_id(self):
        print(1010)
        try:
            # 如果UUID不相同 UID相同
            print(self.file_uid, self.pc_uid)

            if self.file_uuid != self.pc_uuid and self.file_uid == self.pc_uid:
                print(505)
                m = MusicTrial.MainUI()
                m.MainWindow()
                MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                       "许可已失效 请尽快更换许可证")
                m.Run()
            # 如果UUID不相同 UID不相同
            elif self.file_uuid != self.pc_uuid and self.file_uid != self.pc_uid:
                print(606)
                m = MusicTrial.MainUI()
                m.MainWindow()
                MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误","发生错误：许可地址失效")
                m.Run()
        except Exception as a: print(a)

    # 更新验证信息
    def update_key_time(self):
        # 时效判断
        if self.file_date != "Permanent":
            if self.file_end_time == self.pc_time:
                m = MusicBase.MainUI()
                m.MainWindow()
                MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                       "许可已过期 请尽快更换许可证")
                print(707)
                m.Run()

        # 密钥判断
        if self.file_state != "True":
            print(808)
            if self.file_key == self.file_keys and self.app_version == "Trial" and self.file_date != "Permanent":
                print(100)
                m = MusicTrial.MainUI()
                m.MainWindow()
                key = MusicMessageBox.Box.Activation(m.music.MusicPlayer_Bottom_Widget)
                if key:
                    MusicVerifyer.modify_16(MusicFileService.FileService().amc_read("Config/license currently use.amc"))
                    MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "激活成功",
                                                     "许可证已在您的电脑上临时激活")
                    MusicVerifyer.Activation_End("Trial Temp","MusicIco.ico")
                    dialog = MusicVerifyer.AutoCloseDialog(seconds=10)
                    dialog.show()

                m.Run()
            if self.file_key == self.file_keys and self.app_version == "Trial" and self.file_date == "Permanent":
                print(200)
                m = MusicTrial.MainUI()
                m.MainWindow()
                key = MusicMessageBox.Box.Activation(m.music.MusicPlayer_Bottom_Widget)
                if key:
                    MusicVerifyer.modify_16(MusicFileService.FileService().amc_read("Config/license currently use.amc"))
                    MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "激活成功",
                                                     "许可证已在您的电脑上临时激活")
                    MusicVerifyer.Activation_End("Trial","MusicIco.ico")
                    dialog = MusicVerifyer.AutoCloseDialog(seconds=10)
                    dialog.show()
                m.Run()

            if self.file_key == self.file_keys and self.app_version == "Plus" and self.file_date != "Permanent":
                print(300)
                m = MusicTrial.MainUI()
                m.MainWindow()
                key = MusicMessageBox.Box.Activation(m.music.MusicPlayer_Bottom_Widget)
                if key:
                    MusicVerifyer.modify_16(MusicFileService.FileService().amc_read("Config/license currently use.amc"))
                    MusicVerifyer.Activation_End("Plus Temp","MusicIco.ico")
                    dialog = MusicVerifyer.AutoCloseDialog(seconds=10)
                    dialog.show()
                m.Run()

            if self.file_key == self.file_keys and self.app_version == "Plus" and self.file_date == "Permanent":
                print(400)
                m = MusicTrial.MainUI()
                m.MainWindow()
                key = MusicMessageBox.Box.Activation(m.music.MusicPlayer_Bottom_Widget)
                if key:
                    MusicVerifyer.modify_16(MusicFileService.FileService().amc_read("Config/license currently use.amc"))
                    MusicVerifyer.Activation_End("Plus","MusicIco.ico")
                    dialog = MusicVerifyer.AutoCloseDialog(seconds=10)
                    dialog.show()
                m.Run()
            if self.file_key != self.file_keys:
                print(500)
                print(self.file_key,self.file_keys)
                m = MusicTrial.MainUI()
                m.MainWindow()
                MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                       "发生错误：无密钥")
                m.Run()

    # 更新许可证信息
    def update_lic_data(self):
        # 如果数字签名不合规
        if self.file_DigitalSignature not in ["Music Player 18", "Music Player 18 Plus", "Music Player 18 Trial"]:
            print(111)
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无法识别该许可")
            m.Run()

        # 如果授权信息不合规
        if self.file_AuthorizationInformation not in ["AP1.3", "Artificial Python 1.3", "STD 3"]:
            print(222)
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无法识别该许可")
            m.Run()

        # 如果授权信息不合规
        if self.file_Copyright not in ["STD Studio", "STD AP"]:
            print(333)
            m = MusicBase.MainUI()
            m.MainWindow()
            MusicMessageBox.Box.Critical_Box(m.music.MusicPlayer_Bottom_Widget, "验证错误",
                                                   "发生错误：无法识别该许可")
            m.Run()


    def Main(self):

        # 更新基础信息
        self.update_base_data()

        # 更新基础信息
        self.update_key_id()

        # 更新验证信息
        self.update_key_time()

        # 更新许可证信息
        self.update_lic_data()

        # 启动试用版
        if self.app_version == "Trial":
            print(000)
            m = MusicTrial.MainUI()
            m.MainWindow()
            m.Run()
        # 启动升级版
        elif self.app_version == "Plus":
            print(000)
            MusicMain.MainUI().MainWindow()

if __name__ == "__main__":
    Door().Main()


