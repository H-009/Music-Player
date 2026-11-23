import re
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QThread


# ======================
# TimeMonitorThread：负责解析实时传入的时间字符串，如 "0:00.000"
# ======================
class TimeMonitorThread(QThread):
    # 信号：发射解析后的时间（单位：秒，类型 float）
    time_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._current_time_str = "0:00.000"  # 默认初始值，稍后会被外部更新
        self._running = True  # 控制线程是否继续运行

    def run(self):
        try:
            while self._running:
                # 解析当前的时间字符串
                current_time_sec = self.parse_time()
                if current_time_sec is not None:
                    self.time_updated.emit(current_time_sec)  # 发射 float 秒数
                self.msleep(1)  # 每1毫秒检查一次（可根据需求调整，比如 10ms）
        except Exception as e:
            print(f"[TimeMonitorThread] 运行异常: {e}")

    def parse_time(self):
        """
        解析格式为 "分:秒.毫秒" 的时间字符串，例如 "0:01.500"
        返回对应的秒数（float），例如 "0:01.500" -> 1.5
        """
        try:
            match = re.match(r'^(\d+):(\d{2})\.(\d{3})$', self._current_time_str.strip())
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3))
                total_seconds = minutes * 60 + seconds + milliseconds / 1000.0
                return total_seconds
            else:
                print(f"[TimeMonitorThread] 时间格式不匹配，当前值: '{self._current_time_str}'")
        except Exception as e:
            print(f"[TimeMonitorThread] 解析时间出错: {e}")
        return None  # 解析失败时返回 None

    def update_time_string(self, time_str):
        """
        外部调用此方法，传入最新的时间字符串，例如 "0:01.500"
        """
        self._current_time_str = time_str

    def stop(self):
        """
        停止线程运行，并等待其退出
        """
        self._running = False
        self.wait()


# ======================
# LyricWidget：歌词控件，根据时间显示对应歌词
# ======================
class LyricWidget(QWidget):
    # 信号：发射当前应该显示的歌词文本
    text_pyqtSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lyrics = []  # 歌词数据，格式建议为：List[Tuple[float, str]]，如 [(0.0, "第一句"), (5.0, "第二句")]
        self.current_line = 0  # 当前显示的歌词行索引
        self.monitor_thread = None  # 时间监控线程
        self.last_lyric_text = ""  # 上一次显示的歌词内容，用于避免重复刷新
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def update_lyric_position(self, current_sec):
        try:
            if not self.lyrics:
                return

            # 新增：当时间小于0.01秒时强制高亮第一行
            if current_sec < 0.01:
                new_line = 0
            else:
                new_line = 0
                for i, (time_sec, text) in enumerate(self.lyrics):
                    if time_sec <= current_sec:
                        new_line = i
                    else:
                        break

            current_text = self.lyrics[new_line][1]
            if new_line != self.current_line or current_text != self.last_lyric_text:
                self.current_line = new_line
                self.last_lyric_text = current_text
                self.text_pyqtSignal.emit(self.last_lyric_text)
        except Exception as e:
            print("LyricWidget::update_lyric_position 异常:", e)

    def bind_time_monitor(self):
        """
        初始化并启动时间监控线程（不传入任何初始时间字符串）
        之后需要通过 update_current_time_str(...) 方法实时推送时间
        """
        try:
            if self.monitor_thread and self.monitor_thread.isRunning():
                self.monitor_thread.stop()

            self.monitor_thread = TimeMonitorThread()  # 不再传入 time_str
            self.monitor_thread.time_updated.connect(
                self.update_lyric_position,
                Qt.QueuedConnection  # 确保线程安全
            )
            self.monitor_thread.start()
        except Exception as e:
            print(f"LyricWidget::bind_time_monitor 错误: {e}")

    def update_current_time_str(self, time_str):
        """
        外部调用此方法，传入当前播放时间字符串，例如 "0:01.500"
        该方法将时间字符串传递给 TimeMonitorThread，由其解析并驱动歌词同步
        """
        if self.monitor_thread:
            self.monitor_thread.update_time_string(time_str)
        else:
            print("[LyricWidget] 警告：时间监控线程未启动，请先调用 bind_time_monitor()")

    def set_lyrics(self, lyrics):
        """
        设置歌词数据，格式建议为：List[Tuple[float, str]]
        例如：[(0.0, "第一句"), (5.0, "第二句"), (10.0, "第三句")]
        """
        try:
            self.lyrics = lyrics  # 假定传入的是 [(秒数, 歌词), ...]
            self.current_line = 0
            if self.lyrics:
                # 可选：返回第一句歌词，或者直接显示
                return self.lyrics[0][1]
        except Exception as a:
            print("[LyricWidget] 设置歌词发生错误:", a)

    def closeEvent(self, event):
        """
        窗口关闭时，确保线程安全退出
        """
        if hasattr(self, 'monitor_thread') and self.monitor_thread:
            self.monitor_thread.stop()
        super().closeEvent(event)

    def stop(self):
        """
        停止时间监控线程
        """
        if self.monitor_thread:
            self.monitor_thread.stop()