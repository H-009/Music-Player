import binascii
import secrets
import subprocess
import uuid
from datetime import datetime
import plyer
import wmi
from PyQt5.QtWidgets import QMessageBox


def write_2(text: str, filename: str) -> None:
    """将字符串直接转换为二进制写入文件(默认UTF-8编码)

    Args:
        text: 要写入的原始字符串
        filename: 输出文件名（如 license.bin）
    """
    byte_array = text.encode("GBK")
    text = ''.join([bin(byte)[2:].zfill(8) for byte in byte_array])

    with open(filename, 'wb') as f:
        f.write(text.encode('GBK'))  # 无额外处理


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

#写入16进制
def write_16(s, path):
    hex_str = binascii.hexlify(s.encode("UTF-8")).decode()
    hex_key = ''.join(f'\\Ox{hex_str[i:i + 2]}' for i in range(0, len(hex_str), 2))

    with open(path, 'wb') as f:
        f.write(hex_key.encode('UTF-8'))  # 无额外处理

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

#修改
def modify_16(file_path):
    """
    修改16进制编码文件中的特定键值对

    参数:
        file_path (str): 目标文件路径
        target_key (str): 需要修改的键名
        new_value (str): 新的键值内容

    返回:
        bool: 修改是否成功
    """
    keys = parse_key_value_pairs(read_16(file_path))

    write_16(f"ProductName:{keys['ProductName']};\n"  # 产品标识
             f"ProductVersion:{keys['ProductVersion']};\n"  # 版本号
             f"LicenseType:{keys['LicenseType']};\n"  # 激活模式
             f"Features:{keys['Features']};\n"  # 高级功能权限

             # 硬件绑定组
             f"UUID:{keys['UUID']};\n"  # 设备唯一标识
             f"MotherboardUID:{keys['MotherboardUID']};\n"  # 主板物理指纹

             # 授权验证组
             f"LicenseID:{keys['LicenseID']};\n"  # 许可证唯一编码
             f"LicenseKey:{keys['LicenseKey']};\n"  # 加密激活密钥
             f"ValidityPeriodType:{keys['ValidityPeriodType']};\n"  # 时效类型
             f"IssuedDate:{keys['IssuedDate']};\n"  # 签发时间戳  
             f"ValidityPeriod:{keys['ValidityPeriod']};\n"  # 有效时长配置
             "Activation:True;"  # 激活状态

             # 版权元数据组
             f"DigitalSignature:{keys['DigitalSignature']};\n"  # 数字签名算法
             f"AuthorizationInformation:{keys['AuthorizationInformation']};\n"  # 授权引擎版本
             f"Copyright:{keys['Copyright']}"  # 版权信息

             , file_path)

def get_board_uuid():
    try: # powershell 修正版 不使用wmic
        cmd = 'powershell (Get-WmiObject Win32_ComputerSystemProduct).UUID'
        output = subprocess.check_output(cmd, shell=True)
        return output.decode().strip()
    except Exception as e:
        return f"Error: {str(e)}"


def generate_secure_key(length=25, group_size=5):
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    # 生成随机字节序列
    rand_bytes = secrets.token_bytes(length)

    # 将字节映射到字符集
    key = []
    for byte in rand_bytes:
        index = byte % len(charset)  # 取模确保均匀分布
        key.append(charset[index])

    # 按分组格式拼接
    grouped = '-'.join(
        ''.join(key[i:i + group_size])
        for i in range(0, length, group_size)
    )
    return grouped


def wmi_pc():
    motherboard_wmi = wmi.WMI()
    for product in motherboard_wmi.Win32_ComputerSystemProduct():
        return product.UUID.replace('-', '')


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

#当前时间
def Time():
    """返回当前时间，格式为YYYY-MM-DD HH:MM"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")

#时间比较
def compare_time_str(time_str1, time_str2):
    """
    比较两个时间字符串的大小
    参数格式必须为'YYYY-MM-DD HH:MM'
    返回:
        -1 如果time_str1 < time_str2
        0  如果time_str1 == time_str2
        1  如果time_str1 > time_str2
    """
    try:
        t1 = datetime.strptime(time_str1, "%Y-%m-%d %H:%M")
        t2 = datetime.strptime(time_str2, "%Y-%m-%d %H:%M")
        return -1 if t1 < t2 else (1 if t1 > t2 else 0)
    except ValueError as e:
        raise ValueError("时间格式必须为'YYYY-MM-DD HH:MM'") from e


def Activation_End(ico):
    plyer.notification.notify(
        title="激活通知",
        message="Music Player 21 Bate已在此计算机上永久激活",
        app_name="Music Player 21",
        app_icon=ico,
    )


def Logout(path):

    write_16("ProductName:None;\n"  # 产品名称
             "ProductVersion:None;\n"  # 版本号
             "LicenseType:None;\n"  # 激活模式
             "Features:None;\n"  # 高级功能权限

             # 硬件绑定组
             f"UUID:None;\n"  # 设备唯一标识
             f"MotherboardUID:None;\n"  # 主板物理指纹

             # 授权验证组
             f"LicenseID:None;\n"  # 许可证唯一编码
             f"LicenseKey:None;\n"  # 加密激活密钥
             f"ValidityPeriodType:None;\n"  # 时效类型
             f"IssuedDate:None;\n"  # 签发时间戳
             f"ValidityPeriod:None;\n"  # 有效时长配置
             "Activation:None;"  # 激活状态

             # 版权元数据组
             "DigitalSignature:None;\n"  # 数字签名
             "AuthorizationInformation:None;\n"  # 授权信息
             "Copyright:None"  # 版权信息

             , path)

def Write(path):
    time = "Permanent"  # or 2025-5-9 11:21:31
    time_type = "Temporary"  # or Perpetual
    time_begin = "2025-5-9 14:03:21"
    key = generate_secure_key()

    write_16("ProductName:Music Player 21 Bate;\n"  # 产品名称
             "ProductVersion:1.3.21 Bate;\n"  # 版本号
             "LicenseType:Local;\n"  # 激活模式
             "Features:Bate,API;\n"  # 高级功能权限
    
             # 硬件绑定组
             f"UUID:{wmi_pc()};\n"  # 设备唯一标识
             f"MotherboardUID:{wmi_pc()};\n"  # 主板物理指纹
    
             # 授权验证组
             f"LicenseID:{uuid.uuid4()};\n"  # 许可证唯一编码
             f"LicenseKey:{key};\n"  # 加密激活密钥
             f"ValidityPeriodType:{time_type};\n"  # 时效类型
             f"IssuedDate:{time_begin};\n"  # 签发时间戳
             f"ValidityPeriod:{time};\n"  # 有效时长配置
             "Activation:False;"  # 激活状态
    
             # 版权元数据组
             "DigitalSignature:Music Player 21 Bate;\n"  # 数字签名
             "AuthorizationInformation:Artificial Python 1.4;\n"  # 授权信息
             "Copyright:STD Studio"  # 版权信息

             , path+".lic")

    write_2(key,"secret key.key")

def Read(path):
    keys = parse_key_value_pairs(read_16(path))

    return keys

def Write_Key(path):
    a = generate_secure_key()
    write_2(a,path)

def Read_Key(path):
    key = read_2(path)
    return key

def show_license_activation():
    box = QMessageBox()
    box.setWindowTitle("激活许可")
    box.setText("是否立即激活当前许可证")
    box.setIcon(QMessageBox.Warning)

    confirm_btn = box.addButton("激活", QMessageBox.YesRole)
    cancel_btn = box.addButton("稍后激活", QMessageBox.NoRole)
    box.setDefaultButton(cancel_btn)

    box.exec_()
    return box.clickedButton() == confirm_btn


if __name__ == "__main__":
    Write("111")