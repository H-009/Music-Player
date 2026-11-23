import math
import os
import time
from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker, QElapsedTimer, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel

from .MusicService import MusicService
from .MusicService import MusicFileService


#更新进度条 毫秒级高精度计时器
class SliderUpdater(QThread):
    update_slider = pyqtSignal(int)  # 更新滑动条信号
    update_label = pyqtSignal(str)  # 新增：更新标签信号
    update_label2 = pyqtSignal(str)  # 新增：更新标签信号
    next = pyqtSignal()
    update = pyqtSignal(str)

    def __init__(self, slider, max_value, min_v,max_s):
        super().__init__()
        self.music_service = MusicService

        self.current_value = self.music_service.format_minutes(min_v)
        self.slider = slider
        self.max_value = max_value
        self.min = min_v
        self.max_s = max_s


        # 初始化滑动条范围
        self.slider.setMinimum(0)
        self.slider.setMaximum(max_value)

        self.timer = QElapsedTimer() #高精度计时器

        # 线程安全控制
        self.mutex = QMutex()
        self._is_paused = False  # 私有变量 + 线程锁保护

    def stop(self):
        """暂停线程（线程安全）"""
        self.slider.setValue(0)
        with QMutexLocker(self.mutex):
            self._is_paused = True

    def pause(self):
        """暂停线程（线程安全）"""
        with QMutexLocker(self.mutex):
            self._is_paused = True

    def resume(self):
        """恢复线程（线程安全）"""
        with QMutexLocker(self.mutex):
            self._is_paused = False

    def run(self):
        try:
            current_value = self.min  # 假设是秒，从 min 开始
            if current_value == 0:
                current_value = 1

            max_value = self.max_value
            max_s = self.max_s

            last_update_time = 0  # 上一次触发更新的时间点
            update_interval_ms = 1000  # 每 1000ms（1秒）更新一次

            # 计时器先不启动，等到第一次非暂停时再启动
            timer_started = False

            while current_value <= max_value:
                with QMutexLocker(self.mutex):
                    is_paused = self._is_paused

                if not is_paused:
                    if not timer_started:
                        self.timer.start()  # ✅ 第一次进入运行状态时，启动计时器
                        timer_started = True
                        last_update_time = self.timer.elapsed()  # 初始化为当前时间

                    current_time_ms = self.timer.elapsed()

                    if current_time_ms - last_update_time >= update_interval_ms:
                        self.update_slider.emit(current_value)
                        self.current_value = self.music_service.format_minutes(current_value)
                        self.update_label.emit(self.current_value)
                        self.update_label2.emit(max_s)

                        MusicFileService.process_ams_file("Config/Statistics/song time.ams", 1)

                        if self.current_value == max_s:
                            self.next.emit()
                            self.update_label.emit("0:00")
                            self.update_label.emit("0:00")
                            print("匹配成功")

                        current_value += 1
                        last_update_time = current_time_ms

                    elapsed_since_last_update = current_time_ms - last_update_time
                    self.update.emit(f"{self.current_value}.{elapsed_since_last_update:03d}")

                    QThread.msleep(1)

                else:
                    # 暂停时，确保计时器不要误导，可以重置标志位或直接不操作计时器
                    if timer_started:
                        # 可选：暂停时可以选择不修改任何计时逻辑
                        pass
                    QThread.msleep(10)

        except Exception as a:
            print(f"run() 异常: {a}")

class FolderServicePlus(QObject):
    status_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int)  # 新增进度信号
    _stop_flag = False
    _mutex = QMutex()

    def __init__(self, folder_path, c, parent=None):
        super().__init__(parent)
        self.folder_path = os.path.normpath(folder_path)
        self.c = c
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)  # 动态线程数

    def stop(self):
        """安全停止扫描"""
        self._mutex.lock()
        self._stop_flag = True
        self._mutex.unlock()

    def _should_stop(self):
        """检查停止标志"""
        self._mutex.lock()
        flag = self._stop_flag
        self._mutex.unlock()
        return flag

    def run(self):
        """优化的扫描执行函数"""
        self.status_updated.emit(f"{self.c}计算中...")
        start_time = time.time()

        try:
            # 1. 预扫描获取文件总数（用于进度计算）
            total_files = 0
            for _, _, files in os.walk(self.folder_path):
                if self._should_stop():
                    self.status_updated.emit(f"{self.c}已取消")
                    return
                total_files += len(files)

            # 2. 多线程并行扫描
            total_size = 0
            processed_files = 0
            progress_interval = max(1, total_files // 100)  # 进度更新间隔

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for root, _, files in os.walk(self.folder_path):
                    if self._should_stop():
                        break

                    for filename in files:
                        file_path = os.path.join(root, filename)
                        futures.append(executor.submit(self._get_file_size, file_path))

                for future in futures:
                    if self._should_stop():
                        break

                    total_size += future.result()
                    processed_files += 1

                    # 按间隔更新进度（避免频繁信号发射）
                    if processed_files % progress_interval == 0:
                        progress = int((processed_files / total_files) * 100)
                        self.progress_updated.emit(progress)

            if not self._should_stop():
                elapsed = time.time() - start_time
                size_str = self._format_size(total_size)
                self.status_updated.emit(f"{self.c}{size_str}")

        except Exception as e:
            self.status_updated.emit(f"{self.c}错误: {str(e)}")

    def _get_file_size(self, file_path):
        """线程安全获取文件大小"""
        try:
            return os.path.getsize(file_path) if os.path.isfile(file_path) else 0
        except:
            return 0  # 忽略权限错误等问题

    def _format_size(self, size_bytes):
        """优化的大小格式化"""
        if size_bytes == 0:
            return "0B"
        units = ("B", "KB", "MB", "GB", "TB")
        i = min(4, int(math.log(max(1, size_bytes), 1024)))
        return f"{size_bytes / 1024 ** i:.2f} {units[i]}"

class FolderServicePlusRealTime(QObject):
    status_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int)  # 新增进度信号
    _stop_flag = False
    _mutex = QMutex()

    def __init__(self, folder_path, c, parent=None):
        super().__init__(parent)
        self.folder_path = os.path.normpath(folder_path)
        self.c = c
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)  # 动态线程数

    def stop(self):
        """安全停止扫描"""
        self._mutex.lock()
        self._stop_flag = True
        self._mutex.unlock()

    def _should_stop(self):
        """检查停止标志"""
        self._mutex.lock()
        flag = self._stop_flag
        self._mutex.unlock()
        return flag

    def run(self):
        """优化的扫描执行函数"""
        start_time = time.time()

        try:
            # 1. 预扫描获取文件总数（用于进度计算）
            total_files = 0
            for _, _, files in os.walk(self.folder_path):
                if self._should_stop():
                    self.status_updated.emit(f"{self.c}已取消")
                    return
                total_files += len(files)

            # 2. 多线程并行扫描
            total_size = 0
            processed_files = 0
            progress_interval = max(1, total_files // 100)  # 进度更新间隔

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for root, _, files in os.walk(self.folder_path):
                    if self._should_stop():
                        break

                    for filename in files:
                        file_path = os.path.join(root, filename)
                        futures.append(executor.submit(self._get_file_size, file_path))

                for future in futures:
                    if self._should_stop():
                        break

                    total_size += future.result()
                    processed_files += 1

                    # 按间隔更新进度（避免频繁信号发射）
                    if processed_files % progress_interval == 0:
                        progress = int((processed_files / total_files) * 100)
                        self.progress_updated.emit(progress)

            if not self._should_stop():
                elapsed = time.time() - start_time
                size_str = self._format_size(total_size)
                self.status_updated.emit(f"{self.c}{size_str}")

        except Exception as e:
            self.status_updated.emit(f"{self.c}错误: {str(e)}")

    def _get_file_size(self, file_path):
        """线程安全获取文件大小"""
        try:
            return os.path.getsize(file_path) if os.path.isfile(file_path) else 0
        except:
            return 0  # 忽略权限错误等问题

    def _format_size(self, size_bytes):
        """优化的大小格式化"""
        if size_bytes == 0:
            return "0B"
        units = ("B", "KB", "MB", "GB", "TB")
        i = min(4, int(math.log(max(1, size_bytes), 1024)))
        return f"{size_bytes / 1024 ** i:.2f} {units[i]}"


# 图标缓存区
class IconCache:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def get_icon(self, path, size=256):
        """获取缓存中的图标，如果路径不存在则不创建缓存"""
        cache_key = f"{hash(path)}_{size}"

        # 如果路径不存在，直接返回空QIcon 防止假缓存无法替换
        if not os.path.exists(path):
            return QIcon()  # 返回空图标

        # 正常缓存处理
        if cache_key not in self._cache:
            self._cache[cache_key] = QIcon(path)

        return self._cache[cache_key]

    def replace_icon(self, path, size=256, new_icon=None):
        """
        替换缓存中的图标

        参数:
            path: 图标路径
            size: 图标尺寸(用于区分不同尺寸的相同路径图标)
            new_icon: 新的QIcon对象，如果为None则重新加载路径图标

        返回:
            替换后的图标
        """
        cache_key = f"{hash(path)}_{size}"

        if new_icon is None:
            # 如果未提供新图标，则重新加载路径图标
            self._cache[cache_key] = QIcon(path)
        else:
            # 使用提供的新图标替换
            self._cache[cache_key] = new_icon

        return self._cache[cache_key]

    def clear_cache(self):
        """清空图标缓存"""
        self._cache.clear()

    def remove_icon(self, path, size=256):
        """
        从缓存中移除指定图标

        参数:
            path: 图标路径
            size: 图标尺寸

        返回:
            如果图标存在并被移除返回True，否则返回False
        """
        cache_key = f"{hash(path)}_{size}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False

    def get_cache_info(self):
        """打印当前缓存内容"""
        print("\n当前图标缓存内容:")
        print(f"缓存条目总数: {len(self._cache)}")

        for key, icon in self._cache.items():
            path_hash, size = key.split('_')
            print(f"\n缓存键: {key}")
            print(f"路径哈希: {path_hash}")
            print(f"图标尺寸: {size}px")
            print(f"图标是否有效: {'否' if icon.isNull() else '是'}")

