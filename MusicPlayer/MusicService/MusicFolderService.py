import math
import shutil
import os


# 返回文件夹内的文件数量
def file_len(directory):
    count = 0
    for _, _, files in os.walk(directory):
        count += len(files)
    return count


#获取所有文件夹数量
def count_directories(path):
    try:
        # 列出指定目录下的所有文件和文件夹
        items = os.listdir(path)
        # 计数文件夹的数量
        directory_count = sum(1 for item in items if os.path.isdir(os.path.join(path, item)))
        return directory_count
    except FileNotFoundError:
        # 如果指定的路径不存在，则抛出异常或返回特定的错误值
        print(f"The directory '{path}' does not exist.")
        return 0
    except PermissionError:
        # 如果没有权限访问指定的路径，则抛出异常或返回特定的错误值
        print(f"Permission denied to access the directory '{path}'.")
        return 0


# 获取所有文件夹数量
def get_first_folder_name(directory_path):
    try:
        # 列出目录中的所有项
        items = os.listdir(directory_path)

        # 遍历这些项，找到第一个文件夹
        for item in items:
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                return item

        # 如果没有找到文件夹，返回None
        return None
    except Exception as e:
        # 处理可能出现的异常，例如目录不存在或权限不足
        print(f"An error occurred: {e}")
        return None


#获取文件夹中第一个文件
def get_first_filename(folder_path: str):
    """
    获取指定文件夹中的第一个文件名称

    Args:
        folder_path: 目标文件夹路径

    Returns:
        str: 第一个文件的完整名称（含后缀）
        None: 文件夹不存在或没有文件时返回空
    """
    # 路径有效性校验‌:ml-citation{ref="1" data="citationList"}
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None

    try:
        # 获取目录下所有条目‌:ml-citation{ref="3,7" data="citationList"}
        entries = os.listdir(folder_path)

        # 遍历条目寻找第一个文件‌:ml-citation{ref="3,7" data="citationList"}
        for entry in entries:
            full_path = os.path.join(folder_path, entry)
            if os.path.isfile(full_path):  # 严格判断文件类型‌:ml-citation{ref="7" data="citationList"}
                return entry  # 返回文件名部分‌:ml-citation{ref="4" data="citationList"}

        return None  # 无文件时返回空
    except PermissionError:
        return None


#获取文件夹中第一个文件夹
def get_first_subdirectory(folder_path: str):
    """
    获取指定目录下的第一个子目录名称

    特性：
    - 自动过滤文件和非目录条目‌:ml-citation{ref="2,4" data="citationList"}
    - 条目名称按字母序排列‌:ml-citation{ref="2,8" data="citationList"}
    - 空目录或无效路径返回None‌:ml-citation{ref="1,7" data="citationList"}

    参数：
    folder_path: 目标目录绝对路径

    返回：
    str: 首个子目录名称（不含路径）
    None: 无子目录或路径无效时返回
    """
    # 路径有效性校验‌:ml-citation{ref="1,7" data="citationList"}
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None

    try:
        # 获取排序后的目录条目‌:ml-citation{ref="2,8" data="citationList"}
        entries = sorted(os.listdir(folder_path))

        for entry in entries:
            full_path = os.path.join(folder_path, entry)
            # 严格判断目录类型‌:ml-citation{ref="4,8" data="citationList"}
            if os.path.isdir(full_path):
                return entry
        return None
    except PermissionError:
        return None

#统计文件夹文件数量
def count_files(folder_path):
    """
    统计指定文件夹内所有文件数量（包含子文件夹）

    参数:
        folder_path (str): 目标文件夹路径

    返回:
        int: 文件总数（路径无效时返回0）
    """
    if not os.path.isdir(folder_path):
        return 0

    total = 0
    try:
        # 遍历所有子目录
        for dirpath, _, filenames in os.walk(folder_path):
            total += len(filenames)  # 累加当前目录文件数
    except PermissionError:
        pass  # 忽略无权限访问的目录
    return total


#删除文件夹下的子文件夹 屏蔽指定文件夹
def clean_parent_folder(parent_path, keep_folder):
    """
    保留父目录中的指定文件夹并删除其他子文件夹

    参数:
        parent_path (str): 要清理的父目录路径
        keep_folder (str): 需要保留的文件夹名称
    """

    # 标准化保留名称‌:ml-citation{ref="6" data="citationList"}
    target_name = os.path.normcase(keep_folder)

    for entry in os.scandir(parent_path):
        # 仅处理文件夹‌:ml-citation{ref="7" data="citationList"}
        if not entry.is_dir():
            continue

        entry_name = os.path.normcase(entry.name)
        entry_path = entry.path

        # 判断保留条件‌:ml-citation{ref="2" data="citationList"}
        if entry_name == target_name:
            print(f"保留目录: {entry_path}")
            continue

        try:
            # 递归删除非保留目录‌:ml-citation{ref="7" data="citationList"}
            shutil.rmtree(entry_path)
            print(f"已删除: {entry_path}")
            return True
        except PermissionError as e:
            print(f"权限不足无法删除: {entry_path} ({e})")
            return False
        except Exception as e:
            print(f"删除异常: {entry_path} ({type(e).__name__})")
            return False


#获取文件夹下的一级子文件夹数量
def count_folder(parent_path: str) -> int:
    """
    统计指定目录下的直接子文件夹数量

    Args:
        parent_path: 需要扫描的父目录路径

    Returns:
        直接子文件夹数量（不包含文件/不递归子目录）
    """
    try:
        # 使用scandir提升遍历效率‌:ml-citation{ref="5,7" data="citationList"}
        entries = os.scandir(parent_path)
        return sum(1 for entry in entries if entry.is_dir())
    except FileNotFoundError:
        print(f"错误路径: {parent_path} 不存在")
        return 0
    except PermissionError:
        print(f"权限不足: 无法访问 {parent_path}")
        return 0
    finally:
        entries.close() if 'entries' in locals() else None


#删除文件夹下的所有文件夹和文件
def clear_folder_contents(target_dir: str) -> bool:
    """
    安全删除目标目录下的所有子目录与文件（保留根目录）

    Args:
        target_dir: 需要清空的目录路径

    Returns:
        bool: 是否成功完成所有删除操作
    """
    # 路径存在性校验‌:ml-citation{ref="1,4" data="citationList"}
    if not os.path.exists(target_dir):
        print(f"警告：路径 {target_dir} 不存在")
        return False

    try:
        # 遍历一级目录条目‌:ml-citation{ref="1,4" data="citationList"}
        for entry in os.listdir(target_dir):
            full_path = os.path.join(target_dir, entry)

            try:
                # 处理文件及符号链接‌:ml-citation{ref="1,4" data="citationList"}
                if os.path.isfile(full_path) or os.path.islink(full_path):
                    os.unlink(full_path)  # 删除文件/链接‌:ml-citation{ref="1,6" data="citationList"}
                # 处理子目录‌:ml-citation{ref="4,7" data="citationList"}
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)  # 递归删除目录树‌:ml-citation{ref="4,7" data="citationList"}
            except PermissionError as pe:
                print(f"权限不足无法删除 {full_path}: {pe}")
            except Exception as e:
                print(f"删除 {full_path} 时发生异常: {e}")

        return True
    except NotADirectoryError:
        print(f"错误：{target_dir} 不是有效目录")
        return False
    except Exception as e:
        print(f"清空目录失败: {e}")
        return False


#获取文件夹下的所有文件大小
def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size

    # 转换大小为更易读的格式
    def readable_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"


    return readable_size(total_size)


#删除根文件夹下的所有文件夹和文件
def delete_root_folder(folder_path, safety_check=False):
    """
    递归删除指定根文件夹下的所有文件和文件夹，但保留根目录
    参数：
    folder_path: 要清理的根目录路径
    safety_check: 是否进行基础安全验证（默认开启）

    返回：(success: bool, message: str)
    """
    # 基础路径验证
    if safety_check:
        if not os.path.exists(folder_path):
            return False, f"路径不存在: {folder_path}"
        if not os.path.isdir(folder_path):
            return False, f"目标不是文件夹: {folder_path}"
        if os.path.samefile(os.path.dirname(folder_path), folder_path):
            return False, "禁止删除文件系统根目录"

    # 遍历根目录下的所有文件和文件夹
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # 删除文件或符号链接
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # 递归删除文件夹

        # 二次验证确保删除成功
        if any(os.listdir(folder_path)):
            return False, f"残留文件未完全删除: {folder_path}"
        return True, f"成功清理目录: {folder_path}"
    except PermissionError as e:
        return False, f"权限拒绝: {str(e)}"
    except FileNotFoundError as e:
        return False, f"文件已不存在: {str(e)}"
    except Exception as e:
        return False, f"删除失败: {str(e)}"


#获取文件夹中的所有MP3文件
def find_all_mp3_files(folder_path):
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


#获取文件夹中的所有PNG文件
def find_all_png_files(folder_path):
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


#获取文件夹下的子文件夹
def count_immediate_folder(folder_path):
    """
    统计指定文件夹的直接子文件夹数量（不递归）

    参数：
    folder_path (str): 目标文件夹路径

    返回：
    int: 直接子文件夹数量

    异常：
    ValueError: 当路径不存在或不是文件夹时抛出
    """
    # 验证路径有效性
    if not os.path.exists(folder_path):
        raise ValueError(f"路径不存在: {folder_path}")
    if not os.path.isdir(folder_path):
        raise ValueError(f"不是文件夹: {folder_path}")

    # 使用scandir高效遍历
    with os.scandir(folder_path) as entries:
        return sum(1 for entry in entries if entry.is_dir())


#获取文件夹下的mp3文件
def get_all_files(path):

    """
    接收一个文件夹路径，返回该文件夹中所有MP3文件的名称列表（不包括路径）。

    :param path: 文件夹路径
    :return: MP3文件名称列表
    """
    mp3_files = []

    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(path):
        # 遍历文件列表
        for file in files:
            # 检查文件扩展名是否为.mp3（不区分大小写）
            if file.lower().endswith('.mp3'):
                # 将文件名（不包括路径）添加到列表中
                mp3_files.append(file)

    return mp3_files

def create_directory2(base_path, folder_name):
    """
    在指定路径创建文件夹

    参数:
        base_path (str): 基础路径
        folder_name (str): 要创建的文件夹名称

    返回:
        str: 创建成功的完整路径
    """
    full_path = os.path.join(base_path, folder_name)

    try:
        os.makedirs(full_path, exist_ok=True)
        print(f"文件夹创建成功: {full_path}")
        return full_path
    except Exception as e:
        print(f"创建文件夹失败: {e}")
        return None

def create_directory(dir_path):
    try:
        # 尝试创建目录
        os.makedirs(dir_path)
    except FileExistsError:
        # 如果目录已存在，捕获错误并提示
        print(f"目录 '{dir_path}' 已存在，无需创建。")
    except Exception as e:
        # 捕获其他可能的错误
        print(f"创建目录 '{dir_path}' 时发生错误: {e}")

