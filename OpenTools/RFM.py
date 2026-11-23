import ctypes
import os
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont, QPixmap,QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QGraphicsScene, QGraphicsView, QFrame
from PyQt5.QtCore import Qt, QUrl
from qfluentwidgets import FluentWindow, setTheme, Theme, FluentIcon, PopUpAniStackedWidget, NavigationItemPosition, \
    setStyleSheet, TitleLabel, ProgressRing, setThemeColor, SingleDirectionScrollArea, SimpleCardWidget, CardWidget, \
    GroupHeaderCardWidget, HeaderCardWidget, BodyLabel, ColorDialog, ComboBox, IconWidget, PushButton, CaptionLabel, \
    StrongBodyLabel, SubtitleLabel, LargeTitleLabel, ToolButton, Pivot, OpacityAniStackedWidget, FlipView, SwitchButton, \
    InfoBar, InfoBarPosition, Dialog, FlowLayout, TransparentToolButton, RoundMenu, Action, MSFluentTitleBar, \
    FluentStyleSheet


class MainUI(FluentWindow):
    def __init__(self):
        super().__init__()
        #self.setCustomBackgroundColor(QColor(242, 242, 242), QColor(25, 33, 42))

        # 初始化数据
        self.metaverse_path = os.getenv('APPDATA')+"\\STD Studio\\Metaverse 4" # 元境根目录
        self.config_path = self.metaverse_path+"\\Config" # 配置文件夹
        self.users_path = self.metaverse_path+"\\Users"  # 用户文件夹

        self.login_path = self.config_path + "\\login.json"  # 登录配置
        self.theme_path = self.config_path + "\\theme.json"  # 主题配置
        self.zoom_path = self.config_path + "\\zoom.json"  # 缩放配置
        self.wallpaper_path = self.config_path + "\\wallpaper.json"  # 壁纸引擎配置

        self.init_window() # 初始化窗口
        self.init_navigationInterface() # 初始化导航栏

    # 初始化窗口
    def init_window(self):
        # 基础属性
        self.setWindowTitle("资源文件管理器")
        self.setWindowIcon(QIcon("Metaverse 4.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("资源文件管理器")

        screen_size = QApplication.primaryScreen().availableGeometry()
        # 中心坐标
        h = 1200
        w = 800
        x = (screen_size.width() - h) // 2
        y = (screen_size.height() - w) // 2

        self.setGeometry(x,y,h,800)


    # 初始化导航栏
    def init_navigationInterface(self):
        self.navigationInterface.setReturnButtonVisible(False)  # 隐藏返回按钮
        self.navigationInterface.setExpandWidth(150) # 固定抽屉长度

        # 资源文件
        self.ResourceFile = QWidget(self)
        self.ResourceFile.setObjectName("ResourceFile")
        self.init_ResourceFile() # 初始化资源文件
        self.addSubInterface(
            self.ResourceFile,
            FluentIcon.DOCUMENT,
            "资源文件"
        )

        # 内置图标
        self.BuiltInIcon = QWidget(self)
        self.BuiltInIcon.setObjectName("BuiltInIcon")
        #self.init_BuiltInIcon() # 初始化内置图标
        self.addSubInterface(
            self.BuiltInIcon,
            FluentIcon.EMOJI_TAB_SYMBOLS,
            "内置图标"
        )


        # 工具箱
        self.toolbox = QWidget(self)
        self.toolbox.setObjectName("toolbox")
        self.addSubInterface(
            self.toolbox,
            FluentIcon.DEVELOPER_TOOLS,
            "工具箱",
            NavigationItemPosition.BOTTOM
        )


        # 设置
        self.setting = QWidget(self)
        self.setting.setObjectName("setting")
        self.init_setting() # 初始化设置
        self.addSubInterface(
            self.setting,
            FluentIcon.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM
        )

    # 初始化库
    def init_ResourceFile(self):
        # 嵌入垂直布局
        self.library_vlayout = QVBoxLayout(self.ResourceFile)

        # 嵌入滚动画布
        self.library_scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)
        self.library_scrollArea.setWidgetResizable(True) # 内部控件可调整大小
        self.library_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.library_scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}") # 滚动区域透明

        # 设置视图
        library_view = QWidget()
        library_view.setStyleSheet("QWidget{background: transparent}") # 视图透明
        self.library_view_layout = FlowLayout(library_view) #视图布局
        self.library_view_layout.setSpacing(5) # 设置间距
        self.library_view_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(5):
            # 卡片
            card = SimpleCardWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 20, 10, 10)
            card.setLayout(layout)
            ico = IconWidget() # 图标画布
            ico.setIcon(FluentIcon.APPLICATION)
            ico.setFixedSize(64, 64)
            layout.addWidget(ico,alignment=Qt.AlignHCenter)
            text = SubtitleLabel("应用程序") # 程序标题
            layout.addWidget(text,alignment=Qt.AlignHCenter)
            button_layout = QHBoxLayout() # 按钮布局
            button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
            runButton = TransparentToolButton(FluentIcon.PLAY) # 运行按钮
            runButton.setToolTip("运行")
            runButton.clicked.connect(lambda _, btn=runButton: self.run_app(btn))
            button_layout.addWidget(runButton)
            moreButton = TransparentToolButton(FluentIcon.MORE) # 更多按钮
            moreButton.clicked.connect(lambda _, btn=moreButton: self.program_showMenu(btn))
            button_layout.addWidget(moreButton)
            button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
            layout.addLayout(button_layout)
            self.library_view_layout.addWidget(card)

        # 滚动画布嵌入视图
        self.library_scrollArea.setWidget(library_view)
        # 嵌入滚动画布
        self.library_vlayout.addWidget(self.library_scrollArea)

    # 程序菜单
    def program_showMenu(self,btn):
        # 创建菜单
        menu = RoundMenu(parent=self)
        #version_action.triggered.connect(self.onVersion)
        #uninstall_action.triggered.connect(self.onUninstall)
        version_action = Action(FluentIcon.INFO, "详情", self)
        menu.addAction(version_action)
        uninstall_action = Action(FluentIcon.DELETE, "卸载", self)
        menu.addSeparator()  # 添加分隔线（可选，图中无但常见）
        menu.addAction(uninstall_action)
        # 计算弹出位置（在按钮下方显示）
        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        menu.exec(pos)

    # 初始化设置
    def init_setting(self):
        # 嵌入垂直布局
        self.setting_vlayout = QVBoxLayout(self.setting)
        # 滚动画布
        self.setting_scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical) # 竖直方向
        self.setting_scrollArea.setWidgetResizable(True) # 内部控件可调整大小
        self.setting_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setting_scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}") # 滚动区域透明

        # 设置视图
        self.setting_view = QWidget()
        self.setting_view.setStyleSheet("QWidget{background: transparent}") # 视图透明
        self.setting_view_layout = QVBoxLayout(self.setting_view) #视图布局

        # 主题标题
        self.setting_view_layout.addWidget(StrongBodyLabel("主题"))
        # 主题卡片
        card = SimpleCardWidget() # 简单卡片
        hBoxLayout = QHBoxLayout() # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.PALETTE) # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout() # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("主题模式")) # 文字标签
        contentLabel = CaptionLabel("设置配色方案") # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.themem_model_combox = ComboBox() # 下拉框
        self.themem_model_combox.setFixedWidth(120)
        self.themem_model_combox.addItems(["明亮", "黑暗", "自动"])
        hBoxLayout.addWidget(iconWidget) # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.themem_model_combox)
        card.setLayout(hBoxLayout) # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card) # 添加卡片到滚动窗口
        # 强调色卡片
        card = SimpleCardWidget() # 简单卡片
        hBoxLayout = QHBoxLayout() # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.HIGHTLIGHT) # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout() # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("强调色")) # 文字标签
        contentLabel = CaptionLabel("设置主题强调色") # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        button = PushButton("选择颜色") # 颜色选择器按钮
        button.setFixedWidth(120)
        hBoxLayout.addWidget(iconWidget) # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(button)
        card.setLayout(hBoxLayout) # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card) # 添加卡片到滚动窗口

        # 缩放标题
        self.setting_view_layout.addWidget(StrongBodyLabel("缩放"))
        # 缩放卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout() # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.ZOOM) # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout() # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("缩放")) # 文字标签
        contentLabel = CaptionLabel("更改界面文本和其他项目的大小") # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.zoom_switch = SwitchButton() # 颜色选择器按钮
        self.zoom_switch.setOffText("关")
        self.zoom_switch.setOnText("开")
        self.zoom_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget) # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.zoom_switch)
        card.setLayout(hBoxLayout) # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card) # 添加卡片到滚动窗口

        # 壁纸引擎标题
        self.setting_view_layout.addWidget(StrongBodyLabel("壁纸引擎"))
        # 壁纸引擎卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout() # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.BRUSH) # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout() # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("壁纸引擎")) # 文字标签
        contentLabel = CaptionLabel("激活壁纸引擎") # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.wallpaper_switch = SwitchButton() # 颜色选择器按钮
        self.wallpaper_switch.setOffText("关")
        self.wallpaper_switch.setOnText("开")
        self.wallpaper_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget) # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.wallpaper_switch)
        card.setLayout(hBoxLayout) # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card) # 添加卡片到滚动窗口

        # 底部弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        # 滚动画布嵌入视图
        self.setting_scrollArea.setWidget(self.setting_view)
        # 嵌入滚动画布
        self.setting_vlayout.addWidget(self.setting_scrollArea)


    # 运行应用程序
    def run_app(self,btn):
        if btn.toolTip() == "停止": # 停止
            w = Dialog("要强制关闭吗？", "强制退出可能会导致数据丢失", self)
            w.yesButton.setText("确认")
            w.cancelButton.setText("取消")
            if w.exec():
                btn.setIcon(FluentIcon.PLAY)
                btn.setToolTip("运行")

        elif btn.toolTip() == "运行": # 运行
            btn.setIcon(FluentIcon.PAUSE)
            btn.setToolTip("停止")
            InfoBar.success(
                title='成功',
                content="程序开始运行",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

if __name__ == "__main__":

    # 1. 启用OpenGL渲染
    QApplication.setAttribute(Qt.AA_UseOpenGLES, True)
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)

    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 支持非整数缩放比
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication([])
    # 主题
    setTheme(Theme.AUTO)
    mainWin = MainUI()
    mainWin.show()

    sys.exit(app.exec_())