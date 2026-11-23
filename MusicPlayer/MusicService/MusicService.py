import base64
import io
import json
import os
import random
import struct
import subprocess
import sys

from PIL import Image
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QWidget, QListWidget
from mutagen.mp3 import MP3
import datetime
from mutagen.easyid3 import EasyID3
from pymediainfo import MediaInfo
from mutagen import File


#全局退出
def EXIT():
    sys.exit()


#返回无mp3后缀字符串
def remove_mp3_extension(filename):
    """
    去除字符串中的.mp3后缀

    参数:
    filename (str): 格式为XXX.mp3的字符串

    返回:
    str: 去掉.mp3后缀的字符串
    """
    # 检查字符串是否以.mp3结尾
    if filename.endswith('.mp3'):
        # 返回去掉.mp3后缀的字符串
        return filename[:-4]
    elif filename.endswith('.MP3'):
        # 返回去掉.mp3后缀的字符串
        return filename[:-4]
    else:
        # 如果字符串不是以.mp3结尾，则返回原字符串
        # 或者你可以选择抛出一个异常或进行其他处理
        return filename

#手动获取歌曲一般信息
def read_mp3_tag_v2(path):
    """
    处理mp3解析，获取ID3V2信息
    """
    def parse_ID3V2_frames(frames_ID3):
        """
        解析帧数据
        :param frames_ID3:
        :return:
        """
        pointer = 0
        frames_size = len(frames_ID3)
        frame = {}
        while pointer < frames_size - 10:
            frame_header_bin = frames_ID3[pointer:pointer + 10]
            frame_header = struct.unpack('>4sI2s', frame_header_bin)
            frame_body_size = frame_header[1]
            if frame_body_size == 0:
                break
            pointer += 10
            frame[frame_header[0]] = frames_ID3[pointer:pointer + frame_body_size]
            pointer += frame_body_size
        TIT2_bin = frame.get(b'TIT2', None)
        TPE1_bin = frame.get(b'TPE1', None)
        TALB_bin = frame.get(b'TALB', None)

        if TALB_bin:
            encoding = encodings[TALB_bin[0]]
            frame[b'TALB'] = TALB_bin[1:].decode(encoding)
        if TIT2_bin:
            encoding = encodings[TIT2_bin[0]]
            frame[b'TIT2'] = TIT2_bin[1:].decode(encoding)
        if TPE1_bin:
            encoding = encodings[TPE1_bin[0]]
            frame[b'TPE1'] = TPE1_bin[1:].decode(encoding)
        return frame


    def parse_ID3V2_head(head_bin):
        """
        获取数据头位置
        :param head_bin:
        :return:
        """
        if head_bin[:3] != b'ID3':
            return None
        frames_size = (head_bin[6] << 21 | head_bin[7] << 14 |
                           head_bin[8] << 7 | head_bin[9])
        return frames_size

    encodings = ['GBK', 'UTF-16', 'UTF-16BE', 'UTF-8']

    f = open(path, 'rb')
    frames_bin_size = parse_ID3V2_head(f.read(10))
    if frames_bin_size is None:
        f.close()
        return ["标题 None","作者 None","专辑 None"]

    frames_bin = f.read(frames_bin_size - 10)
    f.close()
    frames = parse_ID3V2_frames(frames_bin)

    info = []

    try:
        tit2 = frames[b'TIT2']  # 标题
        info.append(f'标题 ' + tit2)
    except KeyError:
        info.append(f"标题 None")

    try:
        tpe1 = frames[b'TPE1']  # 作者
        info.append(f'艺术家 ' + tpe1)
    except KeyError:
        info.append(f"艺术家 None")

    try:
        talb = frames[b'TALB']  # 专辑
        info.append(f'专辑 ' + talb)
    except KeyError:
        info.append(f"专辑 None")

    return info

#获取歌曲一般信息
def read_mp3_tag_v2_mutagen(path):
    """
    使用 mutagen.mp3 解析 MP3 标签信息
    :param path: MP3 文件路径
    :return: 包含标题、艺术家、专辑信息的列表
    """
    try:
        # 使用 mutagen 读取 MP3 文件
        audio_file = MP3(path)
        tags = audio_file.tags

        # 初始化返回信息列表
        info = []

        # 提取标题 (TIT2)
        title = tags.get('TIT2', [None])[0] if tags and 'TIT2' in tags else None
        info.append(f'标题 {title if title else "None"}')

        # 提取艺术家 (TPE1)
        artist = tags.get('TPE1', [None])[0] if tags and 'TPE1' in tags else None
        info.append(f'作者 {artist if artist else "None"}')

        # 提取专辑 (TALB)
        album = tags.get('TALB', [None])[0] if tags and 'TALB' in tags else None
        info.append(f'专辑 {album if album else "None"}')

        # 如果没有标签信息，返回默认值
        if not info:
            return ["标题 None", "作者 None", "专辑 None"]

        return info

    except Exception as e:
        # 处理文件读取或解析错误
        print(f"错误读取MP3标签: {e}")
        return ["标题 None", "作者 None", "专辑 None"]

#获取歌曲时长 秒
def senior_time(path_mp3):
    # 加载MP3文件
    audio_mp3 = MP3(path_mp3, ID3=EasyID3)

    file_time2 = audio_mp3.info.length
    file_time2 = int(file_time2)

    return file_time2

#获取歌曲时长 分钟
def get_audio_duration(file_path: str) -> str:
    """ 支持MP3/WAV/FLAC格式，返回格式自动去除分钟前导零 """
    try:
        audio = File(file_path)
        if audio is None:
            raise ValueError("不支持的音频格式")

        # 核心修改点：分钟部分使用普通格式化，秒保持两位数
        mins, secs = divmod(int(audio.info.length), 60)
        return f"{mins}:{secs:02d}"  # 去掉了分钟前的0

    except Exception as e:
        return f"错误: {str(e)}"

#格式化分钟
def format_minutes(minutes):
    # 确保输入是整数
    if not isinstance(minutes, int):
        raise ValueError("Input must be an integer")

    # 计算小时和剩余的分钟
    hours = minutes // 60
    remaining_minutes = minutes % 60

    # 格式化分钟数为 X:XX 形式
    formatted_minutes = f"{hours}:{remaining_minutes:02d}"

    return formatted_minutes

#获取音频所有轨道信息
def get_audio_tracks(audio_path):
    """
    解析音频文件所有轨道信息
    参数:
        audio_path (str): 音频文件路径
    返回:
        str: 格式化后的轨道信息字符串
    """

    def _format_track_data(data, indent=0):
            """递归格式化字典/列表数据"""
            lines = []
            prefix = "  " * indent
            if isinstance(data, dict):
                for k, v in data.items():
                    lines.append(f"{prefix}{k}:")
                    lines += _format_track_data(v, indent+1)
            elif isinstance(data, list):
                for item in data:
                    lines += _format_track_data(item, indent)
            else:
                lines.append(f"{prefix}{str(data)}")
            return lines

    try:
        # 路径安全校验‌:ml-citation{ref="2" data="citationList"}
        if not os.path.isfile(audio_path):
            return f"错误: 文件不存在 - {audio_path}"

        media_info = MediaInfo.parse(audio_path)
        output = []

        # 按轨道类型分类‌:ml-citation{ref="4" data="citationList"}
        track_types = {}
        for track in media_info.tracks:
            track_type = track.track_type
            if track_type not in track_types:
                track_types[track_type] = []
            track_types[track_type].append(track)

        # 格式化输出
        for track_type, tracks in track_types.items():
            output.append(f"▣ 轨道类型: {track_type}")
            for idx, track in enumerate(tracks, 1):
                # 递归展开属性‌:ml-citation{ref="3" data="citationList"}
                output += _format_track_data(track.to_data())

        return "\n".join(output)

    except Exception as e:
        return f"解析异常: {str(e)}"


#格式化时间戳字符串
def format_seconds(seconds_str: str) -> str:
    try:
        seconds = int(seconds_str)
    except ValueError:
        return "0秒"

    if seconds < 60:
        return f"{seconds}秒"
    elif 60 <= seconds < 3600:
        return f"{seconds // 60}分钟"
    else:
        hours = seconds // 3600
        return f"{hours}小时"

def create_directory(base_path, folder_name):
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

def replace_file_line(file_path, line_number, new_content):
    """
    替换文本文件中指定行的内容

    参数:
        file_path (str): 目标文件路径
        line_number (int): 要替换的行号（从0开始计数）
        new_content (str): 要写入的新内容（自动添加换行符）

    返回:
        bool: 操作是否成功
    """
    try:
        # 读取所有行
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证行号有效性
        if line_number < 0 or line_number >= len(lines):
            print(f"错误：行号 {line_number} 超出范围（文件共 {len(lines)} 行）")
            return False

        # 替换指定行（保留原换行符风格）
        lines[line_number] = new_content.rstrip('\n') + '\n'

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return True

    except Exception as e:
        print(f"操作失败：{str(e)}")
        return False

def replace_above_separator(file_path: str) -> bool:
    """
    处理包含11行的文本文件，用分隔行(第6行)以下的内容替换分隔行以上的内容
    并在分隔行前后添加空行

    参数:
    file_path (str): 文本文件路径

    返回:
    bool: 操作是否成功
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证文件行数
        if len(lines) != 11:
            print(f"错误：文件必须包含11行，当前有{len(lines)}行")
            return False

        # 第6行是分隔行(索引为5)
        separator_line = lines[5]

        # 获取分隔行以下的内容(第7-11行，索引6-10)
        below_separator = lines[6:]

        # 构建新内容：用分隔行以下的内容替换分隔行以上的内容
        # 并在分隔行前后添加空行
        new_content = below_separator + ['\n', separator_line] + below_separator

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)

        return True

    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return False
    except PermissionError:
        print(f"错误：没有文件写入权限")
        return False
    except Exception as e:
        print(f"错误：{str(e)}")
        return False

def replace_above_separator2(file_path: str) -> bool:
    """
    处理包含5行的文本文件，用分隔行(第3行)以下的内容替换分隔行以上的内容
    并在分隔行前后添加空行

    参数:
    file_path (str): 文本文件路径

    返回:
    bool: 操作是否成功
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证文件行数
        if len(lines) != 5:
            print(f"错误：文件必须包含5行，当前有{len(lines)}行")
            return False

        # 第3行是分隔行(索引为2)
        separator_line = lines[2]

        # 获取分隔行以下的内容(第4-5行，索引3-4)
        below_separator = lines[3:]

        # 构建新内容：用分隔行以下的内容替换分隔行以上的内容
        # 并在分隔行前后添加空行
        new_content = below_separator + ['\n', separator_line] + below_separator

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)

        return True
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False

def get_duration_ffmpeg_fast(file_path):
    """
    用 FFmpeg 获取音频时长并返回 MM:SS 格式

    参数:
        file_path: 音频文件路径
        ffprobe_path: ffprobe可执行文件路径（默认从环境变量查找）

    返回:
        str: 格式为 "MM:SS" 的时长（如 "03:45"），失败返回 "00:00"
    """
    cmd = [
        "ffprobe.dll",
        '-v', 'error',
        '-select_streams', 'a',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        file_path
    ]
    try:
        # 获取原始秒数
        result = subprocess.run(cmd, capture_output=True, text=True, check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW,
                                shell=True
                                )
        total_seconds = round(float(result.stdout.strip()))

        # 转换为 MM:SS
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:01d}:{seconds:02d}"  # 补零对齐

    except Exception as e:
        print(f"FFmpeg 解析失败: {e}")
        return "00:00"  # 失败返回默认值

def get_duration_ffmpeg_fast2(file_path):
    """FFmpeg 最快解析（无缓存，首次调用约 5-50ms）"""
    cmd = [
        'ffprobe.dll',
        '-v', 'error',          # 屏蔽日志
        '-select_streams', 'a', # 仅检查音频流
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',       # 纯数字输出（无格式）
        file_path
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            shell=True
        )
        return round(float(result.stdout.strip()))
    except Exception as e:
        print(f"FFmpeg 解析失败: {e}")
        return None

def find_list_indices(list_widget: QListWidget,
                      target: str,
                      exact_match: bool = True,
                      case_sensitive: bool = True) -> list:
    """
    在 QListWidget 中查找包含指定字符串的项索引

    参数：
    - list_widget: 要搜索的 QListWidget 对象
    - target: 要查找的目标字符串
    - exact_match: True 精确匹配，False 模糊匹配（默认True）
    - case_sensitive: 是否区分大小写（默认True）

    返回：
    - 包含所有匹配项索引的列表（从0开始）
    """
    indices = []

    # 预处理目标字符串
    processed_target = target.strip()
    if not case_sensitive:
        processed_target = processed_target.lower()

    # 遍历所有项
    for row in range(list_widget.count()):
        item = list_widget.item(row)
        if not item:  # 跳过空项
            continue

        # 获取并处理项文本
        text = item.text().strip()
        if not case_sensitive:
            text = text.lower()

        # 匹配判断
        if exact_match:
            if text == processed_target:
                indices.append(row)
        else:
            if processed_target in text:
                indices.append(row)

    return indices

# 设置全部字体 系统内置字体
def set_all_font_sys(widget, font_name):
    """
    递归遍历所有控件并设置字体样式（仅修改字体名称，保持其他属性不变）
    :param widget: 当前控件
    :param font_name: 字体名称（如"Arial"）
    """
    # 获取当前字体
    current_font = widget.font()
    # 仅修改字体名称，保持其他属性不变
    current_font.setFamily(font_name)
    # 设置新字体
    widget.setFont(current_font)

    # 递归遍历子控件
    for child in widget.children():
        if isinstance(child, QWidget):
            set_all_font_sys(child, font_name)

# 设置全部字体 本地路径字体
def set_all_font_local(widget, font_path):
    """
    递归遍历所有控件并设置字体样式（使用本地字体文件，保持其他属性不变）
    :param widget: 当前控件
    :param font_path: 本地字体文件路径
    """

    # 创建 QFontDatabase 实例
    font_db = QFontDatabase()
    # 加载本地字体文件
    font_id = font_db.addApplicationFont(font_path)
    if font_id != -1:
        # 获取字体家族名称
        font_families = font_db.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]

            # 递归遍历当前控件及其子控件
            def apply_font_to_widget(w):
                # 获取当前控件的字体
                current_font = w.font()
                # 获取当前字体大小
                current_font_size = current_font.pointSize()
                # 创建新字体，使用加载的字体家族和当前字体大小
                new_font = font_db.font(font_family, "", current_font_size)
                # 设置新字体
                w.setFont(new_font)
                # 递归遍历子控件
                for child in w.children():
                    if isinstance(child, QWidget):
                        apply_font_to_widget(child)

            apply_font_to_widget(widget)

def save_colored_images_back_to_json(
        json_path,
        target_color_rgb_str  # 目标颜色，比如 "255,0,0" 或 "0,0,0" 或 "30,200,150"
):
    def rgb_str_to_tuple(rgb_str):
        try:
            r, g, b = map(int, rgb_str.split(','))
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError(f"RGB 值必须在 0~255 之间，但得到 R={r}, G={g}, B={b}")
            return (r, g, b)
        except Exception as e:
            raise ValueError(f"无效的 RGB 字符串: '{rgb_str}'，应为 'R,G,B' 格式，如 '255,0,0'。错误：{e}")

    # --- 1. 解析目标颜色 ---
    try:
        target_rgb = rgb_str_to_tuple(target_color_rgb_str)
    except ValueError as e:
        print(f"❌ 颜色解析失败：{e}")
        return

    # --- 2. 读取 JSON 文件 ---
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            resources = json.load(f)
    except Exception as e:
        print(f"❌ 无法读取或解析 JSON 文件 '{json_path}'，错误：{e}")
        return

    colored_resources = {}
    total_images = len(resources)
    success_count = 0
    fail_count = 0
    skipped_all_transparent = 0

    # --- 3. 遍历并处理每张图片 ---
    for idx, (key, base64_str) in enumerate(resources.items(), 1):

        try:
            # --- 3.1 解码 Base64 ---
            image_bytes = base64.b64decode(base64_str)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            pixels = image.load()
            width, height = image.size

            has_visible_pixels = False

            # --- 3.2 遍历像素并变色 ---
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    if a == 0:
                        continue  # 跳过透明
                    has_visible_pixels = True

                    # 只要不是透明，就设置为 target_rgb
                    if a > 0:
                        pixels[x, y] = (target_rgb[0], target_rgb[1], target_rgb[2], a)

            if not has_visible_pixels:
                skipped_all_transparent += 1
                colored_resources[key] = base64_str  # 保持原样
                continue

            # --- 3.3 编码回 Base64，更新 JSON ---
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            colored_image_bytes = buffered.getvalue()
            colored_base64_str = base64.b64encode(colored_image_bytes).decode('utf-8')

            colored_resources[key] = colored_base64_str
            success_count += 1

            # 可选：比较 Base64 长度变化
            old_len = len(base64_str)
            new_len = len(colored_base64_str)

        except Exception as e:
            fail_count += 1

    # --- 4. 保存结果回 JSON 文件 ---
    try:
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(colored_resources, json_file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 保存 JSON 文件失败：{json_path}，错误：{e}")