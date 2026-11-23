import ctypes
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QFont

# 配置字体调节v2
def set_dual_font(widget, small_widgets=None):
    """
    双字体方案自适应函数

    :param widget: 父控件（通常是主窗口）
    :param small_widgets: 需要使用小字体的控件列表 [widget1, widget2, ...]
    """

    if small_widgets is None:
        small_widgets = []

    # ---------- 字体配置（写死在函数内部） ----------
    FONT_LARGE = {
        "base": 11,
        "min": 11,
        "max": 13
    }

    FONT_SMALL = {
        "base": 9,
        "min": 9,
        "max": 10
    }

    # ---------- 获取系统缩放 ----------
    def get_scale():
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            raw_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            rounded_scale = round(raw_scale * 4) / 4

            print(f"系统缩放 {rounded_scale:.2f}")

            return rounded_scale
        except Exception as e:
            print(e)
            print(f"系统缩放 1.0 (100%) - 使用默认值")
            return 1.0

    scale = get_scale()

    # ---------- 计算字号 ----------
    def calc_size(cfg):
        screen = QApplication.primaryScreen()
        w, h = screen.size().width(), screen.size().height()

        if w == 1920 and h == 1080 and scale == 1.0:
            return cfg["max"]
        elif w == 1920 and h == 1080 and scale == 1.25:
            return cfg["min"]
        else:
            ratio = min(w / 1920, h / 1080)
            size = int(cfg["base"] * ratio * scale)
            return min(max(size, cfg["min"]), cfg["max"])

    large_size = calc_size(FONT_LARGE)
    small_size = calc_size(FONT_SMALL)

    print(f"大字方案 {large_size}")
    print(f"小字方案 {small_size}")

    # ---------- 递归应用 ----------
    def apply(target):
        # 判断是否是小字体控件
        use_small = False
        for sw in small_widgets:
            if target is sw or target in sw.findChildren(QWidget):
                use_small = True
                break

        font = target.font()
        font.setPointSize(small_size if use_small else large_size)
        font.setStyleStrategy(QFont.PreferAntialias)
        target.setFont(font)

        for child in target.findChildren(QWidget):
            apply(child)

    apply(widget)

# 智能字体调节v1
def set_resolution_font(widget, min_size=8, max_size=24, base_size=12, exclude_widgets=None):
    """
    智能分辨率字体适配函数(保留原字体)
    :param widget: 目标控件对象
    :param base_size: 基准字号(1920x1080下的标准字号)
    :param min_size: 最小允许字号
    :param max_size: 最大允许字号
    :param exclude_widgets: 要排除的控件列表(不调整这些控件的字体)
    """
    if exclude_widgets is None:
        exclude_widgets = []

    def get_system_scale():
        """返回系统缩放比例（1.0/1.25等标准值）"""
        try:
            # Windows API方法（精度最高）
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            return round(scale * 4) / 4  # 标准化为1.0/1.25等
        except:
            # 备用方法：注册表查询
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Control Panel\Desktop")
                logpixels = winreg.QueryValueEx(key, "LogPixels")[0]
                return round((logpixels / 96) * 4) / 4
            except:
                return 1.0

    scale = get_system_scale()
    print("系统缩放", scale)

    def _calc_font_size():
        screen = QApplication.primaryScreen()
        width = screen.size().width()
        height = screen.size().height()

        # 动态计算公式
        if width == 1920 and height == 1080 and scale == 1.0:  # 1920x1080 缩放100 最大字体
            return max_size
        elif width == 1920 and height == 1080 and scale == 1.25:  # 1920x1080 缩放125 最小字体
            return min_size
        else:
            ratio = min(width / 1920, height / 1080)
            scaled_size = int(base_size * ratio * scale)
            return min(max(scaled_size, min_size), max_size)

    def _apply_font(target_widget):
        # 跳过排除的控件
        if target_widget in exclude_widgets:
            return

        # 获取控件原有字体
        original_font = target_widget.font()
        # 仅修改字号
        original_font.setPointSize(_calc_font_size())
        original_font.setStyleStrategy(QFont.PreferAntialias)
        target_widget.setFont(original_font)

        for child in target_widget.findChildren(QWidget):
            _apply_font(child)

    _apply_font(widget)


# DPI智能感知 实验中
class FontScaler:
    def __init__(self, base_dpi=96, base_size=12):
        self.base_dpi = base_dpi
        self.base_size = base_size

    def get_scaled_font(self, widget):
        screen = QApplication.primaryScreen()
        logical_dpi = screen.logicalDotsPerInch()
        scale_factor = logical_dpi / self.base_dpi

        original_font = widget.font()
        scaled_size = max(8, min(24, round(self.base_size * scale_factor)))
        original_font.setPointSize(scaled_size)
        return original_font


def apply_adaptive_font(root_widget, base_size=12):
    scaler = FontScaler(base_size=base_size)

    def _apply(widget):
        if hasattr(widget, 'font'):
            widget.setFont(scaler.get_scaled_font(widget))
        for child in widget.findChildren(QWidget):
            _apply(child)

    _apply(root_widget)
