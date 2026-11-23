import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QTimer, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath, QPen, QFontMetrics


class LyricLine:
    def __init__(self, time_ms, text):
        self.time_ms = time_ms
        self.text = text
        self.end_time_ms = 0  # 将在解析后计算


class LyricWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lyrics = []  # List[LyricLine]
        self.current_line_index = -1
        self.progress_in_line = 0.0  # 0.0 to 1.0, 当前行内的播放进度

        # 样式配置
        self.font = QFont("Microsoft YaHei", 14)
        self.normal_color = QColor(100, 100, 100)
        self.highlight_color = QColor(0, 153, 255)
        self.bg_color = QColor(255, 255, 255)

        self.setMinimumHeight(100)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), self.bg_color)
        self.setPalette(pal)

    def set_lyrics(self, lyrics: list):
        """设置解析后的歌词列表"""
        self.lyrics = lyrics
        # 计算每行的结束时间（即下一行的开始时间）
        for i in range(len(self.lyrics) - 1):
            self.lyrics[i].end_time_ms = self.lyrics[i + 1].time_ms
        if self.lyrics:
            # 最后一行假设持续5秒，或者可以根据音频总长设定
            self.lyrics[-1].end_time_ms = self.lyrics[-1].time_ms + 5000
        self.update()

    def update_progress(self, current_time_ms: int):
        """由外部播放器调用，更新当前时间和进度"""
        if not self.lyrics:
            return

        # 查找当前行
        new_index = -1
        for i, line in enumerate(self.lyrics):
            if current_time_ms >= line.time_ms and current_time_ms < line.end_time_ms:
                new_index = i
                break

        if new_index != self.current_line_index:
            self.current_line_index = new_index
            self.update()

        if self.current_line_index != -1:
            line = self.lyrics[self.current_line_index]
            duration = line.end_time_ms - line.time_ms
            if duration > 0:
                self.progress_in_line = (current_time_ms - line.time_ms) / duration
                self.progress_in_line = max(0.0, min(1.0, self.progress_in_line))
            else:
                self.progress_in_line = 1.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.current_line_index == -1 or not self.lyrics:
            painter.drawText(self.rect(), Qt.AlignCenter, "No Lyrics")
            return

        line = self.lyrics[self.current_line_index]
        text = line.text

        # 计算文本宽度
        fm = QFontMetrics(self.font)
        text_width = fm.width(text)
        text_height = fm.height()

        # 居中位置
        x_start = (self.width() - text_width) // 2
        y_pos = (self.height() + text_height) // 2 - fm.descent()

        # 1. 绘制背景灰色歌词
        painter.setFont(self.font)
        painter.setPen(self.normal_color)
        painter.drawText(x_start, y_pos, text)

        # 2. 计算高亮宽度 (线性插值核心)
        highlight_width = int(text_width * self.progress_in_line)

        # 3. 绘制高亮部分
        # 使用 QPainterPath 进行裁剪，只绘制高亮宽度的部分
        path = QPainterPath()
        path.addText(x_start, y_pos, self.font, text)

        # 创建裁剪区域：从左边开始，宽度为 highlight_width
        clip_rect = painter.clipBoundingRect()  # 获取当前裁剪区，通常是大矩形
        # 我们手动定义一个矩形作为新的裁剪区
        highlight_clip = painter.clipRegion()  # 保存旧裁剪区

        # 设置新的裁剪区：只允许在 highlight_width 范围内绘制
        painter.setClipRect(x_start, 0, highlight_width, self.height(), Qt.IntersectClip)

        painter.setPen(self.highlight_color)
        painter.drawText(x_start, y_pos, text)

        # 恢复裁剪区
        painter.setClipping(False)


class MusicPlayerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 LRC 逐字插值演示")
        self.setGeometry(100, 100, 600, 400)

        # 模拟数据
        self.current_time_ms = 0
        self.is_playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)

        # 界面布局
        layout = QVBoxLayout()

        self.lyric_widget = LyricWidget()
        layout.addWidget(self.lyric_widget)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 10000)  # 模拟10秒歌曲
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)

        btn_layout = QVBoxLayout()
        self.btn_load = QPushButton("加载示例歌词")
        self.btn_load.clicked.connect(self.load_sample_lyrics)
        self.btn_play = QPushButton("播放/暂停")
        self.btn_play.clicked.connect(self.toggle_play)

        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_play)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # 加载示例
        self.load_sample_lyrics()

    def load_sample_lyrics(self):
        # 模拟解析 LRC
        # 格式: [mm:ss.xx] 歌词
        sample_lrc = """
[00:00.00] Hello World
[00:02.00] This is a test
[00:04.00] Linear Interpolation
[00:06.00] For Karaoke Effect
[00:08.00] End of Song
"""
        lyrics = []
        pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
        for line in sample_lrc.strip().split('\n'):
            match = pattern.match(line.strip())
            if match:
                m, s, ms, text = match.groups()
                time_ms = int(m) * 60000 + int(s) * 1000 + int(ms.ljust(3, '0'))
                if text.strip():
                    lyrics.append(LyricLine(time_ms, text.strip()))

        # 按时间排序
        lyrics.sort(key=lambda x: x.time_ms)
        self.lyric_widget.set_lyrics(lyrics)
        self.slider.setMaximum(lyrics[-1].end_time_ms if lyrics else 10000)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(50)  # 50ms 刷新一次
        else:
            self.timer.stop()

    def on_timer_tick(self):
        self.current_time_ms += 50
        if self.current_time_ms > self.slider.maximum():
            self.current_time_ms = 0
            self.is_playing = False
            self.timer.stop()

        self.slider.setValue(self.current_time_ms)
        self.lyric_widget.update_progress(self.current_time_ms)

    def on_slider_changed(self, value):
        self.current_time_ms = value
        self.lyric_widget.update_progress(self.current_time_ms)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MusicPlayerUI()
    window.show()
    sys.exit(app.exec_())
