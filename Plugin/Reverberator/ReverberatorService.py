import os
from pathlib import Path
import librosa
import numpy as np
from pydub import AudioSegment
from scipy import signal
import soundfile as sf
from scipy.signal import lfilter, butter


def ensure_folder_exists(folder_path):
    """确保文件夹存在，不存在则递归创建"""
    try:
        # 使用pathlib处理跨平台路径
        path = Path(folder_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        return False


# 混响v1 重复音
def reverberation_1(input_path, output_path,
                    strength=0.5#强度
                    ):
    def _generate_impulse(sample_rate, delay_ms, decay):
        delay_samples = int(delay_ms * sample_rate / 1000)
        impulse = np.zeros(3 * delay_samples + 1)
        for i in range(3):
            impulse[(i + 1) * delay_samples] = decay ** (i + 1)
        return impulse / np.max(impulse)
    y, sr = librosa.load(input_path, mono=True)
    impulse = _generate_impulse(sr, 100*strength, 0.7*strength)
    wet = signal.fftconvolve(y, impulse, mode='same')
    processed = y*(1-strength) + wet*strength
    sf.write(output_path, processed, sr)  # 关键修改点

# 混响v2 延音
def reverberation_2(input_path, output_path,
               delay=0.3,#初始回声延迟时间
               decay=0.5,#回声衰减系数
               wet_level=0.3,#混响强度
               dry_level=0.7,#原始强度
               reverb_strength=1.0,#全局效果强度
               num_echoes=6#基础回声次数
               ):
    # 读取音频
    y, sr = librosa.load(input_path, sr=None, mono=False)

    # 立体声转单声道
    if len(y.shape) > 1:
        y = librosa.to_mono(y)

    # 动态调整参数（根据强度系数）
    adjusted_delay = delay * (1 + 0.2 * (reverb_strength - 1))
    adjusted_decay = decay * (1 - 0.3 * (reverb_strength - 1))
    adjusted_wet = wet_level * reverb_strength
    adjusted_echoes = num_echoes + int((reverb_strength - 1) * 2)

    # 参数安全限制
    adjusted_delay = max(0.1, min(adjusted_delay, 1.0))
    adjusted_decay = max(0.2, min(adjusted_decay, 0.8))
    adjusted_wet = max(0.0, min(adjusted_wet, 2.0))
    adjusted_echoes = max(4, min(adjusted_echoes, 12))

    # 混响生成流程
    y = y / np.max(np.abs(y))  # 归一化

    delay_samples = int(adjusted_delay * sr)
    reverb_signal = np.zeros_like(y)

    # 生成回声
    for i in range(1, adjusted_echoes + 1):
        current_decay = adjusted_decay ** i
        current_delay = delay_samples * i

        echo = np.roll(y, current_delay) * current_decay
        if current_delay > 0:
            echo[:current_delay] = 0

        reverb_signal += echo

    # 信号混合（带强度控制）
    wet = reverb_signal / (np.max(np.abs(reverb_signal)) + 1e-6)  # 安全归一化
    processed = (dry_level * y) + (adjusted_wet * wet)

    # 限幅保护
    processed = np.clip(processed, -1.0, 1.0)

    sf.write(output_path, processed, sr)

# 混响v3 室内音
def reverberation_3(audio_path, output_path,
                 m=0.4#干湿比
                 ):
    def butter_lowpass(cutoff, sr, order=5):
        """低通滤波器设计"""
        nyq = 0.5 * sr
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low')
        return b, a

    def schroeder_reverb(y, sr, mix=0.4):
        """四通道梳状滤波器+全通滤波器"""
        out = np.zeros_like(y)
        # 梳状滤波器组（不同延迟时间）
        for delay in [0.0297, 0.0371, 0.0411, 0.0437]:
            delayed = np.roll(y, int(sr * delay)) * 0.7
            out += delayed
        # 全通滤波器增强扩散
        allpass_delay = int(sr * 0.005)
        allpass_out = np.zeros_like(out)
        for i in range(allpass_delay, len(out)):
            allpass_out[i] = out[i] + 0.5 * allpass_out[i - allpass_delay]
        return y * (1 - mix) + allpass_out * mix

    """主处理函数"""
    y, sr = librosa.load(audio_path, sr=None)

    # 高频衰减处理
    b, a = butter_lowpass(2000, sr)
    y_filtered = lfilter(b, a, y)

    # 应用Schroeder混响
    y_reverb = schroeder_reverb(y_filtered, sr,m)

    # 添加随机反射声
    for _ in range(8):
        delay = np.random.uniform(0.02, 0.15)
        decay = np.random.uniform(0.1, 0.3)
        y_reverb += np.roll(y, int(sr * delay)) * decay

    # 归一化并保存
    y_reverb = y_reverb / np.max(np.abs(y_reverb))
    sf.write(output_path, y_reverb, sr)

# 混响v4 远回音
def reverberation_4(audio_path, output_path,
                    reverb_strength=0.3#混响强度
                    ):
    y, sr = librosa.load(audio_path, sr=None)
    # 模拟混响（简化版）
    y_reverb = y + reverb_strength * np.roll(y, int(sr * 0.2))  # 延迟0.1秒叠加
    sf.write(output_path, y_reverb, sr)

# 混响v5 长延音
def reverberation_5(input_path, output_path,
                    delay=0.3,#基础回声延迟时间
                    decay=0.5,#回声衰减系数
                    wet_level=0.3,#混响强度
                    dry_level=0.7,#原始信号保留比例
                    reverb_strength=1.0,#效果强度系数
                    num_echoes=6,#基础回声次数
                    env_noise=None,#可选噪声类型（'nature'或'urban'）
                    noise_intensity=0.1#环境噪声混合强度
                    ):
    def add_environmental_noise(audio, sr, noise_type='nature', intensity=0.2):
        """添加环境噪声层"""
        noise_length = len(audio)
        if noise_type == 'nature':
            # 生成自然噪声（瀑布/风声混合）
            noise = 0.6 * np.random.randn(noise_length) * intensity
            noise += 0.4 * signal.lfilter([1], [1, -0.98], np.random.randn(noise_length)) * intensity
        elif noise_type == 'urban':
            # 生成城市环境噪声
            noise = np.random.uniform(-0.5, 0.5, noise_length) * intensity
            impulse = np.zeros(noise_length)
            impulse[::sr // 10] = np.random.rand(len(impulse[::sr // 10])) * 0.8  # 随机脉冲声
            noise = signal.fftconvolve(noise, impulse, 'same') * intensity
        return noise[:noise_length]
    y, sr = librosa.load(input_path, sr=None, mono=False)

    if len(y.shape) > 1:
        y = librosa.to_mono(y)

    # 动态参数调整（非线性曲线）
    strength_factor = np.log1p(reverb_strength)
    adjusted_delay = delay * (1 + 0.3 * strength_factor)
    adjusted_decay = decay * (1 - 0.2 * strength_factor ** 2)
    adjusted_wet = wet_level * (1 + 0.8 * strength_factor)
    adjusted_echoes = num_echoes + int(3 * strength_factor)

    # 环境音处理
    if env_noise:
        env_layer = add_environmental_noise(y, sr, env_noise, noise_intensity)
        y = y * (1 - noise_intensity) + env_layer * noise_intensity

    # 混响生成（带早期反射优化）
    early_reflections = np.zeros_like(y)
    for i in [5, 10, 15, 20]:  # 毫秒级早期反射
        idx = int(i * sr / 1000)
        if idx < len(y):
            early_reflections[idx:] += y[:-idx] * (0.7 ** (i / 5))

    late_reverb = np.zeros_like(y)
    for i in range(1, adjusted_echoes + 1):
        current_delay = int(adjusted_delay * sr * i)
        current_decay = adjusted_decay ** (i / 2)  # 非线性衰减
        echo = np.roll(y, current_delay) * current_decay
        late_reverb += echo[:len(y)]

    # 信号混合（带频谱平衡）
    wet = (early_reflections * 0.4 + late_reverb * 0.6) / np.max(np.abs(early_reflections + late_reverb))
    processed = np.clip(dry_level * y + adjusted_wet * wet, -0.99, 0.99)
    sf.write(output_path, processed, sr)

# 混响v6 室内隔断音
def reverberation_6(input_path, output_path,
                    intensity=0.5,#混响强度系数
                    room_size=0.7,#空间大小模拟参数
                    feedback=0.4#反馈回路强度
                    ):
    # 检查输出文件是否存在并删除
    if os.path.exists(output_path):
        os.remove(output_path)

    y, sr = sf.read(input_path)

    # 多延迟线参数
    delays = [
        int(sr * (50 + 200 * room_size) / 2000),  # 主延迟
        int(sr * (80 + 300 * room_size) / 2000),  # 次级延迟1
        int(sr * (120 + 400 * room_size) / 2000),  # 次级延迟2
    ]

    # 生成混响尾音
    wet = y * intensity
    output = y * (1 - intensity)

    # 多延迟线处理
    for d in delays:
        delayed = np.roll(wet, d)
        output += delayed * (0.7 - 0.3 * intensity)

        # 反馈回路增强空间感
        if feedback > 0:
            for _ in range(2):
                delayed = np.roll(delayed, d // 2)
                output += delayed * feedback

    # 动态范围控制
    peak = np.max(np.abs(output))
    output = np.clip(output / peak * 0.99, -1, 1)
    sf.write(output_path, output, sr)

# 混响v7 现场音
def reverberation_7(input_path, output_path,
               delay=0.3,#混响延迟时间
               decay=0.5,#回声衰减率
               wet_level=0.3,#混响信号强度
               dry_level=0.7#原始信号强度
               ):
    # 读取音频文件
    y, sr = librosa.load(input_path, sr=None, mono=False)

    # 如果是立体声，转换为单声道
    if len(y.shape) > 1:
        y = librosa.to_mono(y)

    # 归一化音频
    y = y / np.max(np.abs(y))

    # 计算延迟的采样点数
    delay_samples = int(delay * sr)

    # 创建混响信号
    reverb_signal = np.zeros_like(y)

    # 生成多个衰减的回声
    num_echoes = 6
    for i in range(1, num_echoes + 1):
        # 计算当前回声的衰减和延迟
        current_decay = decay ** i
        current_delay = delay_samples * i

        # 创建延迟信号
        echo = np.roll(y, current_delay) * current_decay

        # 限制信号长度
        if current_delay > 0:
            echo[:current_delay] = 0

        # 累加到混响信号
        reverb_signal += echo

    # 混合原始信号和混响信号
    wet = reverb_signal / np.max(np.abs(reverb_signal))  # 归一化混响信号
    processed = (dry_level * y) + (wet_level * wet)

    # 再次归一化防止削波
    processed = processed / np.max(np.abs(processed))

    # 保存结果
    sf.write(output_path, processed, sr)

# 混响v8 室内回音
def reverberation_8(input_audio,output_path,
                        wet_gain=-6,#湿信号衰减分贝值
                        delay_ms=500,#延迟时间(毫秒)
                        overlay_position=100#叠加位置(毫秒)
                        ):
    if isinstance(input_audio, str):
        audio = AudioSegment.from_file(input_audio)
    else:
        audio = input_audio

    wet = audio + wet_gain  # 湿信号增益控制
    delayed = wet[:delay_ms] + wet[delay_ms:]  # 创建延迟效果
    reverbed = audio.overlay(delayed, position=overlay_position)
    reverbed.export(output_path, format="mp3")
    return reverbed

# 混响v9 高级混响
class AudioReverb:
    def __init__(self, file_path):
        self.audio = AudioSegment.from_file(file_path)
        self.sample_rate = self.audio.frame_rate
        self.channels = self.audio.channels

    def apply_reverb(self,
                     dry_gain=-3,
                     wet_gain=-12,
                     delay_ms=150,
                     decay=0.7,
                     iterations=3):
        """应用可调参数的多级混响效果"""
        dry = self.audio + dry_gain
        wet = self.audio + wet_gain

        # 创建多级延迟链
        result = dry
        for i in range(1, iterations + 1):
            delayed = self._create_delay(wet, delay_ms * i, decay ** i)
            result = result.overlay(delayed, position=int(delay_ms * i))

        return result

    def _create_delay(self, audio, delay_ms, gain):
        """创建带增益控制的延迟片段"""
        silence = AudioSegment.silent(duration=delay_ms,
                                      frame_rate=self.sample_rate)
        delayed = silence + (audio + gain)
        return delayed[:len(audio)]

    def export(self, output_path, processed_audio):
        processed_audio.export(output_path, format="mp3",
                               bitrate="192k")

def reverberation_9(output_path,file_path,
                    dry_gain=-2,#干信号增益
                    wet_gain=-10,#湿信号增益
                    delay_ms=120,#延迟 毫秒
                    decay=0.6,#衰减
                    iterations=4#叠层次数
                    ):
    processor = AudioReverb(output_path)
    reverbed = processor.apply_reverb(
        dry_gain=dry_gain,
        wet_gain=wet_gain,
        delay_ms=delay_ms,
        decay=decay,
        iterations=iterations
    )
    processor.export(file_path, reverbed)

  # 调用系统默认程序打开
