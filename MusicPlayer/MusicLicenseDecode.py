import binascii
import os

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker


#读取二进制
def read_2(file_path: str) -> str:
    """读取由write_2生成的二进制文件并还原原始字符串

    Args:
        file_path: 二进制文件路径（如 license.bin）

    Returns:
        还原后的原始字符串

    Raises:
        FileNotFoundError: 文件不存在时抛出
        UnicodeDecodeError: GBK解码失败时抛出
    """
    # 读取二进制数据（GBK编码的二进制字符串）
    with open(file_path, 'rb') as f:
        binary_data = f.read().decode('GBK')  # 先解码为二进制字符串文本:ml-citation{ref="3,5" data="citationList"}

    # 将8位二进制字符串分割为字节列表
    byte_list = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]

    # 将二进制字符串转换为整数后组装为字节数组
    byte_array = bytes([int(b, 2) for b in byte_list])  # 二进制字符串转字节:ml-citation{ref="2,3" data="citationList"}

    # GBK解码还原原始字符串
    return byte_array.decode('GBK', errors='strict')  # 严格模式避免乱码:ml-citation{ref="1,5" data="citationList"}


#读取16进制
def read_16(input_file, output_file=None):
    """
    从文件读取加密字符串并解密，支持输出到文件或直接返回结果

    参数:
        input_file (str): 加密文件路径
        output_file (str): 解密结果保存路径（可选）

    返回:
        str: 解密后的原始字符串

    示例:
        decrypt_file("encrypted.txt", "decrypted.txt")
    """
    # Step 1: 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        encrypted_str = f.read().strip()  # 去除首尾空白字符

    # Step 2: 提取16进制片段
    hex_parts = encrypted_str.split("\\Ox")[1:]  # 过滤空字符

    # Step 3: 拼接完整16进制串
    hex_str = ''.join(hex_parts)

    # Step 4: 转换为字节数据
    byte_data = binascii.unhexlify(hex_str)

    # Step 5: 解码为原始字符串
    result = byte_data.decode('GBK')

    # Step 6: 可选输出到文件
    if output_file:
        with open(output_file, 'w', encoding='GBK') as f:
            f.write(result)

    return result


#格式化
def parse_key_value_pairs(data_str: str) -> dict:
    """
    解析键值对字符串并返回字典
    输入格式示例："Key1:Value1;Key2:Value2;..."
    """
    result = {}
    # 按分号分割键值对列表
    pairs = [p.strip() for p in data_str.split(';') if p.strip()]  #:ml-citation{ref="4,6" data="citationList"}

    for pair in pairs:
        # 分割键值并移除空格
        if ':' in pair:
            key, value = pair.split(':', 1)  # 分割一次防止值中含冒号
            result[key.strip()] = value.strip()  #:ml-citation{ref="5" data="citationList"}
    return result

def ProductName(file_path):
    result = parse_key_value_pairs(read_16(file_path))
    return result["ProductName"]

class LicensePath(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        try:
            key = os.path.exists(self.file_path)
            result = parse_key_value_pairs(read_16(self.file_path))

            if self._check_running():
                if not key:
                    self.decode_finished.emit("丢失")
                elif result["ProductName"] == "None":
                    self.decode_finished.emit("无效")
                elif key:
                    self.decode_finished.emit("使用中")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("丢失")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderName(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("产品名称 解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))

            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit(result["ProductName"])
                if result["ProductName"] == "None":
                    self.decode_finished.emit("未知产品")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("产品名称  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderVersion(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("产品版本  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit(result["ProductVersion"])
                if result["ProductVersion"] == "None":
                    self.decode_finished.emit("未知版本号")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("产品版本  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderType(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("激活模式  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                if result["LicenseType"] == "Local":
                    self.decode_finished.emit("激活模式  本地激活")
                elif result["LicenseType"] == "Temporary":
                    self.decode_finished.emit("激活模式  临时激活")
                else:
                    self.decode_finished.emit("激活模式  无效模式")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("激活模式  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderFeatures(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("功能权限  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("功能权限  "+result["Features"])
                if result["Features"] == "None":
                    self.decode_finished.emit("功能权限  无权限")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("功能权限  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderUUID(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("唯一标识  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("唯一标识  "+result["UUID"])
                if result["UUID"] == "None":
                    self.decode_finished.emit("唯一标识  未知")


        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("唯一标识  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderUID(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("主板指纹  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("主板指纹  "+result["MotherboardUID"])
                if result["MotherboardUID"] == "None":
                    self.decode_finished.emit("主板指纹  未知")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("主板指纹  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderID(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("许可编号  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("许可编号  "+result["LicenseID"])
                if result["LicenseID"] == "None":
                    self.decode_finished.emit("许可编号  未知")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("许可编号  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderKey(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("激活秘钥  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("激活秘钥  "+result["LicenseKey"])
                if result["LicenseKey"] == "None":
                    self.decode_finished.emit("激活秘钥  缺失")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("激活秘钥  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderTimeType(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("时效类型  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")

                if result["ValidityPeriodType"] == "Temporary":
                    self.decode_finished.emit("时效类型  临时")
                elif result["ValidityPeriodType"] == "Permanent":
                    self.decode_finished.emit("时效类型  永久")
                elif result["ValidityPeriodType"] == "Trial":
                    self.decode_finished.emit("时效类型  试用")
                else:
                    self.decode_finished.emit("时效类型  无效")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("时效类型  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderBeginDate(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("签发时间  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("签发时间  " + result["IssuedDate"])
                if result["ProductName"] == "None":
                    self.decode_finished.emit("签发时间  未知")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("签发时间  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderEndDate(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("到期时间  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                if result["ValidityPeriod"] == "Permanent":
                    self.decode_finished.emit("到期时间  永久有效")
                elif result["ValidityPeriod"] == "Trial":
                    self.decode_finished.emit("到期时间  永久有效")
                else:
                    self.decode_finished.emit("到期时间  " + result["ValidityPeriod"])
                    if result["ProductName"] == "None":
                        self.decode_finished.emit("到期时间  未知")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("到期时间  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderActivation(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("激活状态  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                if result["Activation"] == "True":
                    self.decode_finished.emit("激活状态  已激活")
                elif result["Activation"] == "False":
                    self.decode_finished.emit("激活状态  未激活")
                else:
                    self.decode_finished.emit("激活状态  异常")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("激活状态  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderDigitalSignature(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("数字签名  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("数字签名  " + result["DigitalSignature"])
                if result["ProductName"] == "None":
                    self.decode_finished.emit("数字签名  不明")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("数字签名  解码失败")


    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderAuthorizationInformation(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("授权信息  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("授权信息  " + result["AuthorizationInformation"])
                if result["ProductName"] == "None":
                    self.decode_finished.emit("授权信息  不明")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("授权信息  解码失败")


    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)

class LicenseDecoderCopyright(QThread):
    """
    16进制文件解码线程
    初始化时接受文件路径，使用read_16函数解码并更新进度
    """
    decode_progress = pyqtSignal(int)  # 解码进度信号(0-100)
    status_updated = pyqtSignal(str)  # 状态更新信号
    decode_finished = pyqtSignal(str)  # 解码完成信号(携带结果)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = os.path.normpath(file_path)
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._update_status("开始解码...")
        self.decode_finished.emit("版权信息  解码中...")

        try:
            # 实际解码调用
            result = parse_key_value_pairs(read_16(self.file_path))


            if self._check_running():
                self._update_status("解码完成")
                self.decode_finished.emit("版权信息  " + result["Copyright"])
                if result["ProductName"] == "None":
                    self.decode_finished.emit("版权信息  不明")

        except Exception as e:
            self._update_status(f"解码错误  {str(e)}")
            self.decode_finished.emit("版权信息  解码失败")

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
            self._update_status("解码已中止")

    def _check_running(self):
        with QMutexLocker(self._mutex):
            return self._is_running

    def _update_status(self, text):
        with QMutexLocker(self._mutex):
            self.status_updated.emit(text)
