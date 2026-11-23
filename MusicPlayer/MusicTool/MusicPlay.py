from pygame import mixer
from PyQt5.QtCore import QThread, QMutex, QMutexLocker, QTimer, QElapsedTimer


class MusicMonitor(QThread):
    def __init__(self, fade_in_duration=1.0, fade_out_duration=1.0):
        super().__init__()
        self.volume = 1.0
        self.mutex = QMutex()
        self._is_running = True
        self._is_paused = False
        self.fade_in_duration = max(0.1, fade_in_duration)
        self.fade_out_duration = max(0.1,fade_out_duration)

        # 从配置文件读取上次的音量（假设文件保存的是 0~100 的整数）
        try:
            with open("Config/Local/select volume.amc", 'r', encoding="UTF-8") as file:
                data = int(file.read())
            self._last_volume = data / 100.0  # 转为 0.0 ~ 1.0
        except Exception:
            self._last_volume = 1.0  # 默认音量

        # 初始化 pygame mixer
        mixer.pre_init(buffer=1024)
        mixer.init()

        # 播放起始位置（可选）
        self._play_start_pos = 0

        # ===== QTimer + QElapsedTimer 淡入淡出相关 =====
        self._fade_timer = QTimer()
        self._fade_timer.timeout.connect(self._on_fade_step)
        self._fade_start_vol = 0.0
        self._fade_end_vol = 0.0
        self._fade_duration_ms = 0
        self._is_fading = False

        # ✅ 修复：用 QElapsedTimer 来记录淡入淡出的开始时间
        self._fade_elapsed_timer = QElapsedTimer()

    def set_load(self, file_path):
        """加载音乐文件"""
        with QMutexLocker(self.mutex):
            mixer.music.load(file_path)

    def set_play(self, start_pos=0):
        """开始播放音乐，支持从指定位置开始（如果 pygame 支持）"""
        with QMutexLocker(self.mutex):
            self._play_start_pos = start_pos
            mixer.music.play(start=start_pos)

    def set_volume(self, volume):
        """直接设置音量（非淡入淡出）"""
        with QMutexLocker(self.mutex):
            mixer.music.set_volume(volume)
            self.volume = volume

    def _on_fade_step(self):
        """QTimer 定时触发的槽函数，用于更新音量（非阻塞淡入淡出核心逻辑）"""
        elapsed = self._fade_elapsed_timer.elapsed()  # ✅ 获取从开始淡入淡出到现在经过的毫秒数
        duration = self._fade_duration_ms

        if elapsed >= duration:
            # 淡入淡出完成
            self._is_fading = False
            self._fade_timer.stop()
            final_vol = self._fade_end_vol
            mixer.music.set_volume(final_vol)

            # 淡出到0后自动暂停
            if final_vol == 0.0:
                mixer.music.pause()

            # 淡入到目标音量后，如果之前是暂停状态，自动恢复播放
            elif self._fade_start_vol == 0.0 and final_vol > 0.0:
                if self._is_paused:
                    mixer.music.unpause()
                    self._is_paused = False

        else:
            # 计算当前音量
            progress = elapsed / duration
            current_vol = self._fade_start_vol + (self._fade_end_vol - self._fade_start_vol) * progress
            mixer.music.set_volume(current_vol)
            # 可选：print(f"[Fade] 当前音量: {current_vol:.2f}, 进度: {progress:.2f}")

    def _start_fade_out_to_pause(self, start_vol, duration_sec):
        """启动淡出到0，用于 pause()"""
        self._fade_start_vol = start_vol
        self._fade_end_vol = 0.0
        self._fade_duration_ms = int(duration_sec * 1000)
        self._fade_elapsed_timer.start()  # ✅ 开始计时
        self._is_fading = True
        self._fade_timer.start(50)  # 每 50 毫秒触发一次 _on_fade_step

    def _start_fade_in_from_pause(self, start_vol, target_vol, duration_sec):
        """启动淡入到目标音量，用于 resume()"""
        self._fade_start_vol = start_vol
        self._fade_end_vol = target_vol
        self._fade_duration_ms = int(duration_sec * 1000)
        self._fade_elapsed_timer.start()  # ✅ 开始计时
        self._is_fading = True
        self._fade_timer.start(50)

    def pause(self):
        """暂停音乐，先淡出到0，然后自动暂停"""
        with QMutexLocker(self.mutex):
            if not self._is_running or self._is_paused:
                return

            self._is_paused = True
            current_vol = mixer.music.get_volume()
            self._last_volume = current_vol

            # 启动淡出到0，淡出完成后自动暂停
            self._start_fade_out_to_pause(current_vol, self.fade_out_duration)

    def resume(self):
        """恢复音乐，先淡入到目标音量，然后自动 unpause"""
        with QMutexLocker(self.mutex):
            if not self._is_running or not self._is_paused:
                return

            self._is_paused = False

            current_vol = mixer.music.get_volume()

            # 启动淡入到目标音量
            self._start_fade_in_from_pause(current_vol, self.volume, self.fade_in_duration)

    def quit(self):
        """退出线程，先淡出到0，然后停止音乐，最后退出线程"""
        with QMutexLocker(self.mutex):
            if not self._is_running:
                super().quit()
                return

            self._is_running = False

            if mixer.get_init() and mixer.music.get_busy():
                current_vol = mixer.music.get_volume()
                if current_vol > 0.0:
                    self._start_fade_out_to_stop(current_vol, self.fade_out_duration)

        super().quit()

    def _start_fade_out_to_stop(self, start_vol, duration_sec):
        """淡出到0，然后停止音乐（用于 quit）"""
        self._fade_start_vol = start_vol
        self._fade_end_vol = 0.0
        self._fade_duration_ms = int(duration_sec * 1000)
        self._fade_elapsed_timer.start()  # ✅ 开始计时
        self._is_fading = True
        self._fade_timer.start(50)

    def run(self):
        """线程主循环，用于监控（可扩展）"""
        while self._is_running:
            with QMutexLocker(self.mutex):
                if self._is_paused:
                    self.msleep(100)  # 暂停时降低 CPU
                    continue
            self.msleep(50)  # 降低总体 CPU 占用