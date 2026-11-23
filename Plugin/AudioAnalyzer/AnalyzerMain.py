import random
import colorsys
import ctypes
import math
import sys
import signal
import pygame
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QProgressDialog

def bin_search(arr, target):
    index = int(len(arr) / 2)
    min_index = 0
    max_index = len(arr) - 1
    found = False

    if target < arr[0]:
        return 0
    if target > arr[len(arr) - 1]:
        return len(arr) - 1

    while not found:
        if min_index == len(arr) - 2:
            return len(arr) - 1
        if arr[index] < target < arr[index + 1] or arr[index] == target:
            return index
        if arr[index] > target:
            max_index = index
        else:
            min_index = index
        index = int((min_index + max_index) / 2)

def rotate(xy, theta):
    cos_theta, sin_theta = math.cos(theta), math.sin(theta)
    return (
        xy[0] * cos_theta - xy[1] * sin_theta,
        xy[0] * sin_theta + xy[1] * cos_theta
    )

def translate(xy, offset):
    return xy[0] + offset[0], xy[1] + offset[1]

def clamp(min_value, max_value, value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value

class AudioAnalyzer:
    def __init__(self):
        self.frequencies_index_ratio = 0
        self.time_index_ratio = 0
        self.spectrogram = None

    def load(self, filename, ico):
        pygame.display.set_caption("音频分析仪")
        icon = pygame.image.load(ico)
        icon = pygame.transform.smoothscale(icon, (64, 64))
        pygame.display.set_icon(icon)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("音频分析仪")

        time_series, sample_rate = librosa.load(filename)
        stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048 * 4))
        self.spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
        frequencies = librosa.core.fft_frequencies(n_fft=2048 * 4)
        times = librosa.core.frames_to_time(np.arange(self.spectrogram.shape[1]),
                                          sr=sample_rate, hop_length=512, n_fft=2048 * 4)
        self.time_index_ratio = len(times) / times[len(times) - 1]
        self.frequencies_index_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

    def show(self):
        librosa.display.specshow(self.spectrogram, y_axis='log', x_axis='time')
        plt.title('spectrogram')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()
        plt.show()

    def get_decibel(self, target_time, freq):
        return self.spectrogram[int(freq * self.frequencies_index_ratio)][int(target_time * self.time_index_ratio)]

    def get_decibel_array(self, target_time, freq_arr):
        return [self.get_decibel(target_time, f) for f in freq_arr]

class AudioBar:
    def __init__(self, x, y, freq, color, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        self.x, self.y, self.freq = x, y, freq
        self.color = color
        self.width, self.min_height, self.max_height = width, min_height, max_height
        self.height = min_height
        self.min_decibel, self.max_decibel = min_decibel, max_decibel
        self.__decibel_height_ratio = (self.max_height - self.min_height) / (self.max_decibel - self.min_decibel)

    def update(self, dt, decibel):
        desired_height = decibel * self.__decibel_height_ratio + self.max_height
        speed = (desired_height - self.height) / 0.1
        self.height += speed * dt
        self.height = clamp(self.min_height, self.max_height, self.height)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y + self.max_height - self.height, self.width, self.height))

class AverageAudioBar(AudioBar):
    def __init__(self, x, y, rng, color, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        super().__init__(x, y, 0, color, width, min_height, max_height, min_decibel, max_decibel)
        self.rng = rng
        self.avg = 0

    def update_all(self, dt, time, analyzer):
        self.avg = 0
        for i in self.rng:
            self.avg += analyzer.get_decibel(time, i)
        self.avg /= len(self.rng)
        self.update(dt, self.avg)

class RotatedAverageAudioBar(AverageAudioBar):
    def __init__(self, x, y, rng, color, angle=0, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        super().__init__(x, y, rng, color, width, min_height, max_height, min_decibel, max_decibel)
        self.angle = angle
        self.rect = None

    def render(self, screen):
        pygame.draw.polygon(screen, self.color, self.rect.points)

    def render_c(self, screen, color):
        pygame.draw.polygon(screen, color, self.rect.points)

    def update_rect(self):
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.rect.rotate(self.angle)

class Rect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.points = []
        self.origin = [self.w / 2, 0]
        self.offset = [self.origin[0] + x, self.origin[1] + y]
        self.rotate(0)

    def rotate(self, angle):
        template = [
            (-self.origin[0], self.origin[1]),
            (-self.origin[0] + self.w, self.origin[1]),
            (-self.origin[0] + self.w, self.origin[1] - self.h),
            (-self.origin[0], self.origin[1] - self.h)
        ]
        self.points = [translate(rotate(xy, math.radians(angle)), self.offset) for xy in template]

    def draw(self, screen):
        pygame.draw.polygon(screen, (255, 255, 0), self.points)

class Audio(QThread):
    def __init__(self):
        super().__init__()
        self.app = None
        self._is_running = True

    def run(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon("AnalyzerIco.ico"))

        progress = QProgressDialog("正在后台加载中，请稍候...", None, 0, 0)
        progress.setWindowTitle("音频分析服务")
        progress.setCancelButton(None)
        progress.setMinimumSize(QSize(300, 100))
        progress.setMaximumSize(QSize(300, 100))
        progress.show()

        timer = QTimer()
        timer.timeout.connect(self.check_running)
        timer.start(100)

        self.app.exec()

    def check_running(self):
        if not self._is_running:
            self.app.quit()

    def stop(self):
        self._is_running = False
        if self.app:
            self.app.quit()

    def __del__(self):
        self.stop()

def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]

def main(file, ico):
    try:
        proc = Audio()
        proc.start()

        analyzer = AudioAnalyzer()
        filename = file
        analyzer.load(filename, ico)

        pygame.init()
        pygame.mixer.init()
        infoObject = pygame.display.Info()
        screen_w = int(infoObject.current_w / 2)
        screen_h = int(infoObject.current_w / 2)
        proc.stop()

        screen = pygame.display.set_mode([screen_w, screen_h])
        pygame.mixer.music.set_volume(1)

        t = pygame.time.get_ticks()
        getTicksLastFrame = t
        timeCount = 0
        avg_bass = 0
        bass_trigger = -30
        bass_trigger_started = 0
        min_decibel = -80
        max_decibel = 80
        circle_color = (40, 40, 40)
        polygon_default_color = [250, 250, 250]
        polygon_bass_color = polygon_default_color.copy()
        polygon_color_vel = [0, 0, 0]
        poly = []
        poly_color = polygon_default_color.copy()
        circleX = int(screen_w / 2)
        circleY = int(screen_h / 2)
        min_radius = 100
        max_radius = 150
        radius = min_radius

        bass = {"start": 50, "stop": 100, "count": 12}
        heavy_area = {"start": 120, "stop": 250, "count": 40}
        low_mids = {"start": 251, "stop": 2000, "count": 50}
        high_mids = {"start": 2001, "stop": 4000, "count": 20}

        freq_groups = [bass, heavy_area, low_mids, high_mids]
        bars = []
        tmp_bars = []
        length = 0

        for group in freq_groups:
            g = []
            s = group["stop"] - group["start"]
            count = group["count"]
            reminder = s % count
            step = int(s / count)
            rng = group["start"]

            for i in range(count):
                if reminder > 0:
                    reminder -= 1
                    arr = np.arange(start=rng, stop=rng + step + 2)
                    rng += step + 3
                else:
                    arr = np.arange(start=rng, stop=rng + step + 1)
                    rng += step + 2
                g.append(arr)
                length += 1
            tmp_bars.append(g)

        angle_dt = 360 / length
        ang = 0

        for g in tmp_bars:
            gr = []
            for c in g:
                gr.append(RotatedAverageAudioBar(
                    circleX + radius * math.cos(math.radians(ang - 90)),
                    circleY + radius * math.sin(math.radians(ang - 90)),
                    c, (255, 0, 255), angle=ang, width=8, max_height=370))
                ang += angle_dt
            bars.append(gr)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(0)

        running = True
        while running:
            avg_bass = 0
            t = pygame.time.get_ticks()
            deltaTime = (t - getTicksLastFrame) / 1000.0
            getTicksLastFrame = t
            timeCount += deltaTime
            screen.fill(circle_color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return

            for b1 in bars:
                for b in b1:
                    b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)
            for b in bars[0]:
                avg_bass += b.avg

            avg_bass /= len(bars[0])

            if avg_bass > bass_trigger:
                if bass_trigger_started == 0:
                    bass_trigger_started = pygame.time.get_ticks()
                if (pygame.time.get_ticks() - bass_trigger_started) / 1000.0 > 2:
                    polygon_bass_color = rnd_color()
                    bass_trigger_started = 0
                if polygon_bass_color is None:
                    polygon_bass_color = rnd_color()
                newr = min_radius + int(avg_bass * ((max_radius - min_radius) / (max_decibel - min_decibel)) + (max_radius - min_radius))
                radius_vel = (newr - radius) / 0.15
                polygon_color_vel = [(polygon_bass_color[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]
            elif radius > min_radius:
                bass_trigger_started = 0
                polygon_bass_color = None
                radius_vel = (min_radius - radius) / 0.15
                polygon_color_vel = [(polygon_default_color[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]
            else:
                bass_trigger_started = 0
                poly_color = polygon_default_color.copy()
                polygon_bass_color = None
                polygon_color_vel = [0, 0, 0]
                radius_vel = 0
                radius = min_radius

            radius += radius_vel * deltaTime

            for i in range(3):
                poly_color[i] = max(0, min(255, poly_color[i] + polygon_color_vel[i] * deltaTime))

            poly = []
            for bar_group in bars:
                for bar in bar_group:
                    rad_angle = math.radians(bar.angle - 90)
                    bar.x = circleX + radius * math.cos(rad_angle)
                    bar.y = circleY + radius * math.sin(rad_angle)
                    bar.update_rect()
                    if hasattr(bar.rect, 'points'):
                        poly.extend([
                            (int(bar.rect.points[3][0]), int(bar.rect.points[3][1])),
                            (int(bar.rect.points[2][0]), int(bar.rect.points[2][1]))
                        ])

            if len(poly) >= 3:
                pygame.draw.polygon(screen, poly_color, poly)
            pygame.draw.circle(screen, circle_color, (circleX, circleY), int(radius))
            pygame.display.flip()
    except Exception as a:
        print(a)
    finally:
        if 'pygame' in locals():
            pygame.quit()
        if 'proc' in locals():
            proc.stop()

class ProgressThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

    def run(self):
        try:
            with open("../../Config/Local/select music.amc", "r", encoding="UTF-8") as f:
                data = f.read()
            with open("../../Config/Local/select playlist.amc", "r", encoding="UTF-8") as f:
                data2 = f.read()

            music = f"../../Play List/{data2}/{data}.mp3"
            main(music, "AnalyzerIco.ico")
        except Exception as e:
            print(f"Error in ProgressThread: {e}")
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait()

    def __del__(self):
        self.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("AnalyzerIco.ico"))

    progress = ProgressThread()
    progress.start()

    def signal_handler(sig, frame):
        progress.stop()
        app.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    timer = QTimer()
    timer.timeout.connect(lambda: None if progress.isRunning() else app.quit())
    timer.start(100)

    sys.exit(app.exec())