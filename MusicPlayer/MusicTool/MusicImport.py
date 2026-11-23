import os
import shutil


class Service(object):

    #复制文件
    @staticmethod
    def copy_file(file_path, target_path):
        """
        将文件从 file_path 复制到 target_path。

        参数:
            file_path (str): 要复制的文件的路径。
            target_path (str): 目标路径，可以是文件夹或文件的完整路径。

        如果 target_path 是文件夹，则文件将被复制到该文件夹内，并保持原名。
        如果 target_path 是文件的完整路径，则文件将被复制并重命名为该路径指定的名称。
        """
        try:
            # 检查源文件是否存在
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"指定的文件不存在: {file_path}")

            # 处理目标路径类型
            if os.path.isdir(target_path):
                # 如果是文件夹，拼接保留原文件名的新路径
                target_file_path = os.path.join(target_path, os.path.basename(file_path))
            else:
                # 如果是文件路径，直接使用目标路径
                target_file_path = target_path

            # 执行文件复制（保留元数据）
            shutil.copy2(file_path, target_file_path)

        except Exception as e:
            print(f"复制文件时发生错误: {e}")

    #复制文件夹
    @staticmethod
    def copy_folder(source_folder, target_dir):
        """
        递归复制所有MP3文件到目标目录（扁平化结构，不保留子文件夹）

        参数:
            source_folder (str): 要扫描的源文件夹路径
            target_dir (str): 目标目录路径（所有MP3文件将直接复制到此）

        特性:
            1. 自动识别.mp3和.MP3文件
            2. 处理文件名冲突（自动添加序号）
            3. 跳过非MP3文件
            4. 不创建任何子文件夹
        """
        try:
            # 验证路径有效性
            if not os.path.isdir(source_folder):
                print(f"[错误] 源文件夹不存在: {source_folder}")
                return False

            # 创建目标目录（如果不存在）
            os.makedirs(target_dir, exist_ok=True)
            print(f"准备复制MP3文件到: {target_dir}")

            # 计数器
            copied_files = 0
            duplicate_count = 0

            # 递归遍历源文件夹
            for root, _, files in os.walk(source_folder):
                for filename in files:
                    # 检查是否为MP3文件（不区分大小写）
                    if filename.lower().endswith('.mp3'):
                        src_path = os.path.join(root, filename)

                        # 处理目标文件名冲突
                        dest_name = filename
                        dest_path = os.path.join(target_dir, dest_name)
                        counter = 1

                        # 如果文件已存在，添加序号
                        while os.path.exists(dest_path):
                            base, ext = os.path.splitext(filename)
                            dest_name = f"{base} ({counter}){ext}"
                            dest_path = os.path.join(target_dir, dest_name)
                            counter += 1
                            duplicate_count += 1

                        # 执行复制
                        shutil.copy2(src_path, dest_path)
                        copied_files += 1
                        print(f"已复制: {filename.ljust(30)} → {dest_name if counter > 1 else ''}")

            # 输出统计信息
            print(f"\n操作完成:")
            print(f"• 共找到 {copied_files} 个MP3文件")
            print(f"• 处理了 {duplicate_count} 个重名文件")
            print(f"• 目标目录: {target_dir}")
            return True

        except Exception as e:
            print(f"\n[错误] 操作失败: {str(e)}")
            return False

    #复制文件夹并新建文件夹
    @staticmethod
    def copy_folder2(source_folder, target_folder):
        """
        递归复制整个文件夹到目标文件夹中（保留原始结构）

        参数:
            source_folder (str): 要复制的源文件夹路径
            target_folder (str): 目标文件夹路径（会在此创建同名文件夹）

        特性:
            1. 完全保留源文件夹结构
            2. 自动处理路径不存在的情况
            3. 显示详细的复制进度
        """
        try:
            # 验证源文件夹
            if not os.path.isdir(source_folder):
                print(f"[错误] 源文件夹不存在: {source_folder}")
                return False

            # 创建目标文件夹路径（保留源文件夹名）
            folder_name = os.path.basename(source_folder)
            dest_path = os.path.join(target_folder, folder_name)

            # 执行复制
            print(f"正在复制: {source_folder} → {dest_path}")
            shutil.copytree(source_folder, dest_path)
            print(f"复制完成: 共复制到 {dest_path}")
            return True

        except shutil.Error as e:
            print(f"[警告] 部分文件复制失败: {str(e)}")
            return True
        except Exception as e:
            print(f"[错误] 复制失败: {str(e)}")
            return False