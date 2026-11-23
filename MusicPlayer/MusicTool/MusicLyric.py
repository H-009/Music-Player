import os
import re
import sys
import traceback
from collections import defaultdict

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, SYLT




def extract_lyrics(file_path, name,path2,output_path=None):
    """
    提取歌词并保存为LRC文件（时间戳保留版）
    参数:
        file_path: 输入文件路径 (支持.mp3或.lrc)
        output_path: 自定义输出路径 (默认同源文件目录)
    返回:
        list: 包含时间戳和歌词的列表，格式为 [时间戳]歌词
    """

    def write_default_lyrics(path):
        """统一处理默认歌词写入"""
        default_content = '[00:00.00]纯音乐，请欣赏'
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            return [default_content]
        except Exception as e:
            print(f"写入默认歌词失败: {e}")
            return []

    # 处理LRC文件
    if file_path.lower().endswith('.lrc'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"LRC读取错误: {e}")
            return write_default_lyrics(output_path) if output_path else ['[00:00.00]暂无歌词']

    # 处理MP3文件
    try:
        if not output_path:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(os.path.dirname(file_path), f"{base_name}.lrc")

        audio = MP3(file_path, ID3=ID3)
        if not audio.tags:
            return write_default_lyrics(output_path)

        lyrics_data = []
        has_valid_lyrics = False
        # 正则表达式匹配标准时间戳格式
        timestamp_pattern = re.compile(r'^$\d+:\d{2}\.\d{2}$')

        for tag in audio.tags.values():
            if isinstance(tag, USLT) and tag.text:
                for line in tag.text.splitlines():
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue
                    # 检查是否已包含有效时间戳
                    if timestamp_pattern.match(stripped_line):
                        # 如果已有时间戳，直接使用
                        lyrics_data.append(stripped_line)
                    else:
                        # 无时间戳的行添加默认时间戳
                        lyrics_data.append(f"{stripped_line}")
                    has_valid_lyrics = True

            elif isinstance(tag, SYLT) and tag.lyrics:
                for ts, text in tag.lyrics:
                    if text.strip():
                        mins, ms = divmod(ts, 60000)
                        secs, cs = divmod(ms, 1000)
                        time_str = f"[{mins:02d}:{secs:02d}.{cs//10:02d}]"
                        lyrics_data.append(f"{time_str}{text.strip()}")
                        has_valid_lyrics = True

        if not has_valid_lyrics:
            return write_default_lyrics(output_path)

        # 后处理：确保每行只有一个时间戳
        processed_lyrics = []
        for line in lyrics_data:
            # 查找所有时间戳
            timestamps = timestamp_pattern.findall(line)
            if len(timestamps) > 1:
                # 如果有多个时间戳，只保留最后一个
                last_timestamp = timestamps[-1]
                content = line[line.rfind(']')+1:].strip()
                processed_line = f"{last_timestamp}{content}"
            else:
                processed_line = line.replace('] ', ']', 1)  # 只替换第一个空格
            processed_lyrics.append(processed_line)
        if not os.path.exists(path2 + name):
            os.makedirs(path2 + name)

        with open(output_path, 'w', encoding='utf-8') as f:
            # 文件夹不存在则创建文件夹
            f.write('\n'.join(processed_lyrics))

        return processed_lyrics

    except Exception as e:
        # 获取错误追踪信息
        tb = traceback.extract_tb(sys.exc_info()[2])
        # 获取错误发生的行号
        line_number = tb[-1].lineno
        print("写入歌词函数发生错误", e, '所在', line_number)
        return write_default_lyrics(output_path) if output_path else ['[00:00.00]暂无歌词']


def parse_lrc_file(lrc_path, model=True, line_lyric=None):
    """
    解析LRC文件，兼容多种时间格式

    参数:
        lrc_path: LRC文件路径
        model: 是否合并同时间戳的歌词 (True/False)
        line_lyric: 当model=True时，限制每个时间戳最多合并的行数 (None表示不限制)

    返回:
        list: 包含时间戳和歌词的元组列表 [(时间戳, 歌词)]
    """
    lyrics_dict = defaultdict(list)
    time_pattern = re.compile(r'\[(-?\d{2})[:.](-?\d{2})[:.](-?\d{1,3})')

    with open(lrc_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('[ti:', '[ar:', '[al:')):
                continue

            matches = list(time_pattern.finditer(line))
            if not matches:
                continue

            lyric = line[matches[-1].end() + 1:].strip()
            for match in matches:
                mins, secs, frac = match.groups()
                total_sec = abs(int(mins)) * 60 + abs(int(secs)) + abs(int(frac)) / 1000
                if '-' in mins + secs + frac:
                    total_sec *= -1
                time_key = round(total_sec, 3)
                if lyric not in lyrics_dict[time_key]:  # 避免重复添加相同歌词
                    lyrics_dict[time_key].append(lyric)

    # 处理合并同时间戳的歌词
    if model:
        line_lyric += 1 #消除索引 归正索引
        if line_lyric is not None and line_lyric > 0:
            # 限制每个时间戳最多合并的行数
            lyrics_data = [
                (time, '\n'.join(lyrics[:line_lyric]))
                for time, lyrics in sorted(lyrics_dict.items())
            ]
        else:
            # 不限制合并行数
            lyrics_data = [
                (time, '\n'.join(lyrics))
                for time, lyrics in sorted(lyrics_dict.items())
            ]
    else:
        # 不合并同时间戳歌词，只取第一条
        lyrics_data = [
            (time, lyrics[0])
            for time, lyrics in sorted(lyrics_dict.items())
        ]

    return lyrics_data