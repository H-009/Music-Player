from . import MusicFileService


class Theme(object):

    @staticmethod
    def theme(config):
        # 读取选择的主题配置
        theme_config = config

        music_service = MusicFileService

        # 读取背景图片
        image = music_service.amt_read(f"Theme/{theme_config}.amt", 2)

        # 读取文字颜色
        color = music_service.amt_read(f"Theme/{theme_config}.amt", 3)

        # 读取背景颜色
        background = music_service.amt_read(f"Theme/{theme_config}.amt", 4)

        # 读取透明强度
        alpha = music_service.amt_read(f"Theme/{theme_config}.amt", 5)

        if image == "None":
            theme = f'''

                                /* 主界面 背景界面*/
                                #MusicPlayer_Bottom_Widget {{
                                background-color: rgba({background});
                                }}



                                /* 子界面 背景界面*/
                                #Song_Menu_Widget,
                                #Playlist_Menu_Widget,
                                #Play_Main_Widget,
                                #Center_set_Widget,
                                #Center_Homepage_Page_Widget,
                                #Center_Details_Page_Widget
                                {{
                                    border-radius:5px;
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background-color:rgba({background},{alpha})
                                }}


                                /* 许可背景界面 */
                                #lic_Widget
                                {{
                                border-radius:5px;
                                border:2px solid rgb({color});
                                background-color:rgba(0,0,0,0)
                                }}


                                #Lyric_Widget
                                {{
                                    background-color:rgba(0,0,0,0)
                                }}
                                #Lyric_Widget QLabel
                                {{
                                    font-size: 15px; 
                                    color: rgb({color}); 
                                    margin: 0;
                                    background-color: rgba(0,0,0,0);
                                    border: none;
                                }}



                                QLabel
                                {{
                                background-color:transparent;
                                color:rgb({color});
                                border-radius:5px;
                                }}



                                #scrollAreaWidgetContents,
                                #scrollAreaWidgetContents_2,
                                #Center_Info_Page_Widget
                                {{  
                                    background-color:rgba(0,0,0,0)
                                }}

                                /* 滚动画布 */
                                QScrollArea {{
                                    border:none;
                                    border-radius: 5px; /* 设置QScrollArea的圆角 */
                                }}
                                QScrollArea:vertical {{
                                    /* 滚动画布的Widget */
                                    border: none; /*无边框*/
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background:rgba({background},{alpha}); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollArea::handle:vertical {{
                                    background: rgba({background},0.5); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 5px; /*圆角*/
                                }}
                                QScrollArea QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollArea QScrollBar::sub-line:vertical {{
                                    height: 0 px; /*隐藏滚动条轨道*/
                                }}





                                /* 文本编辑画布 */
                                #senior_info_textEdit {{
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background-color: rgba({background},{alpha}); /* 设置背景颜色为浅灰色 */
                                    color:rgba({color});           /* 设置文本颜色为深灰色 */
                                    border-radius: 5px;        /* 设置边框圆角为5像素 */
                                    padding: 10px;             /* 设置内边距为10像素 */
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color}) /* 选择的背景色 */
                                }}
                                QScrollBar:vertical {{
                                    border: none; /*无边框*/
                                    background:rgba(0, 0, 0,0); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollBar::handle:vertical {{
                                    background: rgba({background}); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 6px; /*圆角*/
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollBar::sub-page:vertical {{
                                    background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                                }}

                                QScrollBar::add-page:vertical {{
                                    background: rgba(0, 0, 0, 0); /*透明增加行*/
                                }}






                                QPushButton
                                {{
                                        /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({background},0.2);
                                color:rgb({color});
                                border-radius:5px}}

                                QPushButton:disabled
                                {{
                                            /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({color});
                                color:rgb({background});
                                border-radius:5px;
                                }}
                                QPushButton:hover {{	/*鼠标悬浮时*/
                                    background-color: rgba({color},0.5);
                                }}

                                QPushButton::pressed
                                {{
                                            /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({color},0.4);
                                color:rgb({color});
                                }}

                                QListWidget {{
                                            /* 添加边框 */
                                    border:2px solid rgb({color});
                                    border-radius:5px;
                                    background-color: rgba({background},{alpha}); /* 设置QListWidget的背景色 */
                                }}

                                QListWidget::item {{
                                    background-color: rgba({background}); /* 设置QListWidgetItem的背景色 */
                                    color:rgb({color}); /* 设置文字颜色 */
                                    padding: 5px; /* 设置每个项的内边距 */
                                }}

                                QListWidget::item:selected {{
                                    background-color: rgb({color}); /* 设置选中项的背景色 */
                                    color:rgb({background}); /* 设置选中项的文字颜色 */
                                }}

                                QListWidget::item:hover {{
                                    background-color: rgba({color}); /* 设置鼠标悬停时项的背景色 */
                                    color:rgb({background}); /* 设置选中项的文字颜色 */
                                }}

                                QScrollBar:vertical {{
                                    border: none; /*滑块背景无边框*/
                                    background:rgb(0, 0, 0,0); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollBar::handle:vertical {{
                                    background: rgba({color}); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 6px; /*圆角*/
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollBar::sub-line:vertical {{
                                    height: 0 px; /*隐藏滚动条轨道*/
                                }}

                                QScrollBar::sub-page:vertical {{
                                    background: rgba(0, 0, 0,0); /*透明滚动条轨道*/
                                }}

                                QScrollBar::add-page:vertical {{
                                    background: rgba(0, 0, 0,0); /*透明增加行*/
                                }}




                                QSlider {{
                                    background-color: transparent;
                                }}
                                
                                /* 滑槽样式 - 细线设计 */
                                QSlider::groove:horizontal {{
                                    height: 4px;
                                    background: rgba(30, 200, 150, 0.2);
                                    border-radius: 2px;
                                }}
                                /* 加粗的圆形滑块手柄 */
                                QSlider::handle:horizontal {{
                                    background: rgb(30, 200, 150,0);
                                    width: 10px;                  /* 加宽手柄 */
                                    border-radius: 2px;          /* 完全圆形 */
                                }}
                                
                                /* 滑动区域 */
                                QSlider::sub-page:horizontal {{
                                    background: rgba(30, 200, 150, 0.5);
                                    height: 4px;
                                    border-radius: 2px;
                                }}
                                
                                QSlider::add-page:horizontal {{
                                    background: rgba(30, 200, 150, 0.1);
                                    height: 4px;
                                    border-radius: 2px;
                                }}



                                QLineEdit {{
                                            /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background: rgba({background}, 0.2);  /* 半透明白色背景 */
                                    border-radius: 5px;  /* 圆角效果 */
                                    color: rgb({color});  /* 文本颜色 */
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color}) /* 选择的背景色 */
                                }}

                                QLineEdit:hover {{	/*鼠标悬浮时*/
                                    background-color: rgba({background},0.3);
                                }}
                                QLineEdit:focus {{ /* 按下 */
                                    background: rgba({background}, 0.4);
                                }}
                                QLineEdit:disabled{{
                                    background: rgb({color});
                                    color: rgb({background});
                                }}
                                
                                
                                QMenu {{
                                    background-color: rgb({background});
                                    border: 2px solid rgb({color});
                                    border-radius: 5px;       /* 控制菜单整体圆角弧度 */
                                    font-weight: bold;
                                }}
                                QMenu::item {{
                                    padding: 5px 15px;
                                    color: rgb({color});
                                    border-radius: 3px;        /* 菜单项的圆角设置 */
                                }}
                                QMenu::item:selected {{
                                    background-color: rgb({color});
                                    color:rgb({background});
                                }}
                                QMenu::separator {{
                                    background: rgb({background});
                                }}
                                
                                '''

        else:
            theme = f'''

                        /* 主界面 背景界面*/
                        #MusicPlayer_Bottom_Widget {{
                        background-color: rgba(0,0,0,0);
                        }}



                        /* 子界面 背景界面*/
                        #Song_Menu_Widget,
                        #Playlist_Menu_Widget,
                        #Play_Main_Widget,
                        #Center_set_Widget,
                        #Center_Homepage_Page_Widget,
                        #Center_Details_Page_Widget
                        {{
                            border-radius:5px;
                            background-color:rgba({background},{alpha})
                        }}
                        
                        /* 许可背景界面 */
                        #lic_Widget
                        {{
                        border-radius:5px;
                        border:2px solid rgb({color});
                        background-color:rgba(0,0,0,0)
                        }}
                        
                        
                        
                        #Lyric_Widget
                        {{
                            background-color:rgba(0,0,0,0)
                        }}
                        #Lyric_Widget QLabel
                        {{
                            font-size: 15px; 
                            color: rgb({color}); 
                            margin: 0;
                            background-color: rgba(0,0,0,0);
                            border: none;
                        }}




                        QLabel
                        {{
                        background-color:transparent;
                        color:rgb({color});
                        border-radius:5px;
                        }}



                        #scrollAreaWidgetContents,
                        #scrollAreaWidgetContents_2,
                        #Center_Info_Page_Widget
                        {{
                            background-color:rgba(0,0,0,0)
                        }}

                        /* 滚动画布 */
                        QScrollArea {{
                            border:none;
                            border-radius: 5px; /* 设置QScrollArea的圆角 */
                        }}
                        QScrollArea:vertical {{
                            border: none; /*无边框*/
                            background:rgba({background},{alpha}); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollArea::handle:vertical {{
                            background: rgba({background},0.5); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 5px; /*圆角*/
                        }}
                        QScrollArea QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollArea QScrollBar::sub-line:vertical {{
                            height: 0 px; /*隐藏滚动条轨道*/
                        }}





                        /* 文本编辑画布 */
                        #senior_info_textEdit {{
                            background-color: rgba({background},{alpha}); /* 设置背景颜色为浅灰色 */
                            color:rgba({color});           /* 设置文本颜色为深灰色 */
                            border-radius: 5px;        /* 设置边框圆角为5像素 */
                            padding: 10px;             /* 设置内边距为10像素 */
                            selection-color:rgba({background});/* 选择的前景色 */
                            selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                        }}
                        QScrollBar:vertical {{
                            border: none; /*无边框*/
                            background:rgba(0, 0, 0,0); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollBar::handle:vertical {{
                            background: rgba({background}); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 6px; /*圆角*/
                        }}
                        QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollBar::sub-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                        }}

                        QScrollBar::add-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明增加行*/
                        }}






                        QPushButton
                        {{
                        background-color:rgb({background},0.2);
                        color:rgb({color});
                        border-radius:5px}}

                        QPushButton:disabled
                        {{
                        background-color:rgb({background},0.1);
                        color:rgb({color});
                        border-radius:5px;
                        }}
                        QPushButton:hover {{	/*鼠标悬浮时*/
                            background-color: rgba({background},0.3);
                        }}

                        QPushButton::pressed
                        {{
                        background-color:rgb({background},0.4);
                        color:rgb({color});
                        }}
                        




                        QListWidget {{
                            border-radius:5px;
                            background-color: rgba({background},{alpha}); /* 设置QListWidget的背景色 */
                        }}

                        QListWidget::item {{
                            background-color: rgba({background},0); /* 设置QListWidgetItem的背景色 */
                            color:rgb({color}); /* 设置文字颜色 */
                            padding: 5px; /* 设置每个项的内边距 */
                        }}

                        QListWidget::item:selected {{
                            background-color: rgba({background},0.15); /* 设置选中项的背景色 */
                            color:rgb({color}); /* 设置选中项的文字颜色 */
                        }}

                        QListWidget::item:hover {{
                            background-color: rgba({background},0.1); /* 设置鼠标悬停时项的背景色 */
                            color:rgb({color}); /* 设置选中项的文字颜色 */
                        }}





                        QScrollBar:vertical {{
                            border: none; /*无边框*/
                            background:rgb(0, 0, 0,0); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollBar::handle:vertical {{
                            background: rgba({background},0.2); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 6px; /*圆角*/
                        }}
                        QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollBar::sub-line:vertical {{
                            height: 0 px; /*隐藏滚动条轨道*/
                        }}

                        QScrollBar::sub-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                        }}

                        QScrollBar::add-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明增加行*/
                        }}


                        QSlider {{
                            background-color: transparent;
                        }}
                                
                        /* 滑槽样式 - 细线设计 */
                        QSlider::groove:horizontal {{
                            height: 4px;
                            background: rgba(30, 200, 150, 0.2);
                            border-radius: 2px;
                        }}
                        /* 加粗的圆形滑块手柄 */
                        QSlider::handle:horizontal {{
                            background: rgb(30, 200, 150,0);
                            width: 10px;                  /* 加宽手柄 */
                            border-radius: 2px;          /* 完全圆形 */
                        }}
                                
                        /* 滑动区域 */
                        QSlider::sub-page:horizontal {{
                            background: rgba(30, 200, 150, 0.5);
                            height: 4px;
                            border-radius: 2px;
                        }}
                                
                        QSlider::add-page:horizontal {{
                            background: rgba(30, 200, 150, 0.1);
                            height: 4px;
                            border-radius: 2px;
                        }}



                        QLineEdit {{
                            background: rgba({background}, 0.2);  /* 半透明白色背景 */
                            border-radius: 5px;  /* 圆角效果 */
                            color: rgb({color});  /* 文本颜色 */
                            selection-color:rgba({background});/* 选择的前景色 */
                            selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                        }}

                        QLineEdit:hover {{	/*鼠标悬浮时*/
                            background-color: rgba({background},0.3);
                        }}
                        QLineEdit:focus {{ /* 按下 */
                            background: rgba({background}, 0.4);
                        }}
                        QLineEdit:disabled{{
                            background: rgba({background},0.1);
                        }}


                        
                        
                        QMenu {{
                            background-color: rgba({background},{alpha});
                            border-radius: 5px;       /* 控制菜单整体圆角弧度 */
                            font-weight: bold;
                        }}
                        QMenu::item {{
                            padding: 5px 15px;
                            color: rgb({color});
                            border-radius: 3px;        /* 菜单项的圆角设置 */
                        }}
                        QMenu::item:selected {{
                            background-color: rgba({color},0.2);
                            color:rgb({background});
                        }}
                        QMenu::separator {{
                            background: rgb({background});
                        }}
                        
                                '''

        return theme

    @staticmethod
    def info(config):
        # 读取选择的主题配置
        theme_config = config

        music_service = MusicFileService

        # 读取主题名
        name = music_service.amt_read(f"Theme/{theme_config}.amt", 1)

        # 读取背景图片
        image = music_service.amt_read(f"Theme/{theme_config}.amt", 2)

        # 读取文字颜色
        color = music_service.amt_read(f"Theme/{theme_config}.amt", 3)

        # 读取背景颜色
        background = music_service.amt_read(f"Theme/{theme_config}.amt", 4)

        # 读取透明强度
        alpha = music_service.amt_read(f"Theme/{theme_config}.amt", 5)

        return name,image,color,background,alpha

    @staticmethod
    def apply(image,color,background,alpha):

        if image == "None":
            theme = f'''

                                /* 主界面 背景界面*/
                                #MusicPlayer_Bottom_Widget {{
                                background-color: rgba({background});
                                }}



                                /* 子界面 背景界面*/
                                #Song_Menu_Widget,
                                #Playlist_Menu_Widget,
                                #Play_Main_Widget,
                                #Center_set_Widget,
                                #Center_Homepage_Page_Widget,
                                #Center_Details_Page_Widget
                                {{
                                    border-radius:5px;
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background-color:rgba({background},{alpha})
                                }}


                                /* 许可背景界面 */
                                #lic_Widget
                                {{
                                border-radius:5px;
                                border:2px solid rgb({color});
                                background-color:rgba(0,0,0,0)
                                }}


                                #Lyric_Widget
                                {{
                                    background-color:rgba(0,0,0,0)
                                }}
                                #Lyric_Widget QLabel
                                {{
                                    font-size: 15px; 
                                    color: rgb({color}); 
                                    margin: 0;
                                    background-color: rgba(0,0,0,0);
                                    border: none;
                                }}



                                QLabel
                                {{
                                background-color:transparent;
                                color:rgb({color});
                                border-radius:5px;
                                }}



                                #scrollAreaWidgetContents,
                                #scrollAreaWidgetContents_2,
                                #Center_Info_Page_Widget
                                {{  
                                    background-color:rgba(0,0,0,0)
                                }}

                                /* 滚动画布 */
                                QScrollArea {{
                                    border:none;
                                    border-radius: 5px; /* 设置QScrollArea的圆角 */
                                }}
                                QScrollArea:vertical {{
                                    /* 滚动画布的Widget */
                                    border: none; /*无边框*/
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background:rgba({background},{alpha}); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollArea::handle:vertical {{
                                    background: rgba({background},0.5); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 5px; /*圆角*/
                                }}
                                QScrollArea QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollArea QScrollBar::sub-line:vertical {{
                                    height: 0 px; /*隐藏滚动条轨道*/
                                }}





                                /* 文本编辑画布 */
                                #senior_info_textEdit {{
                                    /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background-color: rgba({background},{alpha}); /* 设置背景颜色为浅灰色 */
                                    color:rgba({color});           /* 设置文本颜色为深灰色 */
                                    border-radius: 5px;        /* 设置边框圆角为5像素 */
                                    padding: 10px;             /* 设置内边距为10像素 */
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color}) /* 选择的背景色 */
                                }}
                                QScrollBar:vertical {{
                                    border: none; /*无边框*/
                                    background:rgba(0, 0, 0,0); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollBar::handle:vertical {{
                                    background: rgba({background}); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 6px; /*圆角*/
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollBar::sub-page:vertical {{
                                    background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                                }}

                                QScrollBar::add-page:vertical {{
                                    background: rgba(0, 0, 0, 0); /*透明增加行*/
                                }}






                                QPushButton
                                {{
                                        /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({background},0.2);
                                color:rgb({color});
                                border-radius:5px}}

                                QPushButton:disabled
                                {{
                                            /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({color});
                                color:rgb({background});
                                border-radius:5px;
                                }}
                                QPushButton:hover {{	/*鼠标悬浮时*/
                                    background-color: rgba({color},0.5);
                                }}

                                QPushButton::pressed
                                {{
                                            /* 添加边框 */
                                border:2px solid rgb({color});
                                background-color:rgb({color},0.4);
                                color:rgb({color});
                                }}



                                QListWidget {{
                                            /* 添加边框 */
                                    border:2px solid rgb({color});
                                    border-radius:5px;
                                    background-color: rgba({background},{alpha}); /* 设置QListWidget的背景色 */
                                }}

                                QListWidget::item {{
                                    background-color: rgba({background}); /* 设置QListWidgetItem的背景色 */
                                    color:rgb({color}); /* 设置文字颜色 */
                                    padding: 5px; /* 设置每个项的内边距 */
                                }}

                                QListWidget::item:selected {{
                                    background-color: rgb({color}); /* 设置选中项的背景色 */
                                    color:rgb({background}); /* 设置选中项的文字颜色 */
                                }}

                                QListWidget::item:hover {{
                                    background-color: rgba({color}); /* 设置鼠标悬停时项的背景色 */
                                    color:rgb({background}); /* 设置选中项的文字颜色 */
                                }}

                                QScrollBar:vertical {{
                                    border: none; /*滑块背景无边框*/
                                    background:rgb(0, 0, 0,0); /*透明背景*/
                                    width:12px; /*宽度*/
                                }}

                                QScrollBar::handle:vertical {{
                                    background: rgba({color}); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 6px; /*圆角*/
                                }}
                                QScrollBar::add-line:vertical {{
                                    height: 0px; /*隐藏增加行*/
                                }}

                                QScrollBar::sub-line:vertical {{
                                    height: 0 px; /*隐藏滚动条轨道*/
                                }}

                                QScrollBar::sub-page:vertical {{
                                    background: rgba(0, 0, 0,0); /*透明滚动条轨道*/
                                }}

                                QScrollBar::add-page:vertical {{
                                    background: rgba(0, 0, 0,0); /*透明增加行*/
                                }}





                                QSlider {{
                                    background-color: transparent;
                                }}
                                
                                /* 滑槽样式 - 细线设计 */
                                QSlider::groove:horizontal {{
                                    height: 4px;
                                    background: rgba(30, 200, 150, 0.2);
                                    border-radius: 2px;
                                }}
                                /* 加粗的圆形滑块手柄 */
                                QSlider::handle:horizontal {{
                                    background: rgb(30, 200, 150,0);
                                    width: 10px;                  /* 加宽手柄 */
                                    border-radius: 2px;          /* 完全圆形 */
                                }}
                                
                                /* 滑动区域 */
                                QSlider::sub-page:horizontal {{
                                    background: rgba(30, 200, 150, 0.5);
                                    height: 4px;
                                    border-radius: 2px;
                                }}
                                
                                QSlider::add-page:horizontal {{
                                    background: rgba(30, 200, 150, 0.1);
                                    height: 4px;
                                    border-radius: 2px;
                                }}



                                QLineEdit {{
                                            /* 添加边框 */
                                    border:2px solid rgb({color});
                                    background: rgba({background}, 0.2);  /* 半透明白色背景 */
                                    border-radius: 5px;  /* 圆角效果 */
                                    color: rgb({color});  /* 文本颜色 */
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color}) /* 选择的背景色 */
                                }}

                                QLineEdit:hover {{	/*鼠标悬浮时*/
                                    background-color: rgba({background},0.3);
                                }}
                                QLineEdit:focus {{ /* 按下 */
                                    background: rgba({background}, 0.4);
                                }}
                                QLineEdit:disabled{{
                                    background: rgb({color});
                                    color: rgb({background});
                                }}




                                QMenu {{
                                    background-color: rgb({background});
                                    border: 2px solid rgb({color});
                                    border-radius: 5px;       /* 控制菜单整体圆角弧度 */
                                    font-weight: bold;
                                }}
                                QMenu::item {{
                                    padding: 5px 15px;
                                    color: rgb({color});
                                    border-radius: 3px;        /* 菜单项的圆角设置 */
                                }}
                                QMenu::item:selected {{
                                    background-color: rgb({color});
                                    color:rgb({background});
                                }}
                                QMenu::separator {{
                                    background: rgb({background});
                                }}

                                '''

        else:
            theme = f'''

                        /* 主界面 背景界面*/
                        #MusicPlayer_Bottom_Widget {{
                        background-color: rgba(0,0,0,0);
                        }}



                        /* 子界面 背景界面*/
                        #Song_Menu_Widget,
                        #Play_Main_Widget,
                        #Center_set_Widget,
                        #Center_Homepage_Page_Widget,
                        #Center_Details_Page_Widget
                        {{
                            border-radius:5px;
                            background-color:rgba({background},{alpha})
                        }}

                        /* 许可背景界面 */
                        #lic_Widget
                        {{
                        border-radius:5px;
                        border:2px solid rgb({color});
                        background-color:rgba(0,0,0,0)
                        }}



                        #Lyric_Widget
                        {{
                            background-color:rgba(0,0,0,0)
                        }}
                        #Lyric_Widget QLabel
                        {{
                            font-size: 15px; 
                            color: rgb({color}); 
                            margin: 0;
                            background-color: rgba(0,0,0,0);
                            border: none;
                        }}




                        QLabel
                        {{
                        background-color:transparent;
                        color:rgb({color});
                        border-radius:5px;
                        }}



                        #scrollAreaWidgetContents,
                        #scrollAreaWidgetContents_2,
                        #Center_Info_Page_Widget
                        {{
                            background-color:rgba(0,0,0,0)
                        }}

                        /* 滚动画布 */
                        QScrollArea {{
                            border:none;
                            border-radius: 5px; /* 设置QScrollArea的圆角 */
                        }}
                        QScrollArea:vertical {{
                            border: none; /*无边框*/
                            background:rgba({background},{alpha}); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollArea::handle:vertical {{
                            background: rgba({background},0.5); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 5px; /*圆角*/
                        }}
                        QScrollArea QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollArea QScrollBar::sub-line:vertical {{
                            height: 0 px; /*隐藏滚动条轨道*/
                        }}





                        /* 文本编辑画布 */
                        #senior_info_textEdit {{
                            background-color: rgba({background},{alpha}); /* 设置背景颜色为浅灰色 */
                            color:rgba({color});           /* 设置文本颜色为深灰色 */
                            border-radius: 5px;        /* 设置边框圆角为5像素 */
                            padding: 10px;             /* 设置内边距为10像素 */
                            selection-color:rgba({background});/* 选择的前景色 */
                            selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                        }}
                        QScrollBar:vertical {{
                            border: none; /*无边框*/
                            background:rgba(0, 0, 0,0); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollBar::handle:vertical {{
                            background: rgba({background}); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 6px; /*圆角*/
                        }}
                        QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollBar::sub-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                        }}

                        QScrollBar::add-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明增加行*/
                        }}






                        QPushButton
                        {{
                        background-color:rgb({background},0.2);
                        color:rgb({color});
                        border-radius:5px}}

                        QPushButton:disabled
                        {{
                        background-color:rgb({background},0.1);
                        color:rgb({color});
                        border-radius:5px;
                        }}
                        QPushButton:hover {{	/*鼠标悬浮时*/
                            background-color: rgba({background},0.3);
                        }}

                        QPushButton::pressed
                        {{
                        background-color:rgb({background},0.4);
                        color:rgb({color});
                        }}





                        QListWidget {{
                            border-radius:5px;
                            background-color: rgba({background},{alpha}); /* 设置QListWidget的背景色 */
                        }}

                        QListWidget::item {{
                            background-color: rgba({background},0); /* 设置QListWidgetItem的背景色 */
                            color:rgb({color}); /* 设置文字颜色 */
                            padding: 5px; /* 设置每个项的内边距 */
                        }}

                        QListWidget::item:selected {{
                            background-color: rgba({background},0.15); /* 设置选中项的背景色 */
                            color:rgb({color}); /* 设置选中项的文字颜色 */
                        }}

                        QListWidget::item:hover {{
                            background-color: rgba({background},0.1); /* 设置鼠标悬停时项的背景色 */
                            color:rgb({color}); /* 设置选中项的文字颜色 */
                        }}





                        QScrollBar:vertical {{
                            border: none; /*无边框*/
                            background:rgb(0, 0, 0,0); /*透明背景*/
                            width:12px; /*宽度*/
                        }}

                        QScrollBar::handle:vertical {{
                            background: rgba({background},0.2); /*滑块颜色*/
                            min-height: 20px; /*手柄最小高度*/
                            max-height: 20px; /*手柄最大高度*/
                            margin: 0 0px 0 0px; /*无外边框*/
                            border-radius: 6px; /*圆角*/
                        }}
                        QScrollBar::add-line:vertical {{
                            height: 0px; /*隐藏增加行*/
                        }}

                        QScrollBar::sub-line:vertical {{
                            height: 0 px; /*隐藏滚动条轨道*/
                        }}

                        QScrollBar::sub-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明滚动条轨道*/
                        }}

                        QScrollBar::add-page:vertical {{
                            background: rgba(0, 0, 0, 0); /*透明增加行*/
                        }}




                        QSlider {{
                            background-color: transparent;
                        }}
                                
                        /* 滑槽样式 - 细线设计 */
                        QSlider::groove:horizontal {{
                            height: 4px;
                            background: rgba(30, 200, 150, 0.2);
                            border-radius: 2px;
                        }}
                        /* 加粗的圆形滑块手柄 */
                        QSlider::handle:horizontal {{
                            background: rgb(30, 200, 150,0);
                            width: 10px;                  /* 加宽手柄 */
                            border-radius: 2px;          /* 完全圆形 */
                        }}
                                
                        /* 滑动区域 */
                        QSlider::sub-page:horizontal {{
                            background: rgba(30, 200, 150, 0.5);
                            height: 4px;
                            border-radius: 2px;
                        }}
                                
                            QSlider::add-page:horizontal {{
                            background: rgba(30, 200, 150, 0.1);
                            height: 4px;
                            border-radius: 2px;
                        }}



                        QLineEdit {{
                            background: rgba({background}, 0.2);  /* 半透明白色背景 */
                            border-radius: 5px;  /* 圆角效果 */
                            color: rgb({color});  /* 文本颜色 */
                            selection-color:rgba({background});/* 选择的前景色 */
                            selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                        }}

                        QLineEdit:hover {{	/*鼠标悬浮时*/
                            background-color: rgba({background},0.3);
                        }}
                        QLineEdit:focus {{ /* 按下 */
                            background: rgba({background}, 0.4);
                        }}
                        QLineEdit:disabled{{
                            background: rgba({background},0.1);
                        }}




                        QMenu {{
                            background-color: rgba({background},{alpha});
                            border-radius: 5px;       /* 控制菜单整体圆角弧度 */
                            font-weight: bold;
                        }}
                        QMenu::item {{
                            padding: 5px 15px;
                            color: rgb({color});
                            border-radius: 3px;        /* 菜单项的圆角设置 */
                        }}
                        QMenu::item:selected {{
                            background-color: rgba({color},0.2);
                            color:rgb({background});
                        }}
                        QMenu::separator {{
                            background: rgb({background});
                        }}

                                '''

        return theme

