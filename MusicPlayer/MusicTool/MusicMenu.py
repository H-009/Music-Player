from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QMenu, QAction


class ListWidgetMenupyqtSignals(QObject):
    """自定义信号容器"""
    song_play = pyqtSignal()
    song_update = pyqtSignal()
    song_import = pyqtSignal()
    song_export = pyqtSignal()
    song_path = pyqtSignal()
    song_rename = pyqtSignal()
    song_del = pyqtSignal()

    playlist_skip = pyqtSignal()
    playlist_update = pyqtSignal()
    playlist_import = pyqtSignal()
    playlist_export = pyqtSignal()
    playlist_path = pyqtSignal()
    playlist_new = pyqtSignal()
    playlist_rename = pyqtSignal()
    playlist_del = pyqtSignal()


def setup_listwidget_context_menu(list_widget):
    """为QListWidget添加带信号的右键菜单"""
    # 创建信号发射器
    pyqtSignals = ListWidgetMenupyqtSignals()

    # 配置上下文菜单策略
    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    # 创建菜单动作
    song_play = QAction('播放', list_widget)
    song_update = QAction('刷新列表', list_widget)
    song_import = QAction('导入歌曲', list_widget)
    song_export = QAction('导出', list_widget)
    song_path = QAction('打开路径', list_widget)
    song_rename = QAction('重命名', list_widget)
    song_del = QAction('删除', list_widget)

    # 连接动作到信号
    song_play.triggered.connect(pyqtSignals.song_play.emit)
    song_update.triggered.connect(pyqtSignals.song_update.emit)
    song_import.triggered.connect(pyqtSignals.song_import.emit)
    song_export.triggered.connect(pyqtSignals.song_export.emit)
    song_path.triggered.connect(pyqtSignals.song_path.emit)
    song_rename.triggered.connect(pyqtSignals.song_rename.emit)
    song_del.triggered.connect(pyqtSignals.song_del.emit)

    def show_context_menu(pos):
        """生成带圆角的上下文菜单"""
        menu = QMenu(list_widget)
        # 关键设置：启用透明背景和无边框
        menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setWindowFlag(Qt.NoDropShadowWindowHint)  # 禁用阴影

        menu.addActions([song_play, song_update, song_import,
                         song_export, song_path,song_rename, song_del])
        menu.exec_(list_widget.mapToGlobal(pos))

    # 连接菜单触发信号
    list_widget.customContextMenuRequested.connect(show_context_menu)

    return pyqtSignals  # 返回包含信号的QObject

def setup_listwidget_context_menu_playlist(list_widget):
    """为QListWidget添加带信号的右键菜单"""
    # 创建信号发射器
    pyqtSignals = ListWidgetMenupyqtSignals()

    # 配置上下文菜单策略
    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    # 创建菜单动作
    playlist_skip = QAction('跳转', list_widget)
    playlist_update = QAction('刷新列表', list_widget)
    playlist_import = QAction('导入歌单', list_widget)
    playlist_export = QAction('导出', list_widget)
    playlist_path = QAction('打开路径', list_widget)
    playlist_new = QAction('新建', list_widget)
    playlist_rename = QAction('重命名', list_widget)
    playlist_del = QAction('删除', list_widget)

    # 连接动作到信号
    playlist_skip.triggered.connect(pyqtSignals.playlist_skip.emit)
    playlist_update.triggered.connect(pyqtSignals.playlist_update.emit)
    playlist_import.triggered.connect(pyqtSignals.playlist_import.emit)
    playlist_export.triggered.connect(pyqtSignals.playlist_export.emit)
    playlist_path.triggered.connect(pyqtSignals.playlist_path.emit)
    playlist_new.triggered.connect(pyqtSignals.playlist_new.emit)
    playlist_rename.triggered.connect(pyqtSignals.playlist_rename.emit)
    playlist_del.triggered.connect(pyqtSignals.playlist_del.emit)

    def show_context_menu(pos):
        """生成带圆角的上下文菜单"""
        menu = QMenu(list_widget)
        # 关键设置：启用透明背景和无边框
        menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setWindowFlag(Qt.NoDropShadowWindowHint)  # 禁用阴影

        menu.addActions([playlist_skip, playlist_update, playlist_import,
                         playlist_export,playlist_path,playlist_new,playlist_rename, playlist_del])
        menu.exec_(list_widget.mapToGlobal(pos))

    # 连接菜单触发信号
    list_widget.customContextMenuRequested.connect(show_context_menu)

    return pyqtSignals  # 返回包含信号的QObject
