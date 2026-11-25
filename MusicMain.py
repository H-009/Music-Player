import shutil

from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QFileDialog, QListWidget, QListView,QWidget
from PyQt5.QtGui import QPixmap, QIcon, QPixmapCache
from PyQt5.QtCore import Qt, QThread, QByteArray
from BlurWindow.blurWindow import GlobalBlur

import traceback, random, ctypes, sys, os, darkdetect, base64, json

from MusicPlayer import MusicInspector, MusicThread, QtAnimation, MusicMessageBox
from MusicPlayer import MusicAcrylic, MusicVerifyer, MusicLicenseDecode, MusicAdapt, DataBase

from MusicPlayer import (MusicLyricWidget, HookSelector, Switch,
                         ThemeSelector,HotkeySelector,MusicReader,Mask,Timer,Drawer,
                         MusicWidgetService, MusicService,MusicFolderService, MusicFileService,
                         MusicTip, MusicMenu, MusicLyric,MusicCover, MusicImport, MusicHotKey,
                         MusicStatistics, MusicExplorer, MusicPlay,Widgets,DesktopLyricWidget)

import MusicUI

class MainUI(MusicUI.Ui_MusicPlayer):
    def __init__(self):
        self.theme_worker, self.font_worker, self.song_worker = None, None, None
        self.select_lic_file,  self.thread_play,self.select_lic = None,None,None
        self.timer_thread, self.lyric_widget,self.cover_button = None, None, None
        self.license_thread_AuthorizationInformation,self.lyric_worker = None,None
        self.play_song_count, self.music_timer,self.play_song_time = None, None,None
        self.music_playlist_filenames, self.music_playlist_num_directories = None, None
        self.cover_worker, self.info_worker,self.song_thumbnail_worker = None, None,None
        self.license_thread_Copyright, self.license_thread_DigitalSignature, = None, None
        self.switch_lyric_translation, self.select_playlist,self.switch_lyric = None,None,None
        self.music_duration, self.music_duration_s, self.music_duration_min = None, None, None
        self.import_song_path,self.import_folder_name,self.import_playlist_path = None,None,None
        self.hook_play_thread, self.hook_time_up_thread, self.hook_music_up_thread = None,None,None
        self.music_cover_image,self.switch_slider_animation, self.music_image_png = None, None,None
        self.license_thread_uuid, self.license_thread_uid, self.license_thread_id = None, None, None
        self.switch_combobox_animation,self.select_playlist_list,self.switch_list_item = None,None,None
        self.switch_stacked_widget,self.theme_background, self.switch_button_animation = None,None,None
        self.switch_listitem_ico, self.switch_elastic_rolling, self.switch_widgets_tip = None,None,None
        self.license_thread_path, self.license_thread_name, self.license_thread_name = None, None, None
        self.music_menu_signals_song,self.lyric_line, self.music_menu_signals_playlist = None, None,None
        self.scanner_thread_theme, self.scanner_thread_lyric, self.scanner_thread_font = None, None, None
        self.scanner_thread_thumbnail,self.switch_list_elastic_rolling,self.sum_mp3_file = None,None,None
        self.scanner_thread_file, self.scanner_thread_folder, self.scanner_thread_cover = None, None, None
        self.license_thread_version, self.hook_music_down_thread,self.license_thread_type = None, None,None
        self.license_thread_begin, self.license_thread_end, self.license_thread_activation = None, None, None
        self.music_play_mode, self.play_list, self.select_theme,self.play_list_element = None, None, None,None
        self.music_song_filenames,self.hook_time_down_thread, self.music_song_num_directories = None, None,None
        self.license_thread_features, self.license_thread_time_type, self.license_thread_key = None, None, None
        self.select_song_list, self.select_music_name,self.lyrics_data, self.music_select = None, None, None,None

        # 初始化加速
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)  # 桌面级OpenGL加速
        QApplication.setAttribute(Qt.AA_UseOpenGLES)  # 使用OpenGL ES渲染
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)  # 强制使用软件渲染
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # 共享OpenGL上下文

        self.app = QApplication(sys.argv)
        self.Main = QMainWindow()

        self.music_service = MusicService
        self.music = MusicUI.Ui_MusicPlayer()
        self.music_import = MusicImport.Service()
        self.song_thread, self.cover_thread = QThread(), QThread()
        self.music_cover_service,self.music_inspector = MusicCover.Service(),MusicInspector.Inspector()
        self.theme_thread, self.lyric_thread, self.font_thread, self.song_thumbnail_thread = QThread(), QThread(), QThread(), QThread()

        self.music_explorer = MusicExplorer
        self.music_file_service = MusicFileService
        self.music_folder_service = MusicFolderService
        self.music_mask, self.music_tip = Mask, MusicTip
        self.Box, self.database = MusicMessageBox.Box, DataBase
        self.music_player, self.music_menu = MusicPlay, MusicMenu
        self.reader, self.music_acrylic = MusicReader, MusicAcrylic
        self.music_thread, self.music_adapt = MusicThread, MusicAdapt
        self.hotkey_selector, self.music_hotkey = HotkeySelector, MusicHotKey
        self.music_widget_service,self.music_lyric = MusicWidgetService,MusicLyric
        self.music_verifyer, self.music_statistics = MusicVerifyer, MusicStatistics
        self.music_license, self.music_lyric_widget = MusicLicenseDecode, MusicLyricWidget

        # 提前初始化UI
        self.music.setupUi(self.Main)

        # 使用共享缓存加载（需在程序初始化时设置）
        QPixmapCache.setCacheLimit(100 * 1024)  # 100MB缓存空间

        # 智能适配字体大小
        self.music_adapt.set_dual_font(self.music.MusicPlayer_Bottom_Widget,
                                       [self.music.music_name_Label, self.music.music_lyric_Label,self.music.inherit_Label,
                                        self.music.music_time_1_Label,self.music.music_time_2_Label])

        self.path_suffix = ".amc"
        self.pathfile_local = "Config/Local.cmt"
        self.config_playlist = self.music_file_service.json_read(self.pathfile_local, "playlist path")
        self.cache_playlist = self.music_file_service.json_read(self.pathfile_local, "cache path")

        self.pathfile_resources = "Config/Resources.xns"
        self.path_database = "Config/DataBase/Collect.DBI"
        self.path_cover, self.path_theme_folder, self.path_animation_folder = self.cache_playlist + 'Cover/', "Theme/", 'Config/Animation/'
        self.path_font, self.path_experimental, self.path_hotkey_folder, self.path_hook_folder = "Font/", "Config/Experimental/", "Config/HotKey/", "Config/Hook/"
        self.path_playlist_folder, self.path_config_folder, self.path_switch_folder = self.config_playlist, "Config/Local/", "Config/Switch/"
        self.path_statistics, self.path_lyric, self.path_thumbnail = "Config/Statistics/", self.cache_playlist + "Lyric/", self.cache_playlist + "Thumbnail/"
        self.sys_path_font, self.sys_path_theme, self.sys_path_lyric = "Font\\", "Theme\\", self.cache_playlist + "Lyric\\"
        self.sys_path_playlist, self.sys_path_cover, self.sys_path_thumbnail = self.config_playlist, self.cache_playlist + "Cover\\", self.cache_playlist + "Thumbnail\\"

        self.resources_ico = self.music_file_service.json_all_read(self.pathfile_resources)

        self.app_ico, self.app_id, self.app_title = "MusicIco.ico", "Music Player 24 Pro", "音乐播放器 24 Pro"

        # 初始化毫秒计时器
        self.timer = "0:00.000"

        # 桌面路径
        self.path_desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
        # 读取选择播放列表的配置文件
        self.path_playlist = self.music_file_service.amc_read(
            self.path_config_folder + "select playlist" + self.path_suffix)
        # 读取选择音乐文件的配置文件
        self.path_music = self.music_file_service.amc_read(self.path_config_folder + "select music" + self.path_suffix)
        # 读取播放模式的配置文件
        self.path_play_mode = self.music_file_service.amc_read(self.path_config_folder + "play mode" + self.path_suffix)
        # 读取播放列表的配置文件
        self.path_play_playlist = self.music_file_service.amc_read(
            self.path_config_folder + "play playlist" + self.path_suffix)
        # 构建播放列表
        self.play_list = self.music_folder_service.get_all_files(self.path_playlist_folder + self.path_play_playlist)
        # 读取选择的许可证
        self.license_file = self.music_file_service.amc_read(self.path_config_folder + "license currently use.amc")
        # 读取选择的音量
        self.select_volume = self.music_file_service.amc_read(self.path_config_folder + "select volume.amc")
        # 读取选择的字体
        self.select_font = self.music_file_service.amc_read(self.path_config_folder + "select font" + self.path_suffix)
        # 读取选择的主题
        self.select_theme = self.music_file_service.amc_read(self.path_config_folder + 'select theme.amc')

        # 读取选择的热键
        self.hotkey_play = self.music_file_service.amc_read(self.path_hotkey_folder + "play.amc")
        self.hotkey_playlist = self.music_file_service.amc_read(self.path_hotkey_folder + "playlist.amc")
        self.hotkey_time_up = self.music_file_service.amc_read(self.path_hotkey_folder + "time up.amc")
        self.hotkey_time_down = self.music_file_service.amc_read(self.path_hotkey_folder + "time down.amc")
        self.hotkey_music_up = self.music_file_service.amc_read(self.path_hotkey_folder + "music up.amc")
        self.hotkey_music_down = self.music_file_service.amc_read(self.path_hotkey_folder + "music down.amc")
        self.hotkey_music_like = self.music_file_service.amc_read(self.path_hotkey_folder + "music like.amc")

        # 读取选择的钩子
        self.hook_play = self.music_file_service.amc_read(self.path_hook_folder + "play.amc")
        self.hook_time_up = self.music_file_service.amc_read(self.path_hook_folder + "time up.amc")
        self.hook_time_down = self.music_file_service.amc_read(self.path_hook_folder + "time down.amc")
        self.hook_music_up = self.music_file_service.amc_read(self.path_hook_folder + "music up.amc")
        self.hook_music_down = self.music_file_service.amc_read(self.path_hook_folder + "music down.amc")

        # 读取淡入淡出时长
        self.fade_in_time = self.music_file_service.amc_read(self.path_config_folder + "fade in.amc")
        self.fade_out_time = self.music_file_service.amc_read(self.path_config_folder + "fade out.amc")

        # 项目图片开关
        self.switch_item_ico = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))
        # 控件提示开关
        self.switch_widget_tip = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "widget tip.amc"))

        # 控件动画
        self.animation_button = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "button animation.amc"))
        self.animation_tacked_widget = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "stacked widget.amc"))
        self.animation_slider_animation = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "slider animation.amc"))
        self.animation_elastic_rolling = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "elastic rolling.amc"))
        self.animation_list_elastic_rolling = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "list elastic rolling.amc"))
        self.animation_list_item = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "list item.amc"))
        self.animation_combobox_animation = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "combobox animation.amc"))

        # 主题属性
        self.theme_color = self.music_file_service.json_read(self.path_theme_folder + self.music_file_service.amc_read(
            self.path_config_folder + "select theme.amc") + ".tsp", "color")

        # 播放状态 播放 暂停
        self.music_play_state = True
        # 写入锁
        self.write_lock = False
        # 图标锁
        self.thumbnail_key = True
        # 终止锁
        self.stop_thumbnail_key = True
        # 喜欢状态
        self.like_state = False

        # 配置音频播放线程和淡入淡出时长
        self.music_player = self.music_player.MusicMonitor(float(self.fade_in_time), float(self.fade_out_time))

        self.music_center_buttons = [
            self.music.info_Button,self.music.set_Button, self.music.song_Button, self.music.collect_Button]
        self.button_animators = []
        self.combobox_animators = []
        self.list_animators = []
        self.excluded_widgets = [self.music.play_Button, self.music.up_time_Button, self.music.down_time_Button,
                                 self.music.up_Button, self.music.down_Button,self.music.state_Button,self.music.volume_Button,
                                 self.music.clock_Button,self.music.like_Button,self.music.interrupt_Button]
        # 完成所有控件初始化后

        # 初始化音量抽屉
        self.volume_drawer = Drawer.DrawerHost(self.music.MusicPlayer_Bottom_Widget, self.music.drawer_widget)

        # 初始化图像按钮
        self.init_cover_button()

        # 初始化歌词模块
        self.init_lyric_model()

        # 初始化实验性内容
        self.init_experimental()

        # 建立缓存
        self.ico_cache = self.music_thread.IconCache()

        super().__init__()

    # 更新画布
    def Music_Update(self, model):
        if model == "Music_Song":
            self.music_widget_service.toggle_buttons(self.music_center_buttons, self.music.song_Button)
            self.music.Center_StackedWidget.setCurrentIndex(2)
            self.music_update_song()
            self.music_update_playlist()

        elif model == "Music_Collect":
            self.music_widget_service.toggle_buttons(self.music_center_buttons, self.music.collect_Button)
            self.music.Center_StackedWidget.setCurrentIndex(3)
            self.music_update_collect()

        elif model == "Center_Info":
            self.music_widget_service.toggle_buttons(self.music_center_buttons, self.music.info_Button)
            self.music.Center_StackedWidget.setCurrentIndex(0)
            self.music_update_details()
        elif model == "Center_Set":
            self.music_widget_service.toggle_buttons(self.music_center_buttons, self.music.set_Button)
            self.music.Center_StackedWidget.setCurrentIndex(4)
            self.music_update_set()

    # 更新歌曲进度条
    def music_progress_update(self):
        # 读取选择的歌曲
        path_music = self.music_file_service.amc_read(self.path_config_folder + 'select music.amc')

        # 归零歌曲进度条当前值
        self.music.music_Progressbar.setValue(0)

        # 获取歌曲时长 分钟
        self.music_duration_min = self.music_service.get_duration_ffmpeg_fast(
            self.path_playlist_folder + self.path_playlist + '/' +
            path_music + ".mp3")

        # 格式化秒
        self.music_duration_s = self.music_service.get_duration_ffmpeg_fast2(
            self.path_playlist_folder + self.path_playlist + '/' + path_music + ".mp3")
        # 设置进度条最大值
        self.music.music_Progressbar.setMaximum(self.music_duration_s)

        self.music.music_time_1_Label.setText('0:00')
        self.music.music_time_2_Label.setText(self.music_duration_min)

    # 更新封面缩略图
    def update_thumbnail(self, name=None):
        if name is None:
            path = self.path_playlist
        else:
            path = name
        music_name = self.music_file_service.amc_read(self.path_config_folder + 'select music' + self.path_suffix)


        # 不存在则提取
        self.music_cover_image = self.music_cover_service.get_mp3_cover_ico_webp(
            self.path_playlist_folder + path + '/' + music_name + '.mp3',self.path_thumbnail + path + '/', music_name)

        # 未提取到封面
        if self.music_cover_image is None:
            self.music_cover_service.new_mp3_cover_ico(music_name, self.path_thumbnail + path + '/')

    # 更新详情所有封面
    def update_details_cover(self):
        music_name = self.music_file_service.amc_read(self.path_config_folder + 'select music.amc')

        # 选取的封面不存在
        if not os.path.exists(self.path_cover + self.path_playlist + "/" + music_name + '.png'):
            if not os.path.exists(self.path_cover + self.path_playlist):
                # 创建文件夹
                self.music_folder_service.create_directory(self.path_cover + self.path_playlist)

            # 不存在则提取
            self.music_cover_image = self.music_cover_service.get_mp3_cover(
                self.path_playlist_folder + self.path_playlist + '/' + music_name + '.mp3',
                self.path_cover + self.path_playlist + '/', music_name)

            self.music_image_png = QPixmap(self.path_cover + self.path_playlist + "/" + music_name + '.png')
            self.music.details_cover_Label.setPixmap(self.music_image_png)
            self.music.details_cover_Label.setScaledContents(True)
            self.cover_button.set_image(self.music_image_png)

            # 未提取到封面
            if self.music_cover_image is None:
                self.music_cover_service.new_mp3_cover(music_name, self.path_cover + self.path_playlist + '/')
                self.music_image_png = QPixmap(self.path_cover + self.path_playlist + "/" + music_name + '.png')
                self.music.details_cover_Label.setPixmap(self.music_image_png)
                self.music.details_cover_Label.setScaledContents(True)
                self.cover_button.set_image(self.music_image_png)
        # 存在则使用
        else:
            self.music_image_png = QPixmap(self.path_cover + self.path_playlist + "/" + music_name + '.png')
            self.music.details_cover_Label.setPixmap(self.music_image_png)
            self.music.details_cover_Label.setScaledContents(True)
            self.cover_button.set_image(self.music_image_png)

    # 更新歌曲播放时长 拖动
    def music_update_time(self):
        try:
            # 停止进度条更新
            self.thread_play.pause()

            # 使用新方法代替滑动条值
            self.music_duration = self.music_service.format_minutes(self.music.music_Progressbar.value())

            # 设置歌曲时长
            self.music.music_time_1_Label.setText(self.music_duration)
            self.music.music_time_2_Label.setText(self.music_duration_min)

        except Exception as a:
            print(a)

    # 滑动条快进
    def music_up_time(self):
        try:
            # 获取当前进度值并增加5秒
            current_value = self.music.music_Progressbar.value()
            new_value = min(current_value + 5, self.music.music_Progressbar.maximum())  # 限制不超过最大值
            self.music.music_Progressbar.setValue(new_value)

            # 格式化显示时间
            current_time = self.music_service.format_minutes(new_value)
            self.music.music_time_1_Label.setText(current_time)
            self.music.music_time_2_Label.setText(self.music_duration_min)

            if self.thread_play:  # 如果正在更新进度条
                self.thread_play.pause()  # 暂停

            # 仅在播放时实现
            if not self.music_play_state:
                # 设置要播放的音乐文件路径 线程
                self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                           self.play_list[self.play_list_element])

                # 实现拖动进度条播放音乐
                self.music_player.set_play(self.music.music_Progressbar.value() - 1)

                # 设置歌曲时长
                self.music.music_time_1_Label.setText(self.music_duration)

                # 更新可视化播放器
                self.update_player()

            self.music.music_time_1_Label.setText(current_time)
            self.music.music_time_2_Label.setText(self.music_duration_min)

        except Exception as e:
            print(f"快进操作异常: {e}")

    # 滑动条快退
    def music_down_time(self):
        try:
            # 获取当前进度值
            current_value = self.music.music_Progressbar.value()
            # 防止越界
            if not current_value - 5 < 0:
                # 增加5秒
                new_value = min(current_value - 5, self.music.music_Progressbar.maximum())  # 限制不超过最大值
                self.music.music_Progressbar.setValue(new_value)

                # 格式化显示时间
                current_time = self.music_service.format_minutes(new_value)
                self.music.music_time_1_Label.setText(current_time)
                self.music.music_time_2_Label.setText(self.music_duration_min)

                # 仅在播放时实现
                if not self.music_play_state:
                    # 设置要播放的音乐文件路径 线程
                    self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                               self.play_list[self.play_list_element])

                    # 实现拖动进度条播放音乐
                    self.music_player.set_play(self.music.music_Progressbar.value() - 1)

                    if self.thread_play:  # 如果正在更新进度条
                        self.thread_play.pause()  # 暂停

                    # 更新可视化播放器
                    self.update_player()
            else:
                # 设为0
                new_value = min(0, self.music.music_Progressbar.maximum())  # 限制不超过最大值
                self.music.music_Progressbar.setValue(new_value)

                # 格式化显示时间
                current_time = self.music_service.format_minutes(new_value)
                self.music.music_time_1_Label.setText(current_time)
                self.music.music_time_2_Label.setText(self.music_duration_min)

                # 仅在播放时实现
                if not self.music_play_state:
                    # 设置要播放的音乐文件路径 线程
                    self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                               self.play_list[self.play_list_element])

                    # self.music_play_state = False
                    self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))

                    # 实现拖动进度条播放音乐
                    self.music_player.set_play(self.music.music_Progressbar.value() - 1)

                    if self.thread_play:  # 如果正在更新进度条
                        self.thread_play.pause()  # 暂停

                    # 更新可视化播放器
                    self.update_player()

        except Exception as e:
            print(f"快退操作异常: {e}")

    # 更新歌曲播放时长 释放
    def music_update_time_play(self):
        try:
            # 停止进度条更新
            self.thread_play.pause()

            # 仅在播放时实现
            if not self.music_play_state:
                # 设置要播放的音乐文件路径 线程
                self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                           self.play_list[self.play_list_element])

                self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))

                # 实现拖动进度条播放音乐
                self.music_player.set_play(self.music.music_Progressbar.value() - 1)

                if self.thread_play:  # 如果正在更新进度条
                    self.thread_play.pause()  # 暂停

                # 更新可视化播放器
                self.update_player()

        except Exception as a:
            print(a)

    # 更新歌曲列表
    def music_update_song(self):
        # 终止锁
        self.stop_thumbnail_key = True

        # 清空列表项目
        self.music.music_song_ListWidget.clear()

        # 刷新项图标开关
        self.switch_item_ico = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))

        # 获取文件夹中所有文件和文件夹的名称
        self.music_song_filenames = os.listdir(self.path_playlist_folder + self.path_playlist)

        # 获取文件夹内文件数量
        self.music_song_num_directories = self.music_folder_service.file_len(
            self.path_playlist_folder + self.path_playlist)

        items = 0  # 文件计数器 添加图标
        if self.thumbnail_key:

            for filename in self.music_song_filenames:
                self.thumbnail_key = False
                self.music.music_song_ListWidget.addItem(self.music_service.remove_mp3_extension(filename))

                # 终止锁
                if not self.stop_thumbnail_key:
                    break  # 跳出扫描

                # 开启项目图标 带动态循环的遍历
                if self.switch_item_ico:
                    # 加速拼接路径
                    path_thumbnail_path = os.path.join(self.path_thumbnail, self.path_playlist,
                                                       os.path.splitext(filename)[0] + ".webp")
                    # 缓存存在
                    if os.path.exists(path_thumbnail_path):
                        # 使用缓存中的数据
                        icon = self.ico_cache.get_icon(path_thumbnail_path)
                        self.music.music_song_ListWidget.item(items).setIcon(icon)
                    # 缓存不存在则使用文件图标
                    else:
                        self.music.music_song_ListWidget.item(items).setIcon(
                            self.image_icon(self.resources_ico, "music file"))

                items += 1

        self.thumbnail_key = True
        # 重新高亮 索引初始化后
        if self.play_list_element is not None:
            self.highlight_current_item(self.play_list[self.play_list_element].replace('.mp3', ''))
        else:
            self.highlight_current_item()

    # 更新歌单列表
    def music_update_playlist(self):
        self.stop_thumbnail_key = False

        self.music.music_playlist_ListWidget.clear()

        # 获取文件夹中所有文件和文件夹的名称
        self.music_playlist_filenames = os.listdir(self.path_playlist_folder)

        # 获取文件夹内文件数量
        self.music_playlist_num_directories = self.music_folder_service.count_directories(self.path_playlist_folder)

        items = 0  # 索引计数器
        for filename in self.music_playlist_filenames:
            self.music.music_playlist_ListWidget.addItem(filename)
            # 开始项图标
            if self.switch_item_ico:
                self.music.music_playlist_ListWidget.item(items).setIcon(
                    self.image_icon(self.resources_ico, "music folder"))

            items += 1

        self.highlight_current_item_str(os.path.splitext(os.path.basename(self.path_playlist))[0],
                                              self.music.music_playlist_ListWidget)

    # 选择歌单列表
    def select_playlist_folder(self):
        try:
            # 获取列表全部项目
            self.select_playlist_list = self.music.music_playlist_ListWidget.currentItem()
            # 获取选择的项目
            self.select_playlist = self.select_playlist_list.text()
            # 替换播放列表
            self.path_playlist = self.select_playlist
            # 解锁写入锁
            self.write_lock = True

            # 更新
            self.Music_Update("Music_Song")

        except Exception as a:
            print(a)

    # 播放选择的文件
    def list_play_music_file(self):
        try:
            # 获取列表全部项目
            self.select_song_list = self.music.music_song_ListWidget.currentItem()
            # 获取选择的项目
            self.select_music_name = self.select_song_list.text()
            self.music_select = self.select_music_name + '.mp3'

            self.path_play_playlist = self.music_file_service.amc_read(
                self.path_config_folder + "play playlist" + self.path_suffix)
            # 应用更新
            self.path_play_playlist = self.path_playlist
            self.play_list = self.music_folder_service.get_all_files(
                self.path_playlist_folder + self.path_play_playlist)

            # 更新播放次数
            self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

            # 设置要播放的音乐文件路径 线程
            self.music_player.set_load(self.path_playlist_folder + self.path_playlist + '/' + self.music_select)

            # 写入锁 选择歌单后解锁
            if self.write_lock:
                # 写入选择的歌单
                self.music_file_service.amc_write(self.path_config_folder + 'select playlist' + self.path_suffix,
                                                  self.select_playlist)

            # 写入选择的文件
            self.music_file_service.amc_write(self.path_config_folder + 'select music' + self.path_suffix,
                                              self.select_music_name)

            # 更新歌曲进度条
            self.music_progress_update()

            # 更新播放列表
            self.update_play_list()
            # 归零选择的元素索引
            self.play_list_element = self.music.music_song_ListWidget.currentRow()

            # 停止进度条更新 线程存在
            if self.thread_play:
                self.thread_play.stop()

            # 设置要播放的音乐文件路径 线程
            self.music_player.set_load(self.path_playlist_folder + self.path_playlist + '/' +
                                       self.play_list[self.play_list_element])  # 分离播放

            # 播放音乐
            # 在歌曲进度条的值的地方播放
            self.music_player.set_play(self.music.music_Progressbar.value() - 1)

            # 更新可视化播放器
            self.update_player()

            self.music_player.resume()
            self.music_player.start()  # 启动监测线程

            self.music_play_state = False
            self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))

            # 设置选择的音乐名称
            self.music.music_name_Label.setText(self.select_music_name)
            # 更新歌词
            self.update_lyric()
            # 更新歌曲项图标
            self.update_song_item_ico()

            # 更新喜欢
            self.update_like_check()

        except Exception as a:
            print(a)

    # 播放按钮
    def play_music_file(self):
        try:
            # 播放
            if self.music_play_state:
                # 更新播放次数
                self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)
                # 播放音乐
                # 在歌曲进度条的值的地方播放 修正误差
                self.music_player.set_play(self.music.music_Progressbar.value() - 1)

                # 更新可视化播放器
                self.update_player()

                self.music_player.resume()  # 启动并淡入
                self.music_player.start()  # 启动监测线程

                self.music_play_state = False
                self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))
                self.highlight_current_item()

            # 暂停
            else:
                self.thread_play.pause()
                self.music_player.pause()  # 停止监测线程
                # 结束播放
                self.music_play_state = True
                self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "play"))

        except Exception as a:
            # 获取错误追踪信息
            tb = traceback.extract_tb(sys.exc_info()[2])
            # 获取错误发生的行号
            line_number = tb[-1].lineno
            print("播放按钮 函数中发生错误", a, '所在', line_number)

    # 上一首按钮
    def up_music_file(self):
        try:
            self.path_play_playlist = self.music_file_service.amc_read(
                self.path_config_folder + "play playlist" + self.path_suffix)
            # 应用更新
            self.path_play_playlist = self.path_playlist
            self.play_list = self.music_folder_service.get_all_files(
                self.path_playlist_folder + self.path_play_playlist)

            # 更新播放次数
            self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

            if self.thread_play:
                # 停止进度条更新
                self.thread_play.stop()

            if self.timer_thread:
                self.timer_thread.pause()

            # 上一索引
            self.play_list_element -= 1
            if self.play_list_element == -1:
                self.play_list_element = len(self.play_list) - 1

            # 去掉元素的后缀
            file = self.music_service.remove_mp3_extension(self.play_list[self.play_list_element])

            # 设置选择的音乐名称
            self.music.music_name_Label.setText(file)
            # 写入选择的文件
            self.music_file_service.amc_write(self.path_config_folder + 'select music' + self.path_suffix, file)

            # 更新缩略图
            self.update_thumbnail()

            # 设置要播放的音乐文件路径 线程
            self.music_player.set_load(
                self.path_playlist_folder + self.path_play_playlist + "/" + self.play_list[self.play_list_element])

            # 模拟播放按钮播放
            self.music_play_state = True
            # 更新并归零进度条
            self.music_progress_update()
            self.play_music_file()

            # 更新歌词
            self.update_lyric()

            # 更新喜欢
            self.update_like_check()

            # 更新歌曲项图标
            self.update_song_item_ico()

        except Exception as a:
            # 获取错误追踪信息
            tb = traceback.extract_tb(sys.exc_info()[2])
            # 获取错误发生的行号
            line_number = tb[-1].lineno
            print("上一首按钮函数 发生错误", a, "所在", line_number)

    # 下一首
    def down_music_file(self):
        try:
            # 应用更新
            self.path_play_playlist = self.path_playlist
            self.play_list = self.music_folder_service.get_all_files(self.path_playlist_folder + self.path_playlist)

            # 随机播放 下一首索引随机
            if self.music_play_mode == 1:
                # 更新播放次数
                self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

                if self.thread_play:
                    # 停止进度条更新
                    self.thread_play.stop()

                self.play_list_element += random.randint(1, self.music_song_num_directories)  # 1-列表最大

                if self.play_list_element >= len(self.play_list):
                    # 计算第二次循环的索引
                    self.play_list_element = self.play_list_element % len(self.play_list)

                # 去掉元素的后缀
                file = self.music_service.remove_mp3_extension(self.play_list[self.play_list_element])

                # 设置选择的音乐名称
                self.music.music_name_Label.setText(file)

                # 写入选择的文件
                self.music_file_service.amc_write(self.path_config_folder + 'select music' + self.path_suffix, file)

                # 设置要播放的音乐文件路径 线程
                self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                           self.play_list[self.play_list_element])  # 分离播放

                # 模拟播放按钮播放
                self.music_play_state = True
                # 更新并归零进度条
                self.music_progress_update()
                self.play_music_file()

            # 循环播放 无限循环
            elif self.music_play_mode == 2:
                # 更新播放次数
                self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

                if self.thread_play:
                    # 停止进度条更新
                    self.thread_play.stop()

                self.play_list_element += 1
                if self.play_list_element == len(self.play_list):
                    self.play_list_element = 0

                file = self.music_service.remove_mp3_extension(self.play_list[self.play_list_element])

                # 设置选择的音乐名称
                self.music.music_name_Label.setText(file)

                # 写入选择的文件
                self.music_file_service.amc_write(self.path_config_folder + 'select music' + self.path_suffix, file)

                self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                           self.play_list[self.play_list_element])  # 分离播放

                # 模拟播放按钮播放
                self.music_play_state = True
                # 更新并归零进度条
                self.music_progress_update()
                self.play_music_file()

            # 单曲循环 无限循环一首
            elif self.music_play_mode == 3:
                # 更新播放次数
                self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

                if self.thread_play:
                    # 停止进度条更新
                    self.thread_play.stop()

                # 设置要播放的音乐文件路径 线程
                self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' +
                                           self.play_list[self.play_list_element])  # 分离播放

                # 模拟播放按钮播放
                self.music_play_state = True
                # 更新并归零进度条
                self.music_progress_update()
                self.play_music_file()

            if self.timer_thread:
                self.timer_thread.pause()

            self.update_lyric()
            # 更新喜欢
            self.update_like_check()

            # 更新歌曲项图标
            self.update_song_item_ico()

        except Exception as a:
            print(a)

    # 高亮指定的列表项
    @staticmethod
    def highlight_current_item_str(current_item_text, ListWidget):
        """高亮指定的列表项"""
        list_widget = ListWidget

        # 查找并高亮匹配项
        items = list_widget.findItems(current_item_text, Qt.MatchExactly)
        if items:
            item = items[0]
            list_widget.setCurrentItem(item)
            list_widget.scrollToItem(item)

    # 高亮多个指定项
    @staticmethod
    def highlight_current_items_str(text_list, list_widget):
        """
        高亮（选中）列表中所有文本完全匹配（文件名不含扩展名）的项，
        支持传入文件路径列表（如 ["C:/xxx/半壶纱DJ.mp3"]），自动提取文件名并高亮。

        步骤：
        1. 先取消所有选中项
        2. 设置 list_widget 为多选模式
        3. 禁用交互（防止用户点击干扰）
        4. 遍历传入的路径列表，提取纯文件名，然后查找并设置为选中状态
        5. 滚动到每个匹配项
        6. 操作完成后，恢复为原始选择模式，并重新启用交互

        :param text_list: List[str]，例如 ["C:/Music/半壶纱DJ.mp3", "D:/Music/半壶纱DJ 0.8x.mp3"]
        :param list_widget: QListWidget，目标控件，里面的 item 是纯文件名，比如 "半壶纱DJ"
        """

        # === Step 1: 取消所有已选中的 item ===
        list_widget.clearSelection()

        # === Step 2: 设置为多选模式（必须多选才能选中多个）===
        original_selection_mode = list_widget.selectionMode()
        list_widget.setSelectionMode(QListWidget.MultiSelection)

        # === Step 3: 禁用用户交互（防止点击列表导致选中状态被修改）===
        list_widget.setDisabled(True)

        try:
            # === Step 4: 遍历传入的路径列表，提取纯文件名，然后查找并选中匹配项 ===
            file_names_to_highlight = []  # 用于存放提取后的纯文件名（不含扩展名）

            for file_path in text_list:
                # 提取文件名（含扩展名），例如 "半壶纱DJ.mp3"
                file_name_with_ext = os.path.basename(file_path)
                # 去掉扩展名，得到纯文件名，例如 "半壶纱DJ"
                file_name = os.path.splitext(file_name_with_ext)[0]
                file_names_to_highlight.append(file_name)

            # 遍历提取出的纯文件名，并查找匹配的 item
            for file_name in file_names_to_highlight:
                matched_items = list_widget.findItems(file_name, Qt.MatchExactly)
                for item in matched_items:
                    item.setSelected(True)
                    list_widget.scrollToItem(item)

        finally:
            # === Step 5: 恢复交互 & 恢复选择模式 ===
            list_widget.setDisabled(False)
            list_widget.setSelectionMode(original_selection_mode)

    # 高亮当前播放的列表项
    def highlight_current_item(self, path=None):
        """高亮当前播放的列表项"""
        list_widget = self.music.music_song_ListWidget
        if path is None:
            current_item_text = self.music_file_service.amc_read(
                self.path_config_folder + 'select music' + self.path_suffix)
        else:
            current_item_text = path

        # 清除之前的高亮
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setBackground(Qt.white)
            item.setForeground(Qt.black)

        # 查找并高亮匹配项
        items = list_widget.findItems(current_item_text, Qt.MatchExactly)
        if items:
            item = items[0]
            item.setBackground(Qt.blue)
            item.setForeground(Qt.white)
            list_widget.setCurrentItem(item)
            list_widget.scrollToItem(item)

    # 导入歌单按钮
    def import_playlist(self):
        # 自定义对话框
        try:
            # 提取歌单路径
            self.import_playlist_path = QFileDialog.getExistingDirectory(self.music.MusicPlayer_Bottom_Widget,
                                                                         "提取歌单文件夹",
                                                                         self.path_desktop)

            # 正常文件夹路径
            if not os.path.basename(self.import_playlist_path) == 'Desktop' and not os.path.basename(
                    self.import_playlist_path) == 'C:' and self.import_playlist_path:
                # 从完整路径中提取文件夹名
                self.import_folder_name = os.path.basename(os.path.normpath(self.import_playlist_path))
                # 转移文件夹
                self.music_import.copy_folder(self.import_playlist_path,
                                              self.path_playlist_folder + self.import_folder_name)
                # 更新歌单列表
                self.music_update_playlist()

                # 高亮导入歌单
                self.highlight_current_item_str(os.path.splitext(os.path.basename(self.import_playlist_path))[0],
                                           self.music.music_playlist_ListWidget)

        except Exception as a:
            print(a)

    # 导出歌单按钮
    def export_playlist(self):
        try:
            begin_path = self.music_widget_service.get_current_item_text(self.music.music_playlist_ListWidget)

            # 提取mp3文件
            path = QFileDialog.getExistingDirectory(self.music.MusicPlayer_Bottom_Widget, "选择导出文件夹",
                                                    self.path_desktop)

            if not path == "":
                # 复制文件到指定路径
                self.music_import.copy_folder2(self.path_playlist_folder + begin_path, path)
                QApplication.alert(self.music.MusicPlayer_Bottom_Widget, 0)  # 任务栏闪烁

        except Exception as a:
            print(a)

    # 导入歌曲按钮
    def import_song(self):
        try:
            # 提取mp3文件
            self.import_song_path, sift = QFileDialog.getOpenFileNames(self.music.MusicPlayer_Bottom_Widget,
                                                                       '提取歌曲文件', self.path_desktop
                                                                       , 'MP3 Files (*.mp3)')
            # 筛选mp3文件 多个文件
            if self.import_song_path:
                for i in self.import_song_path:
                    if i.lower().endswith('.mp3'):
                        # 复制文件到指定路径
                        self.music_import.copy_file(i, self.path_playlist_folder + self.path_playlist)
                        # 更新歌曲列表
                        self.music_update_song()
                self.highlight_current_items_str(self.import_song_path, self.music.music_song_ListWidget)

        except Exception as a:
            print(a)

    # 导出歌曲按钮
    def export_song(self):
        try:
            begin_path = self.music_widget_service.get_current_item_text(self.music.music_song_ListWidget)

            # 提取mp3文件
            path = QFileDialog.getExistingDirectory(self.music.MusicPlayer_Bottom_Widget, "选择导出文件夹",
                                                    self.path_desktop)

            if not path == "":
                # 复制文件到指定路径
                self.music_import.copy_file(self.path_playlist_folder + self.path_playlist + "/" + begin_path + ".mp3",
                                            path)
                QApplication.alert(self.music.MusicPlayer_Bottom_Widget, 0)  # 任务栏闪烁

        except Exception as a:
            print(a)

    # 拖入歌曲
    def drag_song(self, file):
        try:
            # 筛选mp3文件 多个文件
            if file:
                for i in file:
                    if i.lower().endswith('.mp3'):
                        # 复制文件到指定路径
                        self.music_import.copy_file(i, self.path_playlist_folder + self.path_playlist)
                        # 更新歌曲列表
                self.music_update_song()
            self.highlight_current_items_str(file, self.music.music_song_ListWidget)

        except Exception as a:
            print(a)

    # 拖入歌单
    def drag_playlist(self, playlist):
        try:
            if not playlist:
                return

            # 歌单字典
            playlist_groups = {}
            # 歌单列表
            playlist_list = []

            for root_path in playlist:
                if not os.path.isdir(root_path):
                    continue
                # 遍历根路径下的所有文件
                for current_root, dirs, files in os.walk(root_path):
                    # 筛选当前目录下的mp3
                    mp3_in_current_dir = []
                    for filename in files:
                        if filename.lower().endswith('.mp3'):
                            full_path = os.path.join(current_root, filename)
                            mp3_in_current_dir.append(full_path)
                    # 如果当前目录有 mp3 文件 则将它们归类到父文件夹名称的歌单中
                    if mp3_in_current_dir:
                        # 获取上级文件夹名称作为歌单名
                        playlist_name = os.path.basename(current_root)

                        # 将文件添加到对应的歌单组
                        if playlist_name not in playlist_groups:
                            playlist_groups[playlist_name] = []
                            playlist_list.append(playlist_name)
                        playlist_groups[playlist_name].extend(mp3_in_current_dir)

            for playlist_name, file_list in playlist_groups.items():
                if not file_list:
                    continue

                #构建目标路径并处理重名
                target_dir = os.path.join(self.path_playlist_folder, playlist_name)
                original_name = playlist_name
                counter = 1

                # 重名判断
                while os.path.exists(target_dir):
                    playlist_name = f"{original_name}({counter})"
                    target_dir = os.path.join(self.path_playlist_folder, playlist_name)
                    counter += 1

                # 创建目标文件夹
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # 复制文件
                for src_file in file_list:
                    try:
                        filename = os.path.basename(src_file)
                        dst_file = os.path.join(target_dir, filename)
                        # 执行复制
                        if hasattr(self.music_service, 'copy_file'):
                            self.music_service.copy_file(src_file, target_dir)
                        else:
                            shutil.copy2(src_file, dst_file)
                    except Exception as e:
                        print(f"复制文件失败 {src_file}: {e}")
                # 添加歌单名称到列表
                self.music.music_playlist_ListWidget.addItem(playlist_name)

            # 更新歌单列表
            self.music_update_playlist()
            # 更新高亮
            self.highlight_current_items_str(playlist_list, self.music.music_playlist_ListWidget)

        except Exception as e:
            print(f"拖拽歌单处理出错: {e}")
            import traceback
            traceback.print_exc()

    # 更新可视播放器
    def update_player(self):
        self.thread_play = self.music_thread.SliderUpdater(self.music.music_Progressbar,
                                                           self.music.music_Progressbar.maximum(),
                                                           self.music.music_Progressbar.value(),
                                                           self.music_duration_min)
        self.thread_play.update_slider.connect(self.music.music_Progressbar.setValue)  # 绑定信号到进度条
        self.thread_play.update_label.connect(self.music.music_time_1_Label.setText)
        self.thread_play.update_label2.connect(self.music.music_time_2_Label.setText)
        # 连接时间监控
        self.thread_play.next.connect(self.down_music_file)
        # 绑定高精度计时器
        self.thread_play.update.connect(lambda x: self.update_timer(x))
        self.thread_play.start()

    # 清理封面缓存
    def clear_cover_cache(self):
        box = self.music_folder_service.delete_root_folder(self.path_cover)
        self.music_update_set()
        if box:
            # 创建一个消息框
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "封面缓存已清理")
        elif not box:
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "封面缓存已清理或不存在")

    # 清理歌词缓存
    def clear_lyric_cache(self):
        box = self.music_folder_service.delete_root_folder(self.path_lyric)
        self.music_update_set()
        if box:
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "歌词缓存已清理")
        elif not box:
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "歌词缓存已清理或不存在")

    # 清理缩略图缓存
    def clear_song_thumbnail_cache(self):
        box = self.music_folder_service.delete_root_folder(self.path_thumbnail)
        self.ico_cache.clear_cache()  # 清理图标内存缓存
        self.music_update_set()
        self.music_update_song()  # 刷新歌曲列表
        if box:
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "缩略图缓存已清理")
        elif not box:
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "缩略图已清理或不存在")

    # 清理所有歌曲
    def clear_song_all(self):
        box = self.Box.show_custom_dialog(self.music.MusicPlayer_Bottom_Widget)
        key = self.music_folder_service.count_folder(self.path_playlist_folder)

        if box:
            for i in range(key):
                self.music_folder_service.clean_parent_folder(self.path_playlist_folder, "local")
            # 更新设置画布
            self.music_update_set()

            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "所有歌曲已清理")

    # 清理所有数据
    def clear_data_all(self):
        box1 = self.Box.show_custom_dialog_one(self.music.MusicPlayer_Bottom_Widget)
        if box1:
            box2 = self.Box.show_custom_dialog_two(self.music.MusicPlayer_Bottom_Widget)
            if box2:
                # 清理封面缓存
                self.music_folder_service.delete_root_folder(self.path_cover)
                # 清理歌词缓存
                self.music_folder_service.delete_root_folder(self.path_lyric)
                # 清理所有歌曲
                key = self.music_folder_service.count_folder(self.path_playlist_folder)

                for i in range(key):
                    self.music_folder_service.clean_parent_folder(self.path_playlist_folder, "local")

                # 更新设置画布
                self.music_update_set()

                self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "全部数据都已清除")

    # 归零统计信息
    def zero_data(self):
        # 获取播放次数
        self.music_file_service.ams_write(self.path_statistics + 'player song count' + ".ams", "0")
        # 获取播放时间
        self.music_file_service.ams_write(self.path_statistics + 'player song time' + ".ams", "0")

        box = self.Box.show_st_dialog(self.music.MusicPlayer_Bottom_Widget, self.play_song_count, self.play_song_time)

        if box:
            self.music_update_set()
            self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "提示", "统计信息已清零")

    # 更新路径管理
    def path_update(self):
        self.music.playlist_lineEdit.setText(self.music_file_service.json_read(self.pathfile_local, "playlist path"))
        self.music.cache_lineEdit.setText(self.music_file_service.json_read(self.pathfile_local, "cache path"))
        self.music.playlist_lineEdit.textEdited.connect(
            lambda: self.music_file_service.json_write(self.pathfile_local, "playlist path",
                                                       self.music.playlist_lineEdit.text()))

    # 更新设置画布按钮
    def music_update_set(self):
        try:
            # 更新字体设置
            self.update_font_set()
            # 更新主题设置
            self.update_theme_set()
            # 更新统计信息
            self.statistic_update()
            # 更新数据管理
            self.data_manage_update()
            # 更新路径管理
            self.path_update()
            # 更新许可证管理
            self.update_license()
        except Exception as a:
            print(a)

    # 更新统计信息
    def statistic_update(self):
        try:
            # 获取歌曲数量
            self.scanner_thread_file = self.music_statistics.FileScannerThread(self.sys_path_playlist)
            self.scanner_thread_file.status_updated.connect(
                lambda msg: self.music.music_sum_Label.setText(f"{'歌曲数量 '}{msg}"))
            self.scanner_thread_file.scan_finished.connect(
                lambda sum_mp3_file: self.music.music_sum_Label.setText(f"{'歌曲数量 '}{len(sum_mp3_file)}"))
            self.scanner_thread_file.start()

            # 获取歌单数量
            self.scanner_thread_folder = self.music_statistics.FolderScannerThread(self.sys_path_playlist)
            self.scanner_thread_folder.status_updated.connect(
                lambda msg: self.music.playlist_sum_Label.setText(f"{'歌单数量 '}{msg}"))
            self.scanner_thread_folder.scan_finished.connect(
                lambda sum_playlist_fouled: self.music.playlist_sum_Label.setText(
                    f"{'歌单数量 '}{len(sum_playlist_fouled)}"))
            self.scanner_thread_folder.start()

            # 获取封面数量
            self.scanner_thread_cover = self.music_statistics.FileScannerThread(self.sys_path_cover)
            self.scanner_thread_cover.status_updated.connect(
                lambda msg: self.music.cover_sum_Label.setText(f"{'封面数量 '}{msg}"))
            self.scanner_thread_cover.scan_finished.connect(
                lambda sum_cover_file: self.music.cover_sum_Label.setText(f"{'封面数量 '}{len(sum_cover_file)}"))
            self.scanner_thread_cover.start()

            # 获取主题数量
            self.scanner_thread_theme = self.music_statistics.FileScannerThread(self.sys_path_theme)
            self.scanner_thread_theme.status_updated.connect(
                lambda msg: self.music.theme_sum_Label.setText(f"{'主题数量 '}{msg}"))
            self.scanner_thread_theme.scan_finished.connect(
                lambda sum_theme_file: self.music.theme_sum_Label.setText(f"{'主题数量 '}{len(sum_theme_file)}"))
            self.scanner_thread_theme.start()

            # 获取歌词数量
            self.scanner_thread_lyric = self.music_statistics.FileScannerThread(self.sys_path_lyric)
            self.scanner_thread_lyric.status_updated.connect(
                lambda msg: self.music.lyric_sum_Label.setText(f"{'歌词数量 '}{msg}"))
            self.scanner_thread_lyric.scan_finished.connect(
                lambda sum_lyric_file: self.music.lyric_sum_Label.setText(f"{'歌词数量 '}{len(sum_lyric_file)}"))
            self.scanner_thread_lyric.start()

            # 获取缩略图数量
            self.scanner_thread_thumbnail = self.music_statistics.FileScannerThread(self.sys_path_thumbnail)
            self.scanner_thread_thumbnail.status_updated.connect(
                lambda msg: self.music.thumbnail_sum_Label.setText(f"{'缩略图数量 '}{msg}"))
            self.scanner_thread_thumbnail.scan_finished.connect(
                lambda sum_thumbnail_file: self.music.thumbnail_sum_Label.setText(
                    f"{'缩略图数量 '}{len(sum_thumbnail_file)}"))
            self.scanner_thread_thumbnail.start()

            # 获取字体数量
            self.scanner_thread_font = self.music_statistics.FileScannerThread(self.sys_path_font)
            self.scanner_thread_font.status_updated.connect(
                lambda msg: self.music.font_sum_Label.setText(f"{'字体数量 '}{msg}"))
            self.scanner_thread_font.scan_finished.connect(
                lambda sum_font_file: self.music.font_sum_Label.setText(f"{'字体数量 '}{len(sum_font_file)}"))
            self.scanner_thread_font.start()

            self.scanner_thread_file.quit()  # 统一销毁
            self.scanner_thread_folder.quit()
            self.scanner_thread_cover.quit()
            self.scanner_thread_theme.quit()
            self.scanner_thread_lyric.quit()
            self.scanner_thread_thumbnail.quit()
            self.scanner_thread_font.quit()

            # 获取播放次数
            self.play_song_count = self.music_file_service.ams_read(self.path_statistics + 'player song count' + ".ams")
            self.music.play_count_Label.setText(f"{'播放次数 '}{self.play_song_count}")

            # 获取播放时间
            self.play_song_time = self.music_service.format_seconds(
                self.music_file_service.ams_read(self.path_statistics + 'song time.ams'))
            self.music.play_song_time_Label.setText(f"{'播放时间 '}{self.play_song_time}")

        except Exception as a:
            print(a)

    # 删除列表歌曲
    def delete_listwidget_song(self):
        box1 = self.Box.del_song(self.music.MusicPlayer_Bottom_Widget)
        if box1:
            # 获取当前选中的项
            currentItem = self.music.music_song_ListWidget.currentItem()
            select_song_list = self.music.music_song_ListWidget.currentItem()
            select_music_name = select_song_list.text()
            music_select = self.path_playlist_folder + self.path_play_playlist + "/" + select_music_name + '.mp3'
            music_select_cover = self.path_cover + self.path_play_playlist + "/" + select_music_name + '.png'
            if currentItem:
                # 删除的时当前播放的
                if currentItem.text() == os.path.splitext(self.play_list[self.play_list_element])[0]:
                    # 播放下一首 防止文件被占用
                    self.down_music_file()
                # 删除选中的项
                self.music.music_song_ListWidget.takeItem(self.music.music_song_ListWidget.row(currentItem))
                self.music_file_service.delete_file(music_select)  # 删除该文件的所有缓存
                self.music_file_service.delete_file(music_select_cover)
                # 更新播放列表
                self.update_play_list()
                del currentItem
                self.Inspector()  # 删除后启用自检
                self.music_update_song()
                self.highlight_current_item()  # 重新高亮所选项

    # 删除列表歌单
    def delete_listwidget_playlist(self):
        box1 = self.Box.del_playlist(self.music.MusicPlayer_Bottom_Widget)
        if box1:
            # 获取当前选中的项
            currentItem = self.music.music_playlist_ListWidget.currentItem()
            select_playlist_list = self.music.music_playlist_ListWidget.currentItem()
            select_music_name = select_playlist_list.text()
            music_select = self.path_playlist_folder + select_music_name
            music_select_cover = self.path_cover + select_music_name
            if currentItem:
                # 删除选中的项
                self.music.music_playlist_ListWidget.takeItem(self.music.music_playlist_ListWidget.row(currentItem))
                self.music_file_service.delete_folder(music_select)
                self.music_file_service.delete_folder(music_select_cover)
                del currentItem
                # 写入当前的歌单 更换进行自检的对象
                self.music_file_service.amc_write(self.path_config_folder + "select playlist.amc",select_music_name)
                self.Inspector()  # 删除后启用自检
                self.music_update_playlist()

    # 重命名歌曲
    def song_rename(self):
        try:
            # 如果无选择 则第一个
            current_item = self.music_widget_service.get_selected_or_first(self.music.music_song_ListWidget)

            # 歌曲重命名
            new_name = MusicMessageBox.Rename_Input(
                widget=self.music.music_song_ListWidget,
                title="重命名",
                text="新名称:",
                current_name=current_item.text()  # 传入当前名称
            )
            if new_name is not None:
                select_music_name = current_item.text()
                self.music_file_service.rename_file(self.path_playlist_folder + self.path_play_playlist
                                                    + "/" + select_music_name + '.mp3', new_name)
                if new_name:
                    current_item.setText(new_name)
                self.update_play_list()
        except Exception as e:
            print(e)
            self.Box.Critical_Box(self.music.MusicPlayer_Bottom_Widget, "错误",
                                  "重命名失败: 正在使用此文件 进程无法访问")
            self.music_update_song()

    # 重命名歌单
    def playlist_rename(self):
        # 如果无选择 则第一个
        current_item = self.music_widget_service.get_selected_or_first(self.music.music_playlist_ListWidget)

        # 歌单重命名
        new_name = MusicMessageBox.Rename_Input(
            widget=self.music.music_playlist_ListWidget,
            title="重命名",
            text="新名称:",
            current_name=current_item.text()  # 传入当前名称
        )
        if new_name is not None:
            select_playlist_name = current_item.text()
            self.music_file_service.rename_folder(self.path_playlist_folder + select_playlist_name, new_name)
            self.music_file_service.rename_folder(self.path_cover + select_playlist_name, new_name)
            if new_name:
                current_item.setText(new_name)
            self.path_playlist = new_name

    # 更新详情画布
    def music_update_details(self):
        try:
            path_music = self.music_file_service.amc_read(self.path_config_folder + 'select music' + self.path_suffix)

            # 更新详情封面
            self.update_details_cover()

            # 使用现有的信息
            id3v2 = self.music_service.read_mp3_tag_v2_mutagen(self.path_playlist_folder+self.path_playlist+'/'+path_music+".mp3")
            self.music.music_title_Label_2.setText(id3v2[0])
            self.music.music_artist_Label_2.setText(id3v2[1])
            self.music.music_album_Label_2.setText(id3v2[2])
            self.music.music_name_Label.setText(id3v2[0][3:])

        except Exception as a:
            print(a)

    # 新建文件夹
    def playlist_new_folder(self):
        name = MusicMessageBox.Rename_Input(self.music.MusicPlayer_Bottom_Widget, "新建歌单", "歌单名称:")
        if name is not None:
            self.music_folder_service.create_directory2(self.path_playlist_folder, name)
            self.music_update_playlist()

    # 更新播放列表
    def update_play_list(self):
        path = self.path_playlist  # 分离
        self.music_file_service.amc_write(self.path_config_folder + 'play playlist' + self.path_suffix,
                                          path)
        self.path_play_playlist = path
        self.play_list = self.music_folder_service.get_all_files(
            self.path_playlist_folder + self.path_play_playlist)

    # 播放模式按钮
    def play_mode(self):
        try:
            self.music_play_mode += 1
            # 归零播放状态
            if self.music_play_mode > 3:
                self.music_play_mode = 1
            if self.music_play_mode == 1:
                self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "random play"))
                self.music_file_service.amc_write(self.path_config_folder + "play mode.amc", "Random Play")
            elif self.music_play_mode == 2:
                self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "loop play"))
                self.music_file_service.amc_write(self.path_config_folder + "play mode.amc", "Loop Play")
            elif self.music_play_mode == 3:
                self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "single loop"))
                self.music_file_service.amc_write(self.path_config_folder + "play mode.amc", "Single Loop")
        except Exception as a:
            print(a)

    # 更新播放模式按钮
    def play_update_mode(self):
        if self.path_play_mode == "Random Play":  # 随机播放
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "random play"))
            self.music_play_mode = 1
        elif self.path_play_mode == "Loop Play":  # 循环播放
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "loop play"))
            self.music_play_mode = 2
        elif self.path_play_mode == "Single Loop":  # 单曲循环
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "single loop"))
            self.music_play_mode = 3

    # 更新歌词
    def update_lyric(self):
        try:
            self.music_update_details()

            path_music = self.music_file_service.amc_read(self.path_config_folder + 'select music.amc')

            self.timer = "0:00.000"

            select_music = self.path_play_playlist + '/' + path_music

            if not os.path.exists(self.path_lyric + select_music + ".lrc"):
                self.music_lyric.extract_lyrics(
                    self.path_playlist_folder + self.path_playlist + '/' + path_music + ".mp3",
                    self.path_play_playlist, self.path_lyric,
                    self.path_lyric + select_music + ".lrc")  # 生成文件

            # 刷新歌词翻译模式 最大翻译行
            self.switch_lyric = self.music_file_service.str_bool(
                self.music_file_service.amc_read(self.path_switch_folder + "lyric translation.amc"))
            self.lyric_line = int(self.music_file_service.amc_read(self.path_config_folder + "lyric line.amc"))
            self.lyrics_data = self.music_lyric.parse_lrc_file(self.path_lyric + select_music + ".lrc",
                                                               self.switch_lyric,
                                                               self.lyric_line)  # 读取文件

            self.lyric_widget.set_lyrics(self.lyrics_data, f"{self.theme_color}")

        except Exception as a:
            # 提取完整的堆栈信息
            tb = traceback.extract_tb(sys.exc_info()[2])
            error_frame = tb[-1]
            filename = error_frame.filename
            line_number = error_frame.lineno
            func_name = error_frame.name
            print(f"更新歌曲歌词函数中发生错误: 变量 {a}, 所在文件 {filename}, 行号 {line_number}, 函数 {func_name}")

    # 更新高级信息
    def music_update_senior_info(self):
        # 指定音频文件路径
        audio_file_path = self.music_file_service.amc_read(self.path_config_folder + 'select music.amc')

        self.music.info_Button.setEnabled(True)

        self.music.Center_StackedWidget.setCurrentIndex(1)
        # 启用文本编辑框
        self.music.senior_info_textEdit.setReadOnly(False)
        # 清空文本编辑框
        self.music.senior_info_textEdit.clear()
        # 遍历所有轨道并输出详细信息
        self.music.senior_info_textEdit.append(self.music_service.get_audio_tracks(self.path_playlist_folder +
                                                                                   self.path_play_playlist + '/' +
                                                                                   audio_file_path + '.mp3'))
        # 归零滚动条
        self.music.senior_info_textEdit.verticalScrollBar().setValue(0)
        # 禁用文本编辑框
        self.music.senior_info_textEdit.setReadOnly(True)

    # 更新数据管理
    def data_manage_update(self):
        try:
            self.cover_worker = self.music_thread.FolderServicePlusRealTime(self.path_cover, "封面缓存 ")
            self.cover_worker.moveToThread(self.cover_thread)
            self.cover_thread.started.connect(self.cover_worker.run)
            self.cover_worker.status_updated.connect(lambda s: self.music.cover_cache_size_Label.setText(s))
            self.cover_thread.start()

            self.lyric_worker = self.music_thread.FolderServicePlusRealTime(self.path_lyric, "歌词缓存 ")
            self.lyric_worker.moveToThread(self.lyric_thread)
            self.lyric_thread.started.connect(self.lyric_worker.run)
            self.lyric_worker.status_updated.connect(lambda s: self.music.lyric_cache_Label.setText(s))
            self.lyric_thread.start()

            self.song_thumbnail_worker = self.music_thread.FolderServicePlusRealTime(self.path_thumbnail, "缩略图缓存 ")
            self.song_thumbnail_worker.moveToThread(self.song_thumbnail_thread)
            self.song_thumbnail_thread.started.connect(self.song_thumbnail_worker.run)
            self.song_thumbnail_worker.status_updated.connect(
                lambda s: self.music.song_thumbnail_cache_Label.setText(s))
            self.song_thumbnail_thread.start()

            self.theme_worker = self.music_thread.FolderServicePlusRealTime(self.path_theme_folder, "主题数据 ")
            self.theme_worker.moveToThread(self.theme_thread)
            self.theme_thread.started.connect(self.theme_worker.run)
            self.theme_worker.status_updated.connect(lambda s: self.music.theme_data_size_Label.setText(s))
            self.theme_thread.start()

            self.font_worker = self.music_thread.FolderServicePlusRealTime(self.path_font, "字体数据 ")
            self.font_worker.moveToThread(self.font_thread)
            self.font_thread.started.connect(self.font_worker.run)
            self.font_worker.status_updated.connect(lambda s: self.music.font_data_size_Label.setText(s))
            self.font_thread.start()

            self.song_worker = self.music_thread.FolderServicePlusRealTime(self.path_playlist_folder, "全部歌曲 ")
            self.song_worker.moveToThread(self.song_thread)
            self.song_thread.started.connect(self.song_worker.run)
            self.song_worker.status_updated.connect(lambda s: self.music.song_all_size_Label.setText(s))
            self.song_thread.start()

            self.cover_thread.quit()  # 启动完后退出
            self.song_thread.quit()
            self.lyric_thread.quit()
            self.song_thumbnail_thread.quit()
            self.font_thread.quit()
            self.theme_thread.quit()


        except Exception as a:
            print(a)

    # 更新许可管理
    def update_license(self):
        try:
            # 设置许可证路径
            self.music.lic_path_Label.setText(self.license_file)
            if not os.path.exists(self.license_file):
                self.music.lic_state_Label.setStyleSheet("color:rgb(255,0,0)")
                self.music.lic_path_Label.setStyleSheet("color:rgb(255,0,0)")
            else:
                self.music.lic_state_Label.setStyleSheet(f"color:rgb({self.theme_color})")
                self.music.lic_path_Label.setStyleSheet(f"color:rgb({self.theme_color})")

            self.license_thread_path = self.music_license.LicensePath(self.license_file)
            self.license_thread_path.decode_finished.connect(lambda x: self.music.lic_state_Label.setText(x))
            self.license_thread_path.start()

            # 设置产品名称
            self.license_thread_name = self.music_license.LicenseDecoderName(self.license_file)
            self.license_thread_name.decode_finished.connect(lambda x: self.music.lic_name_Label.setText(x))
            self.license_thread_name.start()

            # 设置产品名称
            self.license_thread_version = self.music_license.LicenseDecoderVersion(self.license_file)
            self.license_thread_version.decode_finished.connect(lambda x: self.music.lic_version_Label.setText(x))
            self.license_thread_version.start()

            # 设置激活模式
            self.license_thread_type = self.music_license.LicenseDecoderType(self.license_file)
            self.license_thread_type.decode_finished.connect(lambda x: self.music.lic_type_Label.setText(x))
            self.license_thread_type.start()

            # 设置高级功能权限
            self.license_thread_features = self.music_license.LicenseDecoderFeatures(self.license_file)
            self.license_thread_features.decode_finished.connect(lambda x: self.music.lic_features_Label.setText(x))
            self.license_thread_features.start()

            # 设置UUID
            self.license_thread_uuid = self.music_license.LicenseDecoderUUID(self.license_file)
            self.license_thread_uuid.decode_finished.connect(lambda x: self.music.lic_uuid_Label.setText(x))
            self.license_thread_uuid.start()

            # 设置主板指纹
            self.license_thread_uid = self.music_license.LicenseDecoderUID(self.license_file)
            self.license_thread_uid.decode_finished.connect(lambda x: self.music.lic_uid_Label.setText(x))
            self.license_thread_uid.start()

            # 设置许可证编号
            self.license_thread_id = self.music_license.LicenseDecoderID(self.license_file)
            self.license_thread_id.decode_finished.connect(lambda x: self.music.lic_id_Label.setText(x))
            self.license_thread_id.start()

            # 设置许可证秘钥
            self.license_thread_key = self.music_license.LicenseDecoderKey(self.license_file)
            self.license_thread_key.decode_finished.connect(lambda x: self.music.lic_key_Label.setText(x))
            self.license_thread_key.start()

            # 设置时效类型
            self.license_thread_time_type = self.music_license.LicenseDecoderTimeType(self.license_file)
            self.license_thread_time_type.decode_finished.connect(lambda x: self.music.lic_time_type_Label.setText(x))
            self.license_thread_time_type.start()

            # 设置签发时间
            self.license_thread_begin = self.music_license.LicenseDecoderBeginDate(self.license_file)
            self.license_thread_begin.decode_finished.connect(lambda x: self.music.lic_begin_date_Label.setText(x))
            self.license_thread_begin.start()

            # 设置到期时间
            self.license_thread_end = self.music_license.LicenseDecoderEndDate(self.license_file)
            self.license_thread_end.decode_finished.connect(lambda x: self.music.lic_end_date_Label.setText(x))
            self.license_thread_end.start()

            # 设置激活状态
            self.license_thread_activation = self.music_license.LicenseDecoderActivation(self.license_file)
            self.license_thread_activation.decode_finished.connect(lambda x: self.music.lic_activation_Label.setText(x))
            self.license_thread_activation.start()

            # 设置数字签名
            self.license_thread_DigitalSignature = self.music_license.LicenseDecoderDigitalSignature(self.license_file)
            self.license_thread_DigitalSignature.decode_finished.connect(
                lambda x: self.music.lic_DigitalSignature_Label.setText(x))
            self.license_thread_DigitalSignature.start()

            # 设置到期时间
            self.license_thread_AuthorizationInformation = self.music_license.LicenseDecoderAuthorizationInformation(
                self.license_file)
            self.license_thread_AuthorizationInformation.decode_finished.connect(
                lambda x: self.music.lic_AuthorizationInformation_Label.setText(x))
            self.license_thread_AuthorizationInformation.start()

            # 设置激活状态
            self.license_thread_Copyright = self.music_license.LicenseDecoderCopyright(self.license_file)
            self.license_thread_Copyright.decode_finished.connect(lambda x: self.music.lic_Copyright_Label.setText(x))
            self.license_thread_Copyright.start()

        except Exception as a:
            print("许可丢失", a)

    # 选择现有许可
    def select_path_lic(self):
        try:
            # 提取根文件夹中的许可
            self.select_lic, sift = QFileDialog.getOpenFileName(self.music.MusicPlayer_Bottom_Widget,
                                                                '选择现有许可证', "Data/"
                                                                , 'lic (*.lic)')
            if self.select_lic != "":
                self.license_file = self.select_lic  # 应用许可
                self.music_file_service.amc_write(self.path_config_folder + "license currently use.amc",
                                                  self.select_lic)
                self.update_license()  # 更新

        except Exception as a:
            print(a)

    # 选择许可证文件
    def select_file_lic(self):
        try:
            # 提取根文件夹中的许可
            self.select_lic_file, sift = QFileDialog.getOpenFileName(self.music.MusicPlayer_Bottom_Widget,
                                                                     '选择许可证文件', self.path_desktop
                                                                     , 'lic (*.lic)')
            if self.select_lic_file != "":
                self.license_file = self.select_lic_file  # 应用许可
                self.music_file_service.amc_write(self.path_config_folder + "license currently use.amc",
                                                  self.select_lic_file)
                self.update_license()  # 更新

        except Exception as a:
            print(a)

    # 注销许可证文件
    def lic_logout(self):
        box = self.Box.Logout(self.music.MusicPlayer_Bottom_Widget)
        if box:
            self.music_verifyer.Logout(self.license_file)
            self.Box.Critical_Box(self.music.MusicPlayer_Bottom_Widget, "注销许可证", "当前许可证已注销")
            self.update_license()

    # 中断播放
    def music_interrupt(self):
        # 停止进度条更新
        self.thread_play.pause()

        # 仅在播放时实现
        if not self.music_play_state:

            # 实现拖动进度条播放音乐
            self.music.music_Progressbar.setValue(0)
            self.music_player.set_play(0)

            if self.thread_play:  # 如果正在更新进度条
                self.thread_play.pause()  # 暂停

            self.music.music_time_1_Label.setText("0:00")

            # 更新可视化播放器
            self.update_player()

        else:
            self.music.music_Progressbar.setValue(0)
            # 归零格式化分钟
            self.music_duration = self.music_service.format_minutes(0)
            self.music.music_time_1_Label.setText(self.music_duration)

    # 更新喜欢按钮
    def update_like(self):
        if not self.like_state:
            self.music.like_Button.setIcon(QIcon(":/ico/MusicIco/like2.png"))
            # 写入到数据库中
            self.database.add_item(self.path_database,
                                   self.path_playlist_folder + self.path_play_playlist + "/" +
                                   self.play_list[self.play_list_element])  # 确保是播放的文件
            self.like_state = True
        elif self.like_state:
            self.music.like_Button.setIcon(self.image_icon(self.resources_ico, "like"))
            # 从数据库中删除
            self.database.remove_item(self.path_database,
                                      self.path_playlist_folder + self.path_play_playlist + "/" +
                                      self.play_list[self.play_list_element])
            self.like_state = False

    # 更新喜欢检查
    def update_like_check(self, p=None, n=None):
        if p is None:
            path = self.path_play_playlist
            name = self.play_list[self.play_list_element]
        else:
            path = p
            name = n
        if self.database.check_item(self.path_database, self.path_playlist_folder + path + "/" + name):
            self.music.like_Button.setIcon(QIcon(":/ico/MusicIco/like2.png"))
            self.like_state = True
        else:
            self.music.like_Button.setIcon(self.image_icon(self.resources_ico, "like"))
            self.like_state = False

    # 更新后端播放监控
    def update_music_player(self, model):
        try:
            if model == "in":
                self.fade_in_time = self.music.fade_in_text_Label.text()
                self.music_file_service.amc_write(self.path_config_folder + "fade in.amc", self.fade_in_time)
            elif model == "out":
                self.fade_out_time = self.music.fade_out_text_Label.text()
                self.music_file_service.amc_write(self.path_config_folder + "fade out.amc", self.fade_out_time)

            self.music_player = MusicPlay.MusicMonitor(self.fade_in_time, self.fade_out_time)
        except Exception as a:
            print(a)

    # 更新收藏列表
    def music_update_collect(self):
        try:
            # 终止锁
            self.stop_thumbnail_key = True

            # 清空列表项目
            self.music.music_collect_ListWidget.clear()

            # 刷新项图标开关
            self.switch_item_ico = self.music_file_service.str_bool(
                self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))

            items = 0  # 文件计数器 添加图标
            for line in self.database.traverse_item(self.path_database):
                self.thumbnail_key = False

                self.music.music_collect_ListWidget.addItem(os.path.splitext(os.path.basename(line))[0])

                # 终止锁
                if not self.stop_thumbnail_key:
                    break  # 跳出扫描

                # 开启项目图标 带动态循环的遍历
                if self.switch_item_ico:
                    # 加速拼接路径
                    path_thumbnail_path = self.path_thumbnail + self.database.search_item(self.path_database,
                                                                                          os.path.splitext(
                                                                                              os.path.basename(line))[
                                                                                              0]) + "/" + \
                                          os.path.splitext(os.path.basename(line))[0] + ".webp"
                    # 缓存存在
                    if os.path.exists(path_thumbnail_path):
                        # 使用缓存中的数据
                        icon = self.ico_cache.get_icon(path_thumbnail_path)
                        self.music.music_collect_ListWidget.item(items).setIcon(icon)
                    # 缓存不存在则使用文件图标
                    else:
                        self.music.music_collect_ListWidget.item(items).setIcon(
                            self.image_icon(self.resources_ico, "music file"))

                items += 1

            self.thumbnail_key = True
            self.highlight_current_item_str(os.path.splitext(os.path.basename(self.path_music))[0],
                                                  self.music.music_collect_ListWidget)
        except Exception as a:
            print(a)

    # 选择播放的收藏
    def select_music_file_like(self):
        try:
            # 获取列表全部项目
            self.select_song_list = self.music.music_collect_ListWidget.currentItem()
            # 获取选择的项目
            self.select_music_name = self.select_song_list.text()
            self.music_select = self.select_music_name + '.mp3'

            # 设置选择的音乐名称
            self.music.music_name_Label.setText(self.select_music_name)

            # 写入选择的文件
            self.music_file_service.amc_write(self.path_config_folder + 'select music' + self.path_suffix,
                                              self.select_music_name)

            # 更新歌词
            self.update_lyric()

            # 更新歌曲项图标
            # 刷新开关
            self.switch_item_ico = self.music_file_service.str_bool(
                self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))
            if self.switch_item_ico:
                # 项存在则应用图标
                if self.music.music_collect_ListWidget.item(self.music.music_collect_ListWidget.currentRow()):
                    # 不存在则创建
                    if not os.path.exists(
                            self.path_thumbnail + self.database.search_item(self.path_database,
                                                                            self.select_music_name) + "/" + self.music.music_collect_ListWidget.currentItem().text() + ".webp"):
                        self.update_thumbnail(self.database.search_item(self.path_database, self.select_music_name))
                    icon = QIcon(
                        self.path_thumbnail + self.database.search_item(self.path_database,
                                                                        self.select_music_name) + "/" + self.music.music_collect_ListWidget.currentItem().text() + ".webp")
                    self.music.music_collect_ListWidget.item(self.music.music_collect_ListWidget.currentRow()).setIcon(
                        icon)

            # 更新喜欢
            self.update_like_check(self.database.search_item(self.path_database, self.select_music_name),
                                   self.select_music_name)

        except Exception as a:
            print("选择播放的文件 函数中发生错误", a)

    # 播放选择的收藏
    def list_play_music_like(self):
        try:

            self.path_play_playlist = self.database.search_item(self.path_database, self.select_music_name)
            self.play_list = self.music_folder_service.get_all_files(
                self.path_playlist_folder + self.path_play_playlist)

            # 更新播放次数
            self.music_file_service.process_ams_file(self.path_statistics + "player song count.ams", 1)

            # 设置要播放的音乐文件路径 线程
            self.music_player.set_load(self.path_playlist_folder + self.path_play_playlist + '/' + self.music_select)

            # 更新歌曲进度条
            # 归零歌曲进度条当前值
            self.music.music_Progressbar.setValue(0)

            # 获取歌曲时长 分钟
            self.music_duration_min = self.music_service.get_duration_ffmpeg_fast(
                self.path_playlist_folder + self.path_play_playlist + '/' +
                self.select_music_name + ".mp3")

            # 格式化秒
            self.music_duration_s = self.music_service.get_duration_ffmpeg_fast2(
                self.path_playlist_folder + self.path_play_playlist + '/' + self.select_music_name + ".mp3")
            # 设置进度条最大值
            self.music.music_Progressbar.setMaximum(self.music_duration_s)

            self.music.music_time_1_Label.setText('0:00')
            self.music.music_time_2_Label.setText(self.music_duration_min)

            # 停止进度条更新 线程存在
            if self.thread_play:
                self.thread_play.stop()

            # 播放音乐
            # 在歌曲进度条的值的地方播放
            self.music_player.set_play(self.music.music_Progressbar.value() - 1)

            # 更新可视化播放器
            self.update_player()

            self.music_player.resume()
            self.music_player.start()  # 启动监测线程

            self.music_play_state = False
            self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))

            # 更新歌词
            self.update_lyric()

        except Exception as a:
            print(a)

    # 更新热键
    def update_hotkey(self):
        # 读取选择的热键
        self.hotkey_play = self.music_file_service.amc_read(self.path_hotkey_folder + "play.amc")
        self.hotkey_playlist = self.music_file_service.amc_read(self.path_hotkey_folder + "playlist.amc")
        self.hotkey_time_up = self.music_file_service.amc_read(self.path_hotkey_folder + "time up.amc")
        self.hotkey_time_down = self.music_file_service.amc_read(self.path_hotkey_folder + "time down.amc")
        self.hotkey_music_up = self.music_file_service.amc_read(self.path_hotkey_folder + "music up.amc")
        self.hotkey_music_down = self.music_file_service.amc_read(self.path_hotkey_folder + "music down.amc")
        self.hotkey_music_like = self.music_file_service.amc_read(self.path_hotkey_folder + "music like.amc")

        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.play_music_file, self.hotkey_play)
        self.music.key_Label.setText(f"播放  {self.hotkey_play}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget,
                                           lambda: self.Music_Update("Music_PlayList"), self.hotkey_playlist)
        self.music.key_Label_2.setText(f"歌单  {self.hotkey_playlist}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.music_up_time,
                                           self.hotkey_time_up)
        self.music.key_Label_3.setText(f"快进  {self.hotkey_time_up}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.music_down_time,
                                           self.hotkey_time_down)
        self.music.key_Label_4.setText(f"快退  {self.hotkey_time_down}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.up_music_file,
                                           self.hotkey_music_up)
        self.music.key_Label_5.setText(f"上一首  {self.hotkey_music_up}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.down_music_file,
                                           self.hotkey_music_down)
        self.music.key_Label_6.setText(f"下一首  {self.hotkey_music_down}")
        self.music_hotkey.bind_key_to_slot(self.music.MusicPlayer_Bottom_Widget, self.update_like,
                                           self.hotkey_music_like)
        self.music.key_Label_7.setText(f"喜欢  {self.hotkey_music_like}")

    # 选择热键
    def select_hot_key(self, file):
        # 设置遮罩
        mask = self.music_mask.SizeFittingWidget(self.music.MusicPlayer_Bottom_Widget)
        mask.resize(self.music.MusicPlayer_Bottom_Widget.size())

        # 显示遮罩
        mask.show()
        hotkey = self.hotkey_selector.hot_key(self.app, self.music.play_Button, f"{self.theme_color}")
        # 确认更改
        if hotkey is not None:
            self.music_file_service.amc_write(self.path_hotkey_folder + file, hotkey)
            # 更新选择的热键
            self.update_hotkey()

        # 隐藏遮罩
        mask.hide()

    # 更新全局钩子
    def update_hook(self):
        # 读取选择的钩子
        self.hook_play = self.music_file_service.amc_read(self.path_hook_folder + "play.amc")
        self.hook_time_up = self.music_file_service.amc_read(self.path_hook_folder + "time up.amc")
        self.hook_time_down = self.music_file_service.amc_read(self.path_hook_folder + "time down.amc")
        self.hook_music_up = self.music_file_service.amc_read(self.path_hook_folder + "music up.amc")
        self.hook_music_down = self.music_file_service.amc_read(self.path_hook_folder + "music down.amc")

        if self.hook_play_thread:
            self.hook_play_thread.stop()
        if self.hook_time_up_thread:
            self.hook_time_up_thread.stop()
        if self.hook_time_down_thread:
            self.hook_time_down_thread.stop()
        if self.hook_music_up_thread:
            self.hook_music_up_thread.stop()
        if self.hook_music_down_thread:
            self.hook_music_down_thread.stop()

        self.hook_play_thread = self.music_hotkey.GlobalHotkeyManager(self.hook_play)
        self.hook_play_thread.triggered.connect(lambda: self.play_music_file())
        self.music.hook_Label.setText(f"播放 {self.hook_play}")
        self.hook_time_up_thread = self.music_hotkey.GlobalHotkeyManager(self.hook_time_up)
        self.hook_time_up_thread.triggered.connect(lambda: self.music_up_time())
        self.music.hook_Label_2.setText(f"快进 {self.hook_time_up}")
        self.hook_time_down_thread = self.music_hotkey.GlobalHotkeyManager(self.hook_time_down)
        self.hook_time_down_thread.triggered.connect(lambda: self.music_down_time())
        self.music.hook_Label_3.setText(f"快退 {self.hook_time_down}")
        self.hook_music_up_thread = self.music_hotkey.GlobalHotkeyManager(self.hook_music_up)
        self.hook_music_up_thread.triggered.connect(lambda: self.up_music_file())
        self.music.hook_Label_4.setText(f"上一首 {self.hook_music_up}")
        self.hook_music_down_thread = self.music_hotkey.GlobalHotkeyManager(self.hook_music_down)
        self.hook_music_down_thread.triggered.connect(lambda: self.down_music_file())
        self.music.hook_Label_5.setText(f"下一首 {self.hook_music_down}")

    # 选择全局钩子
    def select_hook(self, file):
        # 设置遮罩
        mask = self.music_mask.SizeFittingWidget(self.music.MusicPlayer_Bottom_Widget)
        mask.resize(self.music.MusicPlayer_Bottom_Widget.size())

        # 显示遮罩
        mask.show()
        hook = HookSelector.hook_key(self.app, self.music.play_Button, f"{self.theme_color}")
        # 确认更改
        if hook is not None:
            self.music_file_service.amc_write(self.path_hook_folder + file, hook)
            # 更新选择的钩子
            self.update_hook()

        # 隐藏遮罩
        mask.hide()

    # 更新字体
    def update_font(self, index=None):
        # 手动更新
        if index is None:
            font = self.music_file_service.amc_read(self.path_config_folder + 'select font' + self.path_suffix)
            # 存在则为字体文件 否则系统文件
            if os.path.exists(self.path_font + font + ".ttf"):
                self.music_service.set_all_font_local(self.music.MusicPlayer_Bottom_Widget,
                                                      self.path_font + font + ".ttf")
            else:
                self.music_service.set_all_font_sys(self.music.MusicPlayer_Bottom_Widget, font)
        else:
            # 存在则为字体文件 否则系统文件
            if os.path.exists(self.path_font + self.music.font_comboBox.itemText(index) + ".ttf"):
                self.music_service.set_all_font_local(self.music.MusicPlayer_Bottom_Widget,
                                                      self.path_font + self.music.font_comboBox.itemText(
                                                          index) + ".ttf")
            else:
                self.music_service.set_all_font_sys(self.music.MusicPlayer_Bottom_Widget,
                                                    self.music.font_comboBox.itemText(index))

            self.music_file_service.amc_write(self.path_config_folder + 'select font' + self.path_suffix
                                              , self.music.font_comboBox.itemText(index))

    # 导入字体
    def import_font(self):
        # 提取
        path, sift = QFileDialog.getOpenFileNames(self.music.MusicPlayer_Bottom_Widget,
                                                  '导入字体', self.path_desktop
                                                  , '字体文件 (*.ttf)')
        # 筛选多个文件
        if path:
            for i in path:
                # 复制文件到指定路径
                self.music_import.copy_file(i, "Font/")
                # 更新歌曲列表
                self.update_font_set()

    # 删除字体
    def del_font(self):
        try:
            box = self.Box.text_box(self.music.MusicPlayer_Bottom_Widget, "删除字体", "删除字体？", "是的", "不")
            if box:
                if os.path.exists(self.path_font + self.music.font_comboBox.currentText() + ".ttf"):
                    self.music_explorer.open_in_explorer(self.path_font)
                else:
                    self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "删除字体？", "无法删除系统字体")
        except Exception as a:
            print(a)

    # 更新字体下拉框
    def update_font_set(self):
        self.music.font_comboBox.clear()

        # 先加入默认字体
        self.music.font_comboBox.addItem("黑体")
        self.music.font_comboBox.addItem("幼圆")
        self.music.font_comboBox.addItem("宋体")
        self.music.font_comboBox.addItem("楷体")
        self.music.font_comboBox.addItem("微软雅黑")
        self.music.font_comboBox.addItem("华文细黑")

        for root, dirs, files in os.walk(self.path_font):
            for item in files:
                self.music.font_comboBox.addItem(os.path.splitext(item)[0])

        self.music.font_comboBox.setCurrentText(self.select_font)

    # 刷新歌曲项的图标
    def update_song_item_ico(self):
        # 刷新项图标开关
        self.switch_item_ico = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))
        if self.switch_item_ico:
            # 项存在则应用图标
            if self.music.music_song_ListWidget.item(self.music.music_song_ListWidget.currentRow()):
                # 不存在则创建
                if not os.path.exists(
                        self.path_thumbnail + self.path_playlist + "/" + self.music.music_song_ListWidget.currentItem().text() + ".webp"):
                    self.update_thumbnail()
                icon = QIcon(
                    self.path_thumbnail + self.path_playlist + "/" + self.music.music_song_ListWidget.currentItem().text() + ".webp")
                self.music.music_song_ListWidget.item(self.music.music_song_ListWidget.currentRow()).setIcon(icon)

    # 更新计时器
    def update_timer(self, time):
        self.timer = time

        self.lyric_widget.update_current_time_str(self.timer)

    # 添加按钮提示
    def tip(self):
        self.music_tip.HoverToolTip(self.music.song_Button, "歌曲")
        self.music_tip.HoverToolTip(self.music.collect_Button, "收藏")

        self.music_tip.HoverToolTip(self.music.info_Button, "信息")
        self.music_tip.HoverToolTip(self.music.set_Button, "设置")
        self.music_tip.HoverToolTip(self.music.EXIT_Button, "关闭")

        self.music_tip.HoverToolTip(self.music.state_Button, "播放模式")
        self.music_tip.HoverToolTip(self.music.volume_Button, "音量")
        self.music_tip.HoverToolTip(self.music.clock_Button, "定时关闭")
        self.music_tip.HoverToolTip(self.music.like_Button, "喜欢")

        self.music_tip.HoverToolTip(self.music.up_Button, "上一首")
        self.music_tip.HoverToolTip(self.music.up_time_Button, "快进")
        self.music_tip.HoverToolTip(self.music.play_Button, "播放")
        self.music_tip.HoverToolTip(self.music.down_time_Button, "后退")
        self.music_tip.HoverToolTip(self.music.down_Button, "下一首")

        self.music_tip.HoverToolTip(self.music.interrupt_Button, "中断播放")

        self.music_tip.HoverToolTip(self.music.import_music_Button, "导入歌曲")
        self.music_tip.HoverToolTip(self.music.import_playlist_Button, "导入歌单")

        self.music_tip.HoverToolTip(self.music.theme_import_Button, "导入主题")
        self.music_tip.HoverToolTip(self.music.theme_up_Button, "添加主题")
        self.music_tip.HoverToolTip(self.music.theme_edit_Button, "编辑主题")
        self.music_tip.HoverToolTip(self.music.theme_down_Button, "删除主题")

        self.music_tip.HoverToolTip(self.music.font_import_Button, "导入字体")
        self.music_tip.HoverToolTip(self.music.font_down_Button, "删除字体")

    # 抽屉音量
    def drawer_music(self):
        try:
            self.music.drawer_label.setText(str(self.music.drawer_horizontalSlider.value()) + "%")
            # 范围值
            if self.music.drawer_horizontalSlider.value() == 0:
                self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 0"))
            if 1 <= self.music.drawer_horizontalSlider.value() <= 10:
                self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 1"))
            if 10 <= self.music.drawer_horizontalSlider.value() <= 50:
                self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 2"))
            if 50 <= self.music.drawer_horizontalSlider.value() <= 70:
                self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 3"))
            if 70 <= self.music.drawer_horizontalSlider.value() <= 100:
                self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 4"))
        except Exception as a:
            print(a)

    # 更新抽屉音量
    def update_drawer_music(self):
        self.music_file_service.amc_write(self.path_config_folder + "select volume.amc",
                                          str(self.music.drawer_horizontalSlider.value()))
        self.music_player.set_volume(self.music.drawer_horizontalSlider.value() / 100)

    # 更新动画
    def update_animation(self):
        self.animation_button = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "button animation.amc"))
        self.animation_tacked_widget = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "stacked widget.amc"))
        self.animation_slider_animation = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "slider animation.amc"))
        self.animation_elastic_rolling = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "elastic rolling.amc"))
        self.animation_list_elastic_rolling = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "list elastic rolling.amc"))
        self.animation_list_item = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "list item.amc"))
        self.animation_combobox_animation = self.music_file_service.str_bool(self.music_file_service.amc_read(self.path_animation_folder + "combobox animation.amc"))

        # 按钮动画
        if self.animation_button:
            # 添加按钮动画
            # 在循环中创建并保存动画器
            for widget in self.music.MusicPlayer_Bottom_Widget.findChildren(QPushButton):
                # 检查是否是完全排除
                if widget == self.cover_button:
                    # 直接跳过，不添加任何动画
                    continue
                if widget in self.excluded_widgets:
                    # 为排除的控件设置图标动画
                    animator = QtAnimation.ButtonIconColorAnimator(widget)
                else:
                    # 为其他控件设置通用动画
                    animator = QtAnimation.ButtonColorAnimator(widget)
                self.button_animators.append(animator)
        # 堆叠窗口动画
        if self.animation_tacked_widget:
            QtAnimation.StackedWidgetAnimator(self.music.Center_StackedWidget, 200)
        # 滑动条动画
        if self.animation_slider_animation:
            QtAnimation.SliderAnimator(self.music.drawer_horizontalSlider)
        # 弹性滚动动画
        if self.animation_elastic_rolling:
            QtAnimation.ElasticScrollAnimator(self.music.set_scrollArea)
            QtAnimation.ElasticScrollAnimator(self.music.senior_info_textEdit)
        # 列表弹性滚动动画
        if self.animation_list_elastic_rolling:
            QtAnimation.ElasticListWidgetScrollAnimator(self.music.music_song_ListWidget)
            QtAnimation.ElasticListWidgetScrollAnimator(self.music.music_playlist_ListWidget)
            QtAnimation.ElasticListWidgetScrollAnimator(self.music.music_collect_ListWidget)
        # 列表项动画
        if self.animation_list_item:
            for widget in self.music.MusicPlayer_Bottom_Widget.findChildren(QListWidget):
                animator = QtAnimation.ListItemAnimator(widget)
                self.list_animators.append(animator)
        # 下拉列表动画
        if self.animation_combobox_animation:
            for widget in self.music.MusicPlayer_Bottom_Widget.findChildren(QComboBox):
                animator = QtAnimation.ComboBoxAnimator(widget)
                self.combobox_animators.append(animator)

    # 导入主题
    def import_theme(self):
        # 提取
        path, sift = QFileDialog.getOpenFileNames(self.music.MusicPlayer_Bottom_Widget,
                                                  '导入主题', self.path_desktop
                                                  , '主题包文件 (*.tsp)')
        # 筛选多个文件
        if path:
            for i in path:
                # 复制文件到指定路径
                self.music_import.copy_file(i, "Theme/")
                # 更新主题列表
                self.update_theme_set()

    # 删除主题
    def del_theme(self):
        try:
            box = self.Box.text_box(self.music.MusicPlayer_Bottom_Widget, "删除主题", "删除主题？", "是的", "不")
            if box:
                if os.path.exists(self.path_theme_folder + self.music.theme_comboBox.currentText() + ".tsp"):
                    os.remove(self.path_theme_folder + self.music.theme_comboBox.currentText() + ".tsp")
                    self.update_theme_set()  # 更新主题
                    self.update_theme(self.music.theme_comboBox.maxVisibleItems())
                else:
                    self.Box.Information_Box(self.music.MusicPlayer_Bottom_Widget, "删除主题？", "无法删除主题模式")
        except Exception as a:
            print(a)

    # 创建主题
    def new_theme(self):
        try:
            dialog = ThemeSelector.MainDialog()
            dialog.exec_()

            theme_color, bg_color, filename = dialog.getResults()

            theme_data = {
                "color": f"{theme_color.red()},{theme_color.green()},{theme_color.blue()}",
                "background": f"{bg_color.red()},{bg_color.green()},{bg_color.blue()}",
                "image": "None",
                "qss": "None"
            }
            with open(f"{self.path_theme_folder + filename}.tsp", 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)

            # 更新下拉列表
            self.update_theme_set()

        except Exception as a:
            print(a)

    # 更新主题下拉框
    def update_theme_set(self):
        self.music.theme_comboBox.clear()

        for root, dirs, files in os.walk(self.path_theme_folder):
            for item in files:
                self.music.theme_comboBox.addItem(os.path.splitext(item)[0])

        self.music.theme_comboBox.setCurrentText(self.select_theme)

    # 更新主题
    def update_theme(self, item=None):
        # 遍历并应用样式表
        def set_all_qss(widget, qss_style):
            widget.setStyleSheet(qss_style)
            for child in widget.children():
                if isinstance(child, QWidget):
                    set_all_qss(child, qss_style)
        try:

            if item is not None:
                self.music_file_service.amc_write(self.path_config_folder + 'select theme.amc'
                                                  , str(item))
                theme = item
            else:
                theme = self.music.theme_comboBox.currentText()
            # 存在为主题包 否则是模式
            self.theme_color = self.music_file_service.json_read(
                self.path_theme_folder + theme + ".tsp", "color")
            self.theme_background = self.music_file_service.json_read(
                self.path_theme_folder + theme + ".tsp", "background")

            set_all_qss(self.music.MusicPlayer_Bottom_Widget,
                        self.music_acrylic.Theme.theme(self.theme_color, self.theme_background))
            for obj in self.button_animators:
                # 检查是否有属性
                if hasattr(obj, 'restart_animator'):
                    obj.restart_animator()
            for obj in self.combobox_animators:
                obj.restart_animator()
            for obj in self.list_animators:
                obj.restart_animator()

        except Exception as a:
            print(a)

    # 图像图标
    @staticmethod
    def image_icon(ico, k, pix=None):
        if k in ico and pix is None:
            icon_data = base64.b64decode(ico[k])
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(icon_data))
            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            icon.addPixmap(pixmap, QIcon.Disabled)
            return icon
        elif pix:
            icon_data = base64.b64decode(ico[k])
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(icon_data))
            return pixmap

    # 更新图标
    def update_ico(self):
        # 定义控件与键名的映射关系（键名对应 JSON 中的键，控件对应目标 QPushButton）
        control_mapping = {
            "info": self.music.info_Button,
            "set": self.music.set_Button,
            "close": self.music.EXIT_Button,

            "music file": self.music.song_Button,
            "like folder": self.music.collect_Button,
            "add music": self.music.import_music_Button,
            "import2": self.music.import_playlist_Button,

            "interrupt": self.music.interrupt_Button,
            "previous": self.music.up_Button,
            "retreat": self.music.up_time_Button,
            "forward": self.music.down_time_Button,
            "next": self.music.down_Button,
            "like": self.music.like_Button,
            "clock": self.music.clock_Button,
            "add": self.music.theme_up_Button,
            "edit": self.music.theme_edit_Button,
            "import": self.music.theme_import_Button,
            "delete": self.music.theme_down_Button,

        }

        # 重新读取资源
        self.resources_ico = self.music_file_service.json_all_read(self.pathfile_resources)

        for key, button in control_mapping.items():
            button.setIcon(self.image_icon(self.resources_ico, key))

        # 单独设置冲突的按钮
        self.music.font_import_Button.setIcon(self.image_icon(self.resources_ico, "import"))
        self.music.font_down_Button.setIcon(self.image_icon(self.resources_ico, "delete"))

        # 单独设置特殊控件图标 纯数据
        # 标签
        self.music.donation_Label_2.setPixmap(self.image_icon(self.resources_ico, "donation", True))
        # 下拉列表
        #self.music.theme_comboBox.setStyleSheet(self.music_acrylic.Theme.combobox_ico(self.theme_background,self.theme_background,self.image_icon(self.resources_ico, "down",True)))

        # 播放按钮
        if self.music_play_state:
            self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "play"))
        else:
            self.music.play_Button.setIcon(self.image_icon(self.resources_ico, "stop"))

        # 播放模式
        if self.path_play_mode == "Random Play":  # 随机播放
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "random play"))
            self.music_play_mode = 1
        elif self.path_play_mode == "Loop Play":  # 循环播放
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "loop play"))
            self.music_play_mode = 2
        elif self.path_play_mode == "Single Loop":  # 单曲循环
            self.music.state_Button.setIcon(self.image_icon(self.resources_ico, "single loop"))
            self.music_play_mode = 3

        # 音量
        if self.music.drawer_horizontalSlider.value() == 0:
            self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 0"))
        if 1 <= self.music.drawer_horizontalSlider.value() <= 10:
            self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 1"))
        if 10 <= self.music.drawer_horizontalSlider.value() <= 50:
            self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 2"))
        if 50 <= self.music.drawer_horizontalSlider.value() <= 70:
            self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 3"))
        if 70 <= self.music.drawer_horizontalSlider.value() <= 100:
            self.music.volume_Button.setIcon(self.image_icon(self.resources_ico, "volume 4"))

    # 更新主题数据
    def update_theme_data(self):

        self.update_theme(self.music.theme_comboBox.currentText())
        # 修改资源颜色
        self.music_service.save_colored_images_back_to_json(self.pathfile_resources, self.theme_color)
        self.update_ico()




    # 修复的ComboBox
    def New_ComboBox(self):
        for combo_box in self.music.MusicPlayer_Bottom_Widget.findChildren(QComboBox):
            if combo_box is not None:
                combo_box.setView(QListView())

    # 初始化淡入淡出设置
    def init_fade_in_out(self):
        # 读取淡入淡出时长
        self.fade_in_time = self.music_file_service.amc_read(self.path_config_folder + "fade in.amc")
        self.fade_out_time = self.music_file_service.amc_read(self.path_config_folder + "fade out.amc")

        self.music.fade_in_horizontalSlider.setValue(int(float(self.fade_in_time) * 10))
        self.music.fade_in_text_Label.setText(self.fade_in_time)

        self.music.fade_out_horizontalSlider.setValue(int(float(self.fade_out_time) * 10))
        self.music.fade_out_text_Label.setText(self.fade_out_time)

    # 初始化音量抽屉
    def init_drawer(self):
        self.music.drawer_widget.stackUnder(self.music.Play_Main_Widget)  # 抽屉放在菜单下面
        self.music_player.set_volume(int(self.music_file_service.amc_read(self.path_config_folder + "select volume.amc"))/100)
        self.music.drawer_horizontalSlider.setValue(int(self.select_volume))
        # 激活一次
        self.drawer_music()

    # 初始化封面按钮
    def init_cover_button(self):
        self.cover_button = Widgets.ImageButton()
        self.cover_button.setObjectName("cover_button")
        self.music.horizontalLayout_music.insertWidget(0,self.cover_button)
        self.music.music_name_Label.setAttribute(Qt.WA_TransparentForMouseEvents)

    # 初始化歌词模块
    def init_lyric_model(self):
        try:
            self.lyric_widget = self.music_lyric_widget.LyricWidget(self.music.music_lyric_Label,
                                                                    self.music.Center_Info_Page_Widget)
            # 连接简易歌词
            self.lyric_widget.lyricLineChanged.connect(lambda x: self.music.music_lyric_Label.setText(x))


            # self.desktop_lyric = DesktopLyricWidget.DesktopLyricWindow()
            # self.desktop_lyric.show()

            # 连接桌面歌词
            # self.lyric_widget.lyricChanged.connect(lambda x: self.desktop_lyric.set_text(x))

            self.lyric_widget.setGeometry(370, 0, 0, 0)
            self.lyric_widget.set_custom_size(1000, 730)
            self.lyric_widget.bind_time_label()
            self.lyric_widget.setObjectName("lyric_widget")

        except Exception as a:
            print("初始化歌词 发生错误", a)

    # 初始化自定义控件
    def init_customize_widget(self):
        # 动画
        # 按钮动画
        self.switch_button_animation = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_button_animation.show()
        self.switch_button_animation.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "button animation.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_button_animation, 1, 2)

        # 堆叠窗口动画
        self.switch_stacked_widget = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_stacked_widget.show()
        self.switch_stacked_widget.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "stacked widget.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_stacked_widget, 2, 2)

        # 滑动条动画
        self.switch_slider_animation = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_slider_animation.show()
        self.switch_slider_animation.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "slider animation.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_slider_animation, 3, 2)

        # 弹性滚动动画
        self.switch_elastic_rolling = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_elastic_rolling.show()
        self.switch_elastic_rolling.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "elastic rolling.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_elastic_rolling, 4, 2)

        # 列表弹性滚动动画
        self.switch_list_elastic_rolling = Switch.SwitchButton(f"{self.theme_color}",
                                                               self.music.scrollAreaWidgetContents)
        self.switch_list_elastic_rolling.show()
        self.switch_list_elastic_rolling.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "list elastic rolling.amc",
                                                        str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_list_elastic_rolling, 5, 2)

        # 列表项动画
        self.switch_list_item = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_list_item.show()
        self.switch_list_item.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "list item.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_list_item, 6, 2)

        # 下拉列表动画
        self.switch_combobox_animation = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_combobox_animation.show()
        self.switch_combobox_animation.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_animation_folder + "combobox animation.amc", str(x)))
        self.music.gridLayout_animation.addWidget(self.switch_combobox_animation, 7, 2)

        # 开关
        # 列表项图标
        self.switch_listitem_ico = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_listitem_ico.show()
        self.switch_listitem_ico.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_switch_folder + "item ico.amc", str(x)))
        self.music.gridLayout_switch.addWidget(self.switch_listitem_ico, 1, 2)

        # 控件提示
        self.switch_widgets_tip = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_widgets_tip.show()
        self.switch_widgets_tip.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_switch_folder + "widget tip.amc", str(x)))
        self.music.gridLayout_switch.addWidget(self.switch_widgets_tip, 2, 2)

        # 初始化开关状态
        self.animation_button = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "button animation.amc"))
        self.animation_tacked_widget = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "stacked widget.amc"))
        self.animation_slider_animation = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "slider animation.amc"))
        self.animation_elastic_rolling = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "elastic rolling.amc"))
        self.animation_list_elastic_rolling = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "list elastic rolling.amc"))
        self.animation_list_item = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "list item.amc"))
        self.animation_combobox_animation = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_animation_folder + "combobox animation.amc"))

        if self.animation_button:
            self.switch_button_animation.setOn(True)
        if self.animation_tacked_widget:
            self.switch_stacked_widget.setOn(True)
        if self.animation_slider_animation:
            self.switch_slider_animation.setOn(True)
        if self.animation_elastic_rolling:
            self.switch_elastic_rolling.setOn(True)
        if self.animation_list_elastic_rolling:
            self.switch_list_elastic_rolling.setOn(True)
        if self.animation_list_item:
            self.switch_list_item.setOn(True)
        if self.animation_combobox_animation:
            self.switch_combobox_animation.setOn(True)

        # 项目图片开关
        self.switch_item_ico = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "item ico.amc"))
        # 控件提示开关
        self.switch_widget_tip = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "widget tip.amc"))
        if self.switch_item_ico:
            self.switch_listitem_ico.setOn(True)
        if self.switch_widget_tip:
            self.switch_widgets_tip.setOn(True)

    # 初始化歌词设置
    def init_lyric_set(self):
        # 歌词显示翻译
        self.switch_lyric_translation = Switch.SwitchButton(f"{self.theme_color}", self.music.scrollAreaWidgetContents)
        self.switch_lyric_translation.show()
        self.switch_lyric_translation.toggled.connect(
            lambda x: self.music_file_service.amc_write(self.path_switch_folder + "lyric translation.amc", str(x)))
        self.music.gridLayout_lyric.addWidget(self.switch_lyric_translation, 1, 2)

        # 歌词翻译开关
        self.switch_lyric = self.music_file_service.str_bool(
            self.music_file_service.amc_read(self.path_switch_folder + "lyric translation.amc"))
        if self.switch_lyric:
            self.switch_lyric_translation.setOn(True)

        # 歌词最大翻译
        self.lyric_line = int(self.music_file_service.amc_read(self.path_config_folder + "lyric line.amc"))
        self.music.lyrci_comboBox.setCurrentIndex(self.lyric_line)
        self.music.lyrci_comboBox.activated.connect(
            lambda: self.music_file_service.amc_write(self.path_config_folder + "lyric line.amc",
                                                      str(self.music.lyrci_comboBox.currentIndex())))

    # 初始化定时器
    def init_timer(self):
        self.music_timer = Timer.CountdownTimer()
        self.music_timer.setWindowTitle("定时器")
        self.music_timer.resize(450, 350)
        self.music_timer.hide()

        # 绑定停止 三元表达式
        self.music_timer.finished.connect(lambda: self.play_music_file() if not self.music_play_state else None)

    # 初始化播放列表
    def init_play_list(self):
        # 读取保存的歌曲
        path_music = self.music_file_service.amc_read(self.path_config_folder + 'select music.amc')

        # 更新选择歌单
        self.path_play_playlist = self.music_file_service.amc_read(self.path_config_folder + 'select playlist.amc')

        # 在列表中搜索歌曲
        path_list = self.music_service.find_list_indices(self.music.music_song_ListWidget, path_music)

        # 读取第一个搜索结果
        self.play_list_element = path_list[0]

        # 应用更新
        self.play_list = self.music_folder_service.get_all_files(self.path_playlist_folder + self.path_play_playlist)
        # 初始化播放线程
        self.thread_play = self.music_thread.SliderUpdater(self.music.music_Progressbar,
                                                           self.music.music_Progressbar.maximum(),
                                                           self.music.music_Progressbar.value(),
                                                           self.music_duration_min)

        # 初始化播放的音乐
        self.music_player.set_load(self.path_playlist_folder + self.path_playlist + '/' +
                                   self.play_list[self.play_list_element])  # 分离播放

    # 初始化实验性内容 视觉实验室
    def init_experimental(self):
        GlobalBlur(self.Main.winId(), Dark=True, QWidget=self)
        self.Main.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

    # 自检
    def Inspector(self):
        try:
            # 读取选择的歌单
            select_playlist = self.music_file_service.amc_read(self.path_config_folder + "select playlist.amc")
            # 配置文件中选择的歌单不存在
            if not os.path.exists(self.path_playlist_folder + select_playlist) or select_playlist == "":
                # 选择文件夹中第一个文件夹
                new_folder = self.music_folder_service.get_first_subdirectory(self.path_playlist_folder)
                # 写入纠正后的歌单
                self.music_file_service.amc_write(self.path_config_folder + "select playlist.amc", new_folder)
                # 应用纠正
                self.path_playlist = new_folder

            # 读取选择的歌曲
            select_music = self.music_file_service.amc_read(self.path_config_folder + "select music.amc")
            # 配置文件中选择的文件不存在
            if not os.path.exists(self.path_playlist_folder + self.path_playlist + '/' + select_music + '.mp3'):
                # 选择文件夹中第一个文件
                new_file = self.music_folder_service.get_first_filename(self.path_playlist_folder + self.path_playlist)
                # 处理mp3后缀
                new_file = self.music_service.remove_mp3_extension(new_file)
                # 写入纠正后的歌曲
                self.music_file_service.amc_write(self.path_config_folder + "select music.amc", new_file)
                # 应用纠正
                self.path_music = new_file

            # 读取选择的播放时间
            select_playtime = self.music_file_service.ams_read("Config/Statistics/song time.ams")
            # 配置文件中的数据错误
            if select_playtime is None or select_playtime == "":
                # 恢复默认值
                playtime = "0"
                # 写入纠正
                self.music_file_service.ams_write("Config/Statistics/song time.ams", playtime)

            # 读取选择的播放次数
            select_play_count = self.music_file_service.ams_read(self.path_statistics + "player song count.ams")
            # 配置文件中的数据错误
            if select_play_count is None or select_play_count == "":
                # 恢复默认值
                play_count = "0"
                # 写入纠正
                self.music_file_service.ams_write(self.path_statistics + "player song count.ams", play_count)

            if self.music_inspector.is_folder_empty(self.path_playlist_folder):
                print("没有歌单和歌曲")

        except Exception as a:
            print("自检失败", a)


    # 主窗口
    def MainWindow(self):
        self.Main.setMinimumSize(1390, 890)  # 设置窗口最小尺寸
        self.Main.setMaximumSize(1390, 890)  # 设置窗口最大尺寸
        # 保留最小化和关闭按钮，移除最大化按钮
        flags = (Qt.Window |
                 Qt.WindowMinimizeButtonHint |
                 Qt.WindowCloseButtonHint)
        self.Main.setWindowFlags(flags)
        #self.Main.setWindowFlags(self.Main.windowFlags() | Qt.FramelessWindowHint)  # 无边框窗口


        # 先进行自检
        self.Inspector()

        # 初始化音量抽屉
        self.init_drawer()

        # 更新进度条
        self.music_progress_update()

        # 绑定实时滑动条更新
        self.music.music_Progressbar.sliderMoved.connect(self.music_update_time)
        self.music.music_Progressbar.sliderReleased.connect(self.music_update_time_play)
        self.music.drawer_horizontalSlider.valueChanged.connect(self.drawer_music)
        self.music.drawer_horizontalSlider.sliderReleased.connect(self.update_drawer_music)

        self.music.fade_in_horizontalSlider.valueChanged.connect(
            lambda: self.music.fade_in_text_Label.setText(str(self.music.fade_in_horizontalSlider.value() / 10)))
        self.music.fade_in_horizontalSlider.sliderReleased.connect(lambda: self.update_music_player("in"))
        self.music.fade_out_horizontalSlider.valueChanged.connect(
            lambda: self.music.fade_out_text_Label.setText(str(self.music.fade_out_horizontalSlider.value() / 10)))
        self.music.fade_out_horizontalSlider.sliderReleased.connect(lambda: self.update_music_player("out"))

        # 绑定滑动条快进快退
        self.music.up_time_Button.clicked.connect(self.music_down_time)
        self.music.down_time_Button.clicked.connect(self.music_up_time)

        # 设置滑动条跳转
        self.music_widget_service.enable_click_to_seek(self.music.music_Progressbar)
        self.music_widget_service.enable_click_to_seek(self.music.drawer_horizontalSlider)
        self.music_widget_service.enable_click_to_seek(self.music.fade_out_horizontalSlider)
        self.music_widget_service.enable_click_to_seek(self.music.fade_in_horizontalSlider)

        # 更新播放模式按钮
        self.play_update_mode()

        # 更新歌词
        self.update_lyric()

        # 更新热键
        self.update_hotkey()
        # 更新全局钩子
        self.update_hook()

        # 更新淡入淡出时长
        self.init_fade_in_out()

        # 控件优化处理
        # 断掉按钮的默认键盘捕捉 滚动画布的左右键 滑动条的方向键响应 行编辑框的输入方式
        self.music_widget_service.disable_button_keyboard_capture(self.music.MusicPlayer_Bottom_Widget)
        self.music_widget_service.disable_horizontal_scroll_keys(self.music.set_scrollArea)
        self.music_widget_service.install_slider_filter(self.music.music_Progressbar)
        self.music_widget_service.install_slider_filter(self.music.drawer_horizontalSlider)
        self.music_widget_service.install_slider_filter(self.music.fade_out_horizontalSlider)
        self.music_widget_service.install_slider_filter(self.music.fade_in_horizontalSlider)

        # 禁用滑动条的鼠标滑轮操作
        self.music.music_Progressbar.wheelEvent = lambda event: event.ignore()
        # 断掉所有下拉列表的鼠标滑轮操作
        for widget in self.music.MusicPlayer_Bottom_Widget.findChildren(QComboBox):
            widget.wheelEvent = lambda event: event.ignore()

        # 低灵敏滑动条
        self.music.drawer_horizontalSlider.wheelEvent = lambda event: self.music_widget_service.handle_slider_wheel_event(self.music.drawer_horizontalSlider, event)
        self.music.fade_out_horizontalSlider.wheelEvent = lambda event: self.music_widget_service.handle_slider_wheel_event(self.music.fade_out_horizontalSlider, event)
        self.music.fade_in_horizontalSlider.wheelEvent = lambda event: self.music_widget_service.handle_slider_wheel_event(self.music.fade_in_horizontalSlider, event)

        # 绑定画布按钮
        self.music.info_Button.clicked.connect(lambda: self.Music_Update("Center_Info"))
        self.music.set_Button.clicked.connect(lambda: self.Music_Update("Center_Set"))
        self.music.song_Button.clicked.connect(lambda: self.Music_Update("Music_Song"))
        self.music.collect_Button.clicked.connect(lambda: self.Music_Update("Music_Collect"))

        # 绑定开始 播放按钮
        self.music.play_Button.clicked.connect(self.play_music_file)

        # 绑定上一首 下一首按钮
        self.music.up_Button.clicked.connect(self.up_music_file)
        self.music.down_Button.clicked.connect(self.down_music_file)

        # 绑定播放模式按钮
        self.music.state_Button.clicked.connect(self.play_mode)
        # 绑定中断播放按钮
        self.music.interrupt_Button.clicked.connect(self.music_interrupt)

        # 绑定退出按钮
        self.music.EXIT_Button.clicked.connect(self.music_service.EXIT)

        # 绑定歌曲列表双击按钮
        self.music.music_song_ListWidget.itemDoubleClicked.connect(self.list_play_music_file)
        # 绑定歌单列表单击按钮
        self.music.music_playlist_ListWidget.clicked.connect(self.select_playlist_folder)

        # 绑定收藏列表单击双击按钮
        self.music.music_collect_ListWidget.clicked.connect(self.select_music_file_like)
        self.music.music_collect_ListWidget.itemDoubleClicked.connect(self.list_play_music_like)

        # 绑定导入歌曲歌单按钮
        self.music.import_music_Button.clicked.connect(self.import_song)
        self.music.import_playlist_Button.clicked.connect(self.import_playlist)

        # 绑定轨道信息按钮
        self.music.senior_info_Button.clicked.connect(self.music_update_senior_info)

        # 绑定 导入 删除 字体按钮
        self.music.font_import_Button.clicked.connect(self.import_font)
        self.music.font_down_Button.clicked.connect(self.del_font)
        # 绑定 新建 编辑 导入 删除主题按钮
        self.music.theme_import_Button.clicked.connect(self.import_theme)
        self.music.theme_up_Button.clicked.connect(self.new_theme)
        self.music.theme_down_Button.clicked.connect(self.del_theme)

        # 绑定查看许可证按钮 记事本 阅读器
        self.music.view_license_Button.clicked.connect(lambda: self.reader.show_notepad("LICENSE"))
        # 绑定清理按钮
        self.music.clear_cover_cache_Button.clicked.connect(self.clear_cover_cache)
        self.music.clear_lyric_cache_Button.clicked.connect(self.clear_lyric_cache)
        self.music.clear_song_thumbnail_cache_Button.clicked.connect(self.clear_song_thumbnail_cache)
        self.music.clear_song_all_Button.clicked.connect(self.clear_song_all)
        self.music.clear_data_all_Button.clicked.connect(self.clear_data_all)
        self.music.zeroing_statistical_data_Button.clicked.connect(self.zero_data)

        # 绑定选择现有许可证按钮
        self.music.select_lic_Button.clicked.connect(self.select_path_lic)
        # 绑定选择许可证文件按钮
        self.music.select_lic_file_Button.clicked.connect(self.select_file_lic)
        # 注销当前许可证
        self.music.logout_lic_Button.clicked.connect(self.lic_logout)

        # 连接歌曲列表菜单信号
        self.music_menu_signals_song = self.music_menu.setup_listwidget_context_menu(self.music.music_song_ListWidget)
        self.music_menu_signals_song.song_path.connect(
            lambda: self.music_explorer.open_in_explorer(os.path.abspath(os.path.abspath(self.path_playlist_folder+self.path_playlist+"\\"+self.music.music_song_ListWidget.currentItem().text()+".mp3"))))
        self.music_menu_signals_song.song_play.connect(self.list_play_music_file)
        self.music_menu_signals_song.song_update.connect(self.music_update_song)
        self.music_menu_signals_song.song_import.connect(self.import_song)
        self.music_menu_signals_song.song_rename.connect(self.song_rename)
        self.music_menu_signals_song.song_export.connect(self.export_song)
        self.music_menu_signals_song.song_del.connect(self.delete_listwidget_song)

        # 连接歌单列表菜单信号
        self.music_menu_signals_playlist = self.music_menu.setup_listwidget_context_menu_playlist(
            self.music.music_playlist_ListWidget)
        self.music_menu_signals_playlist.playlist_path.connect(
            lambda: self.music_explorer.open_in_explorer(os.path.abspath(os.path.abspath(self.path_playlist_folder+self.path_playlist+"\\"+self.music.music_song_ListWidget.currentItem().text()+".mp3"))))
        self.music_menu_signals_playlist.playlist_skip.connect(self.select_playlist_folder)
        self.music_menu_signals_playlist.playlist_update.connect(self.music_update_playlist)
        self.music_menu_signals_playlist.playlist_import.connect(self.import_playlist)
        self.music_menu_signals_playlist.playlist_new.connect(self.playlist_new_folder)
        self.music_menu_signals_playlist.playlist_rename.connect(self.playlist_rename)
        self.music_menu_signals_playlist.playlist_export.connect(self.export_playlist)
        self.music_menu_signals_playlist.playlist_del.connect(self.delete_listwidget_playlist)

        # 绑定热键选择按钮
        self.music.select_key_Button.clicked.connect(lambda: self.select_hot_key("play.amc"))
        self.music.select_key_Button_2.clicked.connect(lambda: self.select_hot_key("playlist.amc"))
        self.music.select_key_Button_3.clicked.connect(lambda: self.select_hot_key("time up.amc"))
        self.music.select_key_Button_4.clicked.connect(lambda: self.select_hot_key("time down.amc"))
        self.music.select_key_Button_5.clicked.connect(lambda: self.select_hot_key("music up.amc"))
        self.music.select_key_Button_6.clicked.connect(lambda: self.select_hot_key("music down.amc"))
        self.music.select_key_Button_7.clicked.connect(lambda: self.select_hot_key("music like.amc"))

        # 绑定全局钩子按钮
        self.music.select_hook_Button.clicked.connect(lambda: self.select_hook("play.amc"))
        self.music.select_hook_Button_2.clicked.connect(lambda: self.select_hook("time up.amc"))
        self.music.select_hook_Button_3.clicked.connect(lambda: self.select_hook("time down.amc"))
        self.music.select_hook_Button_4.clicked.connect(lambda: self.select_hook("music up.amc"))
        self.music.select_hook_Button_5.clicked.connect(lambda: self.select_hook("music down.amc"))

        # 绑定音量抽屉
        self.music.volume_Button.clicked.connect(lambda: self.volume_drawer.toggle())

        # 绑定喜欢
        self.music.like_Button.clicked.connect(self.update_like)

        # 绑定定时器
        self.music.clock_Button.clicked.connect(lambda: self.music_timer.show())

        # 绑定字体下拉框
        self.music.font_comboBox.activated.connect(lambda: self.update_font(self.music.font_comboBox.currentIndex()))
        # 绑定主题下拉框
        self.music.theme_comboBox.activated.connect(self.update_theme_data)

        self.New_ComboBox()

        # 初始化自定义控件
        self.init_customize_widget()

        # 初始化歌词设置
        self.init_lyric_set()

        # 设置图标
        self.app.setWindowIcon(QIcon(self.app_ico))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.app_id)
        # 设置标题
        self.Main.setWindowTitle(self.app_title)

        # 更新字体 为了能兼容自定义控件 最后更新
        self.update_font()

        # 更新主页画布
        self.Music_Update("Center_Homepage")
        # 更新歌单歌曲
        self.music_update_song()
        self.music_update_playlist()
        # 初始化播放列表
        self.init_play_list()

        # 更新喜欢
        self.update_like_check()

        # 初始化定时器
        self.init_timer()

        # 添加提示
        if self.switch_widget_tip:
            self.tip()

        # 添加列表拖入支持
        self.music_widget_service.ListWidgetDragDropHelper(self.music.music_song_ListWidget).filesDropped.connect(lambda file: self.drag_song(file))
        self.music_widget_service.ListWidgetDragDropHelper(self.music.music_playlist_ListWidget).filesDropped.connect(lambda playlist: self.drag_playlist(playlist))

        # 更新主题
        self.update_theme(self.select_theme)

        # 更新动画
        self.update_animation()

        # 更新图标
        self.update_ico()

        # 显示窗口
        self.Main.show()

        # 当窗口关闭后会退出程序
        sys.exit(self.app.exec())


if __name__ == '__main__':
    m = MainUI()
    m.MainWindow()

# 模仿洛雪 任务栏显示小按钮 播放暂停上下 播放进度条 暂停时变颜色 windows api