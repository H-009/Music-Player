import io
import os

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QIcon, QPixmap
from mutagen import MutagenError
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


class Service(object):

    # 创建歌曲封面
    @staticmethod
    def new_mp3_cover(text, save_path):
        try:
            # 创建一个350x350的透明矩形
            img = Image.new('RGBA', (350, 350), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # 定义矩形边缘颜色和宽度
            rect_color = (30, 200, 150)  # 灰色
            rect_width = 10

            # 绘制空心矩形，边缘与图片边缘对齐
            draw.rectangle([(0, 0), (350, 350)], outline=rect_color, width=rect_width)

            # 初始字体大小
            font_size = 25
            font_path = "simhei.ttf"  # 黑体字体路径

            # 计算最大可用空间（预留5像素边距）
            max_width = 350 - 2 * (rect_width + 5)
            max_height = 350 - 2 * (rect_width + 5)

            # 自动调整字体大小
            while True:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    # 获取文本边界框
                    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                    text_width = right - left
                    text_height = bottom - top

                    # 检查是否超出边界
                    if text_width <= max_width and text_height <= max_height:
                        break  # 当前字体大小合适
                    else:
                        font_size -= 1  # 减小字体大小
                        if font_size < 8:  # 最小字体大小限制
                            font_size = 8
                            break
                except Exception as e:
                    print(f"字体加载错误: {e}")
                    # 使用默认字体作为后备方案
                    font = ImageFont.load_default()
                    break

            # 计算文本位置（居中显示）
            text_x = (350 - text_width) // 2
            text_y = (350 - text_height) // 2

            # 在图片中央插入文本
            draw.text((text_x, text_y), text, fill=rect_color, font=font)

            # 保存图片
            img.save(f"{save_path}{text}.png")
        except Exception as a:
            print(a)

    # 创建歌曲缩略图
    @staticmethod
    def new_mp3_cover_ico(text, save_path):
        try:
            # 创建24x24透明图像
            img = Image.new('RGBA', (24, 24), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # 定义矩形边缘颜色和宽度
            rect_color = (30, 200, 150)  # 灰色
            rect_width = 1  # 边框宽度1px

            # 绘制空心矩形（向内缩进1像素确保边框完整）
            draw.rectangle([(1, 1), (22, 22)], outline=rect_color, width=rect_width)

            # 初始字体大小
            font_size = 6  # 初始尝试大小
            font_path = "simhei.ttf"

            # 计算最大可用空间（预留3像素边距）
            max_width = 20  # 24 - 2 * 2边距
            max_height = 20  # 24 - 2 * 2边距

            # 自动调整字体大小
            while True:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    # 使用textlength和textbbox获取更精确的尺寸
                    text_width = draw.textlength(text, font=font)
                    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                    text_height = bottom - top

                    # 检查是否超出边界
                    if text_width <= max_width and text_height <= max_height:
                        break  # 当前字体大小合适
                    else:
                        font_size -= 1
                        if font_size < 1:  # 最小字体限制
                            font_size = 1
                            break
                except:
                    font = ImageFont.load_default()
                    break

            # 获取最终文本边界框
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            text_height = bottom - top

            # 计算文本位置（居中显示）
            # 需要考虑实际绘制时的基线位置
            text_x = (24 - text_width) // 2 - left
            text_y = (24 - text_height) // 2 - top

            # 绘制文本（添加1px描边增强小尺寸可读性）
            draw.text((text_x, text_y), text, fill=rect_color, font=font, stroke_width=1)

            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)
            webp_path = os.path.join(save_path, f"{text}.webp")
            img.save(webp_path, 'WEBP', quality=90)
            return webp_path

        except Exception as e:
            print(f"生成封面失败: {str(e)}")
            return None

    #获取音频封面
    @staticmethod
    def get_mp3_cover(mp3_path, save_path, save_name):
        """
        更强大的封面提取器
        提取MP3封面并保存为原始大小的PNG文件
        兼容 ID3v2和旧版ID3v1

        参数:
            mp3_path: MP3文件路径
            save_path: 封面保存目录
            save_name: 封面文件名(不含扩展名)

        返回:
            成功返回封面路径，失败返回None
        """
        try:
            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)

            # 尝试多种方式读取ID3标签
            tags = None
            try:
                tags = ID3(mp3_path)
            except MutagenError:
                # 如果标准方式失败，尝试强制读取
                try:
                    tags = ID3(mp3_path, translate=False)
                except:
                    return None

            if not tags:
                return None

            # 查找所有可能的封面图片
            covers = []
            for tag in tags.values():
                if isinstance(tag, APIC):
                    covers.append(tag)

            # 如果没有找到封面
            if not covers:
                return None

            # 选择最佳封面（优先选择类型为'cover front'的）
            selected_cover = None
            for cover in covers:
                if cover.type == 3:  # 3表示'cover front'
                    selected_cover = cover
                    break
            if not selected_cover:
                selected_cover = covers[0]  # 如果没有front cover，使用第一个

            try:
                # 处理封面数据
                img = Image.open(io.BytesIO(selected_cover.data))

                # 转换格式为RGBA（处理透明背景）
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # 构建保存路径
                png_path = os.path.join(save_path, f"{save_name}.png")

                # 保存为原始大小的PNG
                img.save(
                    png_path,
                    'PNG',
                    optimize=True  # 启用PNG优化
                )

                return png_path

            except Exception as img_error:
                print(f"封面处理失败: {str(img_error)}")
                return None

        except Exception as e:
            print(f"封面提取失败: {str(e)}")
            return None

    # 获取音频封面 保存为缩略图
    @staticmethod
    def get_mp3_cover_ico_webp(mp3_path, save_path, save_name):
        try:
            os.makedirs(save_path, exist_ok=True)

            tags = ID3(mp3_path)
            for tag in tags.values():
                if isinstance(tag, APIC):
                    img = Image.open(io.BytesIO(tag.data))
                    webp_path = os.path.join(save_path, f"{save_name}.webp")
                    # 修改尺寸为24x24
                    img.resize((24, 24), Image.LANCZOS).save(webp_path, 'WEBP', quality=90,lossless=True)
                    return webp_path
            return None

        except Exception as e:
            print(f"封面提取失败: {str(e)}")
            return None

    # 直接返回音频封面缩略图
    @staticmethod
    def get_mp3_cover_ico(mp3_path):
        """
        提取MP3封面并转换为24x24的WEBP格式字节数据

        :param mp3_path: MP3文件路径
        :return: WEBP格式的bytes数据，如果未找到封面或出错则返回None
        """
        try:
            tags = ID3(mp3_path)
            for tag in tags.values():
                if isinstance(tag, APIC):
                    # 从字节数据加载图像
                    img = Image.open(io.BytesIO(tag.data))

                    # 修改尺寸为24x24
                    img_resized = img.resize((24, 24), Image.LANCZOS)

                    # 创建内存缓冲区
                    buffer = io.BytesIO()

                    # 将图像保存到缓冲区，格式为WEBP
                    img_resized.save(buffer, format='WEBP', quality=90, lossless=True)

                    # 获取字节数据
                    webp_data = buffer.getvalue()

                    # 关闭缓冲区释放资源
                    buffer.close()

                    return webp_data

            return None

        except Exception as e:
            print(f"封面提取失败: {str(e)}")
            return None

    # 图像转QIcon
    @staticmethod
    def bytes_to_icon(cover_bytes):
        """
        将图像字节数据转换为 QIcon
        """
        if not cover_bytes:
            return QIcon()  # 返回空图标

        pixmap = QPixmap()
        # loadFromData 会自动识别图像格式 (png, jpg, webp 等)
        # 如果加载成功返回 True，否则返回 False
        if pixmap.loadFromData(cover_bytes):
            return QIcon(pixmap)
        else:
            print("错误: 无法解析图像数据")
            return QIcon()