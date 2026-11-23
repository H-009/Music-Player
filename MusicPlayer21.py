# 版权所有（C）[STD Studio][2025]
# 该软件使用PyQt5 PySide5（LGPL v3.0）作为GUI组件.
# PyQt5版权所有（C） Riverbank Computing Limited.
# 有关详细信息，请参阅发行版中的LICENSE.PyQt5.

import sys
from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

from MusicPlayer.MusicService import MusicFileService
from MusicPlayer import MusicVerifyer
import MusicMain

class Door:
    def __init__(self):
        self.app_version = False
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon('MusicIco.ico'))

        try:
            # 读取解码后的许可证
            self.file_lic = MusicVerifyer.Read(MusicFileService.amc_read("Config/Local/license currently use.amc"))
        except FileNotFoundError:
            QMessageBox.critical(None, "验证错误", "许可证损坏或丢失")
            sys.exit()

        try:
            # 读取解码后的密钥
            self.file_keys = MusicVerifyer.read_2("Data/secret key.key")
        except FileNotFoundError:
            QMessageBox.critical(None, "验证错误", "密钥损坏或丢失")
            sys.exit()

        # 读取产品名称 版本
        self.file_name,self.file_version = self.file_lic["ProductName"],self.file_lic["ProductVersion"]

        # 读取激活模式 高级功能权限
        self.file_type,self.file_api = self.file_lic["LicenseType"],self.file_lic["Features"]

        # 读取UUID 主板指纹
        self.file_uuid,self.file_uid = self.file_lic["UUID"],self.file_lic["MotherboardUID"]

        # 读取许可证编码 加密密钥
        self.file_id,self.file_key = self.file_lic["LicenseID"],self.file_lic["LicenseKey"]
        # 读取时效类型 签发时间戳
        self.file_date,self.file_begin_time = self.file_lic["ValidityPeriodType"],self.file_lic["IssuedDate"]
        # 读取有效时长 激活状态
        self.file_end_time,self.file_state = self.file_lic["ValidityPeriod"],self.file_lic["Activation"]

        # 读取数字签名
        self.file_DigitalSignature = self.file_lic["DigitalSignature"]
        # 读取授权信息
        self.file_AuthorizationInformation = self.file_lic["AuthorizationInformation"]
        # 读取版权信息
        self.file_Copyright = self.file_lic["Copyright"]

        # 读取本机UID 主板指纹
        self.pc_uuid,self.pc_uid = MusicVerifyer.wmi_pc(),MusicVerifyer.wmi_pc()
        # 读取当前时间
        self.pc_time = datetime.now().strftime("%Y-%#m-%#d")

        super().__init__()

    # 更新基础信息
    def update_base_data(self):
        # 如果产品不合规
        key = True
        if self.file_version not in ["1.3.21", "1.3.21 Bate"] or self.file_name not in ["Music Player 21", "Music Player 21 Bate"]:
            QMessageBox.critical(None, "验证错误", "发生错误：无许可")
            print("无许可")
            key = False
        return key

    # 更新身份验证
    def update_key_id(self):
        try:
            key = True
            # 如果UUID不相同 UID不相同
            if self.file_uuid != self.pc_uuid and self.file_uid == self.pc_uid:
                key = False
                print(self.file_uuid,self.pc_uuid)
                QMessageBox.critical(None, "验证错误", "许可已失效 请尽快更换许可证")
            # 如果UUID不相同 UID不相同
            elif self.file_uuid != self.pc_uuid and self.file_uid != self.pc_uid:
                key = False
                QMessageBox.critical(None, "验证错误", "发生错误：许可地址失效")
            return key

        except Exception as a:
            print(a)

    # 更新验证信息
    def update_key_time(self):
        # 时效判断
        key = True
        if self.file_date != "Permanent":
            if self.file_end_time == self.pc_time:
                key = False
                QMessageBox.critical(None, "验证错误", "许可已过期 请尽快更换许可证")
        # 密钥判断
        if self.file_state != "True":

            key = MusicVerifyer.show_license_activation()
            if key:
                MusicVerifyer.modify_16(MusicFileService.amc_read("Config/Local/license currently use.amc"))
                MusicVerifyer.Activation_End("MusicIco.ico")

            if self.file_key != self.file_keys:
                key = False
                QMessageBox.critical(None, "激活错误", "发生错误：无密钥")

        return key

    # 更新许可证信息
    def update_lic_data(self):
        # 如果数字签名不合规
        key = True
        if self.file_DigitalSignature not in ["Music Player 21", "Music Player 21 Plus", "Music Player 21 Bate"]:
            print("数字签名不合规")
            key = False
            QMessageBox.critical(None, "验证错误", "发生错误：无法识别该许可")
        # 如果授权信息不合规
        if self.file_AuthorizationInformation not in ["AP1.4", "Artificial Python 1.4", "STD 4"]:
            print("授权信息不合规")
            key = False
            QMessageBox.critical(None, "验证错误", "发生错误：无法识别该许可")
        # 如果授权信息不合规
        if self.file_Copyright not in ["STD Studio", "STD AP"]:
            print("无法识别该许可")
            key = False
            QMessageBox.critical(None, "验证错误", "发生错误：无法识别该许可")

        return key

    def Main(self):
        # 更新基础信息
        key1 = self.update_base_data()
        # 更新基础信息
        key2 = self.update_key_id()
        # 更新验证信息
        key3 = self.update_key_time()
        # 更新许可证信息
        key4 = self.update_lic_data()

        # 启动
        if key4 and key3 and key2 and key1:
            print("许可验证通过")
            MusicMain.MainUI().MainWindow()

Door().Main()