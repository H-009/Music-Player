import json
import logging
import os
import shutil
from typing import Union, Optional, Tuple


# 读取JSON 全读
def json_all_read(source):
    """
    读取JSON全部数据
    """
    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# 读取json
def json_read(source: Union[str, dict], key_path: str, default=None):
    """
    通过键路径从JSON文件或字典中提取值
    :param source: JSON文件路径或字典对象
    :param key_path: 键路径（支持嵌套如"user.address.city"）
    :param default: 键不存在时返回的默认值
    :return: 匹配的值或默认值
    """
    try:
        # 处理文件路径或直接传入的字典
        data = source if isinstance(source, dict) else json.load(open(source))

        # 分割嵌套路径
        keys = key_path.split('.')
        value = data

        # 递归查找嵌套键
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
    except (FileNotFoundError, json.JSONDecodeError, AttributeError):
        return default

# 写入json
def json_write(target: Union[str, dict], key_path: str, value, create_missing: bool = True):
    """
    通过键路径向JSON文件或字典中写入值
    :param target: JSON文件路径或字典对象
    :param key_path: 键路径（支持嵌套如"user.address.city"）
    :param value: 要写入的值
    :param create_missing: 是否自动创建缺失的中间键（默认为True）
    :return: 成功返回True，失败返回False
    """
    try:
        # 处理文件路径或直接传入的字典
        if isinstance(target, str):
            try:
                with open(target, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {}
        else:
            data = target.copy() if target else {}

        # 分割嵌套路径
        keys = key_path.split('.')
        current = data

        # 遍历到倒数第二个键
        for key in keys[:-1]:
            if key not in current and create_missing:
                current[key] = {}
                current = current[key]
            elif isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False

        # 设置最终键的值
        last_key = keys[-1]
        current[last_key] = value

        # 如果是文件路径，写回文件
        if isinstance(target, str):
            with open(target, 'w') as f:
                json.dump(data, f, indent=4)

        return True
    except (TypeError, PermissionError, json.JSONDecodeError):
        return False

#读取AMC配置文件
def amc_read(path):
    with open (path,'r',encoding="UTF-8") as file:
        data = file.read()

    return data


#写入AMC配置文件
def amc_write(path,data):
    with open (path,'w',encoding="UTF-8") as file:
        file.write(data)

#读取AMS统计文件
def ams_read(path):
    with open (path,'r') as file:
        data = file.read()

    return data


#写入AMS统计文件
def ams_write(path,data):
    with open (path,'w') as file:
        file.write(data)


#读取QSS主题文件
def qss_read(path):
    with open (path,'r',encoding="UTF-8") as file:
        data = file.read()

    return data


#AMS整数化处理
def process_ams_file(ams_path, b):
    with open(ams_path, 'r', encoding='utf-8') as file:
        a = file.read()

    with open(ams_path, 'w', encoding='utf-8') as f:
        a = int(a)+b
        f.write(str(a))

#读取AMT指定行
def amt_read(file_path: str, line_number: int) -> str:
    """
    读取指定文件的特定行

    Args:
        file_path (str): 目标文件的路径
        line_number (int): 要读取的行号（从1开始计数）

    Returns:
        str: 读取到的行内容（自动去除首尾空白字符）

    Raises:
        FileNotFoundError: 文件不存在时抛出
        ValueError: 行号超出文件实际行数时抛出
    """
    # 检查行号有效性
    if line_number < 1:
        raise ValueError("行号必须 >= 1")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 逐行读取直到目标行
            for current_line, line_content in enumerate(file, start=1):
                if current_line == line_number:
                    return line_content.strip()

            # 如果循环结束仍未找到目标行
            raise ValueError(f"文件只有 {current_line} 行，无法读取第 {line_number} 行")

    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")


#读取AMF指定行
def amf_read(file_path: str, line_number: int) -> str:
    """
    读取指定文件的特定行

    Args:
        file_path (str): 目标文件的路径
        line_number (int): 要读取的行号（从1开始计数）

    Returns:
        str: 读取到的行内容（自动去除首尾空白字符）

    Raises:
        FileNotFoundError: 文件不存在时抛出
        ValueError: 行号超出文件实际行数时抛出
    """
    # 检查行号有效性
    if line_number < 1:
        raise ValueError("行号必须 >= 1")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 逐行读取直到目标行
            for current_line, line_content in enumerate(file, start=1):
                if current_line == line_number:
                    return line_content.strip()

            # 如果循环结束仍未找到目标行
            raise ValueError(f"文件只有 {current_line} 行，无法读取第 {line_number} 行")

    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")


#写入AMT指定行
def amt_write(file_path, line_number, content):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 确保 line_number 是有效的索引
        if line_number > len(lines):
            # 若行号超出文件行数，填充空行直到指定行号
            lines.extend(['\n'] * (line_number - len(lines)))

        # 插入或替换指定行的内容
        lines[line_number - 1] = content + '\n'

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到。")
    except Exception as e:
        print(f"发生未知错误: {e}")

def delete_file(
        file_path: Union[str, os.PathLike],
        logger: Optional[logging.Logger] = None,
        raise_errors: bool = False
) -> bool:
    """
    安全删除指定路径的文件

    Args:
        file_path: 要删除的文件路径(字符串或PathLike对象)
        logger: 可选的日志记录器对象
        raise_errors: 是否抛出异常(False时仅返回False)

    Returns:
        bool: 是否成功删除(文件不存在视为成功)

    """
    try:
        if not os.path.exists(file_path):
            if logger:
                logger.debug(f"文件不存在，无需删除: {file_path}")
            return True

        if not os.path.isfile(file_path):
            if logger:
                logger.error(f"路径不是文件: {file_path}")
            if raise_errors:
                raise ValueError(f"路径不是文件: {file_path}")
            return False

        os.remove(file_path)

        # 验证是否删除成功
        if os.path.exists(file_path):
            if logger:
                logger.error(f"文件删除失败: {file_path}")
            if raise_errors:
                raise RuntimeError(f"文件删除失败: {file_path}")
            return False

        if logger:
            logger.info(f"文件已删除: {file_path}")
        return True

    except PermissionError as e:
        if logger:
            logger.error(f"权限不足，无法删除文件 {file_path}: {str(e)}")
        if raise_errors:
            raise
        return False

    except Exception as e:
        if logger:
            logger.error(f"删除文件时发生意外错误 {file_path}: {str(e)}", exc_info=True)
        if raise_errors:
            raise
        return False


def delete_folder(folder_path):
    try:
        """删除文件夹及其所有内容

        参数:
            folder_path (str): 要删除的文件夹路径
        """
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"成功删除文件夹: {folder_path}")
        else:
            print(f"文件夹不存在: {folder_path}")
    except Exception as a:
        print(a)


def rename_file(
        file_path: str,
        new_name: str,
        keep_extension: bool = True,
        overwrite: bool = True
) -> Tuple[bool, str]:
    """
    重命名文件（可选保留后缀名）

    Args:
        file_path:  原始文件路径（如 "/path/to/old_name.txt"）
        new_name:   新文件名（不含路径）
        keep_extension: 是否保留原后缀（默认 True）
        overwrite:  是否覆盖同名文件（默认 False）

    Returns:
        Tuple[是否成功, 新路径或错误消息]
    """
    # 参数校验
    if not os.path.exists(file_path):
        return False, "原始文件不存在"
    if not new_name.strip():
        return False, "新文件名不能为空"

    # 分离路径、文件名和后缀
    dir_path, full_name = os.path.split(file_path)
    name_part, ext_part = os.path.splitext(full_name)

    # 构造新文件名
    new_basename = f"{new_name}{ext_part}" if keep_extension else new_name
    new_path = os.path.join(dir_path, new_basename)

    # 检查文件冲突
    if os.path.exists(new_path) and not overwrite:
        return False, "目标文件已存在（启用 overwrite=True 可覆盖）"

    # 执行重命名
    os.rename(file_path, new_path)
    return True, new_path


def rename_folder(
        folder_path: str,
        new_name: str,
        overwrite: bool = False
) -> Tuple[bool, str]:
    """
    重命名文件夹（纯静态函数，无业务逻辑）

    Args:
        folder_path: 原始文件夹路径 (e.g. "/path/to/old_folder")
        new_name: 新文件夹名称 (e.g. "new_folder")
        overwrite: 是否覆盖已存在的文件夹 (默认False)

    Returns:
        Tuple[是否成功, 新路径或错误消息]
    """
    # 参数校验
    if not os.path.isdir(folder_path):
        return False, "原始文件夹不存在"
    if not new_name.strip():
        return False, "新文件夹名不能为空"

    # 构造新路径
    parent_dir = os.path.dirname(folder_path)
    new_path = os.path.join(parent_dir, new_name.strip())

    # 检查路径冲突
    if os.path.exists(new_path):
        if not overwrite:
            return False, "目标文件夹已存在（启用 overwrite=True 可覆盖）"
        try:
            shutil.rmtree(new_path)  # 删除已存在的文件夹
        except Exception as e:
            return False, f"无法删除已存在文件夹: {str(e)}"

    # 执行重命名
    try:
        os.rename(folder_path, new_path)  # 同一磁盘直接重命名
        return True, new_path
    except OSError:
        try:
            shutil.move(folder_path, new_path)  # 跨磁盘移动
            return True, new_path
        except Exception as e:
            return False, f"重命名失败: {str(e)}"


def len_file(directory_path):
    """
    统计指定文件夹下的文件数量（不包含子目录）
    :param directory_path: 文件夹路径
    :return: 文件数量(int)
    """
    if not os.path.isdir(directory_path):
        raise ValueError("提供的路径不是有效文件夹")

    file_count = 0
    for item in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, item)):
            file_count += 1
    return file_count


def len_folder(directory_path, recursive=False):
    """
    统计指定路径下的文件夹数量
    :param directory_path: 目标文件夹路径
    :param recursive: 是否递归统计子目录（默认False）
    :return: 文件夹数量(int)
    :raises: ValueError 当路径无效时
    """
    if not os.path.isdir(directory_path):
        raise ValueError("提供的路径不是有效文件夹")

    dir_count = 0
    for entry in os.scandir(directory_path):
        if entry.is_dir():
            dir_count += 1
            if recursive:
                dir_count += len_folder(entry.path, recursive=True)
    return dir_count


def len_mp3_files(folder_path):
    """
    递归查找指定文件夹及其子文件夹中的所有MP3文件
    参数：
        folder_path (str): 要搜索的文件夹路径
    返回：
        list: 包含所有MP3文件完整路径的列表，按字母顺序排序
    """
    mp3_files = []

    # 验证路径有效性
    if not os.path.isdir(folder_path):
        raise ValueError(f"无效的文件夹路径: {folder_path}")

    # 使用os.walk递归遍历
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 不区分大小写的扩展名检查
            filename, ext = os.path.splitext(file)  # 解包元组获取扩展名‌:ml-citation{ref="2,7" data="citationList"}
            if ext.lower() == '.mp3' or ext.lower() == '.MP3':  # 对字符串调用lower()
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)

    # 按路径字母顺序排序
    return sorted(mp3_files, key=lambda x: x.lower())


def find_png_files(folder_path):
    """
    递归查找指定文件夹及其子文件夹中的所有PNG文件
    参数：
        folder_path (str): 要搜索的文件夹路径
    返回：
        list: 包含所有PNG文件完整路径的列表，按字母顺序排序
    """
    mp3_files = []

    # 验证路径有效性
    if not os.path.isdir(folder_path):
        raise ValueError(f"无效的文件夹路径: {folder_path}")

    # 使用os.walk递归遍历
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 不区分大小写的扩展名检查
            filename, ext = os.path.splitext(file)  # 解包元组获取扩展名‌:ml-citation{ref="2,7" data="citationList"}
            if ext.lower() == '.png':  # 对字符串调用lower()
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)

    # 按路径字母顺序排序
    return sorted(mp3_files, key=lambda x: x.lower())


def find_lrc_files(folder_path):
    """
    递归查找指定文件夹及其子文件夹中的所有PNG文件
    参数：
        folder_path (str): 要搜索的文件夹路径
    返回：
        list: 包含所有PNG文件完整路径的列表，按字母顺序排序
    """
    mp3_files = []

    # 验证路径有效性
    if not os.path.isdir(folder_path):
        raise ValueError(f"无效的文件夹路径: {folder_path}")

    # 使用os.walk递归遍历
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 不区分大小写的扩展名检查
            filename, ext = os.path.splitext(file)  # 解包元组获取扩展名‌:ml-citation{ref="2,7" data="citationList"}
            if ext.lower() == '.lrc':  # 对字符串调用lower()
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)

    # 按路径字母顺序排序
    return sorted(mp3_files, key=lambda x: x.lower())


def find_ttf_files(folder_path):
    """
    递归查找指定文件夹及其子文件夹中的所有PNG文件
    参数：
        folder_path (str): 要搜索的文件夹路径
    返回：
        list: 包含所有PNG文件完整路径的列表，按字母顺序排序
    """
    mp3_files = []

    # 验证路径有效性
    if not os.path.isdir(folder_path):
        raise ValueError(f"无效的文件夹路径: {folder_path}")

    # 使用os.walk递归遍历
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 不区分大小写的扩展名检查
            filename, ext = os.path.splitext(file)  # 解包元组获取扩展名‌:ml-citation{ref="2,7" data="citationList"}
            if ext.lower() == '.ttf':  # 对字符串调用lower()
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)

    # 按路径字母顺序排序
    return sorted(mp3_files, key=lambda x: x.lower())


def find_amt_files(folder_path):
    """
    递归查找指定文件夹及其子文件夹中的所有PNG文件
    参数：
        folder_path (str): 要搜索的文件夹路径
    返回：
        list: 包含所有PNG文件完整路径的列表，按字母顺序排序
    """
    mp3_files = []

    # 验证路径有效性
    if not os.path.isdir(folder_path):
        raise ValueError(f"无效的文件夹路径: {folder_path}")

    # 使用os.walk递归遍历
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 不区分大小写的扩展名检查
            filename, ext = os.path.splitext(file)  # 解包元组获取扩展名‌:ml-citation{ref="2,7" data="citationList"}
            if ext.lower() == '.amt':  # 对字符串调用lower()
                full_path = os.path.join(root, file)
                mp3_files.append(full_path)

    # 按路径字母顺序排序
    return sorted(mp3_files, key=lambda x: x.lower())

# 字符串布尔类型
def str_bool(s):
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        return None

