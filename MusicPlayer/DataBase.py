import mmap
import os
import platform
from pathlib import Path
from typing import Optional


# 遍历数据库
def traverse_item(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line.strip()

# 遍历数据库文件
def traverse_item_file(directory):
    item = []
    def traverse(path):
        """从文本文件中读取MP3路径并标准化格式"""
        with open(path, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                if line.endswith('.mp3'):
                    # 标准化路径格式为XXX/XXX/XXX.mp3
                    yield line.replace('\\', '/')

    for mp3_file in traverse(directory):
        item.append(mp3_file)
    return item



# 添加项
def add_item(filepath: str, str_file: str) -> None:
    """
    高效追加两个字符串到文件（自动换行）

    参数:
        filepath: 目标文件路径
        str1: 要写入的第一个字符串
        str2: 要写入的第二个字符串
    """
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"{str_file}\n")

# 删除项
def remove_item(filepath: str, target_str: str) -> None:
    """
    参数:
        filepath: 目标文件路径
        target_str: 要删除的目标字符串（支持多行匹配）
    """
    temp_path = f"{filepath}.tmp"
    found = False
    newline = '\n' if platform.system() != 'Windows' else '\r\n'

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            with open(temp_path, 'wb') as tmp:  # 改为二进制写入
                for line in iter(mm.readline, b''):
                    if not found:
                        try:
                            # 处理可能存在的编码问题
                            line_str = line.decode('utf-8', errors='replace')
                            if target_str in line_str:
                                found = True
                                continue
                        except UnicodeDecodeError:
                            # 跳过非UTF-8行
                            pass
                    # 直接写入原始字节，保留所有格式
                    tmp.write(line)

    if found:
        os.replace(temp_path, filepath)
    else:
        os.remove(temp_path)

# 检查项
def check_item(filepath: str, target_str: str) -> bool:
    """
    检查文件中是否包含目标字符串

    参数:
        filepath: 目标文件路径
        target_str: 要查找的字符串

    返回:
        bool: 是否找到目标字符串
    """
    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for line in iter(mm.readline, b''):
                try:
                    line_str = line.decode('utf-8', errors='replace')
                    if target_str in line_str:
                        return True
                except UnicodeDecodeError:
                    pass
    return False

# 查找项
def search_item(file_path: str, target_filename: str) -> Optional[str]:
    """
    从文件中逐行读取路径并查找目标文件名的父目录

    参数:
        file_path: 包含路径字符串的文件路径
        target_filename: 要查找的文件名(不带扩展名)

    返回:
        str: 第一个匹配到的父目录名称，未找到则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 使用 pathlib 解析路径
                path = Path(line)
                if not path.name:  # 确保路径不为空
                    continue

                # 获取文件名（不带扩展名）
                file_stem = path.stem  # 例如 'BABYDOLL' 来自 'BABYDOLL.mp3'
                if file_stem == target_filename:
                    parent_dir = path.parent.name  # 获取父目录名称
                    return parent_dir
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
    except Exception as e:
        print(f"读取文件时出错: {e}")

    return None