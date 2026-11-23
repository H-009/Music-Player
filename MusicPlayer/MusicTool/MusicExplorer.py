import os
import subprocess


def open_in_explorer(path):
    """
    用系统资源管理器打开指定路径
    :param path: 要打开的目录/文件路径（需确保路径存在）
    :return: bool 是否成功打开
    """
    try:
        if os.path.isfile(path):
            # 使用popen完全修正转义
            cmd = f'explorer /select, "{path}"'
            subprocess.Popen(cmd, shell=True)
        else:
            os.startfile(os.path.abspath(path))
    except Exception as e:
        print(f"打开失败: {e}")
        return False