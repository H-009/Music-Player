from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import os

class FileScannerThread(QThread):
    """
    扫描文件夹下的所有文件数量
    """
    file_found = pyqtSignal(str)
    scan_finished = pyqtSignal(list)
    progress_changed = pyqtSignal(int)
    status_updated = pyqtSignal(str)  # 新增状态信号

    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._mutex.lock()
        self.status_updated.emit("扫描中...")  # 初始状态
        self._mutex.unlock()

        file_list = []
        total_files = 0
        processed_files = 0

        try:
            # 第一次遍历计算总数
            for _, _, files in os.walk(self.root_dir):
                if not self._is_running:
                    return
                total_files += len(files)

            # 第二次实际扫描
            for root, _, files in os.walk(self.root_dir):
                if not self._is_running:
                    return

                for file in files:
                    if not self._is_running:
                        return

                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
                    self.file_found.emit(file_path)

                    processed_files += 1
                    progress = int((processed_files / max(total_files, 1)) * 100)
                    self.progress_changed.emit(progress)

            if self._is_running:
                self.scan_finished.emit(file_list)

        except Exception as e:
            self.status_updated.emit(f"扫描错误: {str(e)}")

    def stop(self):
        self._mutex.lock()
        self._is_running = False
        self.status_updated.emit("扫描已停止")  # 停止状态
        self._mutex.unlock()

class FolderScannerThread(QThread):
    """
    扫描文件夹下的所有文件夹数量
    """
    folder_found = pyqtSignal(str)          # 发现文件夹时发射
    scan_finished = pyqtSignal(list)        # 扫描完成时发射所有文件夹列表
    progress_changed = pyqtSignal(int)      # 进度变化信号
    status_updated = pyqtSignal(str)        # 状态更新信号

    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = os.path.normpath(root_dir)  # 规范化路径
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._mutex.lock()
        self.status_updated.emit("扫描中...")
        self._mutex.unlock()

        folder_list = []
        total_folders = 0
        processed_folders = 0

        try:
            # 第一次遍历计算总文件夹数
            for root, dirs, _ in os.walk(self.root_dir):
                if not self._is_running:
                    return
                total_folders += len(dirs)

            # 第二次实际扫描文件夹
            for root, dirs, _ in os.walk(self.root_dir):
                if not self._is_running:
                    return

                for dir_name in dirs:
                    if not self._is_running:
                        return

                    folder_path = os.path.join(root, dir_name)
                    folder_list.append(folder_path)
                    self.folder_found.emit(folder_path)

                    processed_folders += 1
                    progress = int((processed_folders / max(total_folders, 1)) * 100)
                    self.progress_changed.emit(progress)

            if self._is_running:
                self.scan_finished.emit(folder_list)

        except Exception as e:
            self.status_updated.emit(f"扫描错误: {str(e)}")

    def stop(self):
        self._mutex.lock()
        self._is_running = False
        self.status_updated.emit("扫描已停止")
        self._mutex.unlock()

class FileScannerThreadRealTime(QThread):
    """
    扫描文件夹下的所有文件数量
    """
    file_found = pyqtSignal(str)
    scan_finished = pyqtSignal(list)
    progress_changed = pyqtSignal(int)
    status_updated = pyqtSignal(str)  # 新增状态信号

    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._mutex.lock()
        self._mutex.unlock()

        file_list = []
        total_files = 0
        processed_files = 0

        try:
            # 第一次遍历计算总数
            for _, _, files in os.walk(self.root_dir):
                if not self._is_running:
                    return
                total_files += len(files)

            # 第二次实际扫描
            for root, _, files in os.walk(self.root_dir):
                if not self._is_running:
                    return

                for file in files:
                    if not self._is_running:
                        return

                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
                    self.file_found.emit(file_path)

                    processed_files += 1
                    progress = int((processed_files / max(total_files, 1)) * 100)
                    self.progress_changed.emit(progress)

            if self._is_running:
                self.scan_finished.emit(file_list)

        except Exception as e:
            self.status_updated.emit(f"扫描错误: {str(e)}")

    def stop(self):
        self._mutex.lock()
        self._is_running = False
        self.status_updated.emit("扫描已停止")  # 停止状态
        self._mutex.unlock()

class FolderScannerThreadRealTime(QThread):
    """
    扫描文件夹下的所有文件夹数量
    """
    folder_found = pyqtSignal(str)          # 发现文件夹时发射
    scan_finished = pyqtSignal(list)        # 扫描完成时发射所有文件夹列表
    progress_changed = pyqtSignal(int)      # 进度变化信号
    status_updated = pyqtSignal(str)        # 状态更新信号

    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = os.path.normpath(root_dir)  # 规范化路径
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        self._mutex.lock()
        self._mutex.unlock()

        folder_list = []
        total_folders = 0
        processed_folders = 0

        try:
            # 第一次遍历计算总文件夹数
            for root, dirs, _ in os.walk(self.root_dir):
                if not self._is_running:
                    return
                total_folders += len(dirs)

            # 第二次实际扫描文件夹
            for root, dirs, _ in os.walk(self.root_dir):
                if not self._is_running:
                    return

                for dir_name in dirs:
                    if not self._is_running:
                        return

                    folder_path = os.path.join(root, dir_name)
                    folder_list.append(folder_path)
                    self.folder_found.emit(folder_path)

                    processed_folders += 1
                    progress = int((processed_folders / max(total_folders, 1)) * 100)
                    self.progress_changed.emit(progress)

            if self._is_running:
                self.scan_finished.emit(folder_list)

        except Exception as e:
            self.status_updated.emit(f"扫描错误: {str(e)}")

    def stop(self):
        self._mutex.lock()
        self._is_running = False
        self.status_updated.emit("扫描已停止")
        self._mutex.unlock()
