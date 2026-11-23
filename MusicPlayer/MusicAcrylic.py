class Theme(object):


    @staticmethod
    def theme(color="30,200,150",background="30,30,30"):
        # 读取文字颜色
        # color = "85,150,255"
        # color = "180,220,240"
        # color = music_service.amt_read(f"Theme/{theme_config}.amt", 3)

        # 读取背景颜色
        # background = "160,210,240"
        # background = music_service.amt_read(f"Theme/{theme_config}.amt", 4)

        bg = "0,0,0"
        a = "0.9"
        aa = "0.4"

        # 透明强度
        alpha = 0.5

        theme = f'''
                                /* 全局样式 */
                                * {{
                                outline: none; /* 去除焦点虚线 */
                                }}
                                
                                
                                /* 主界面 背景界面*/
                                #MusicPlayer_Bottom_Widget {{
                                background-color: rgba({bg},{aa});
                                }}


                                /* 子界面 背景界面*/
                                #Song_Menu_Widget,
                                #Play_Main_Widget,
                                #Center_set_Widget,
                                #Center_Homepage_Page_Widget,
                                #Center_Details_Page_Widget,
                                #Center_Info_Page_Widget,
                                #drawer_widget
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
                                

                                QLabel
                                {{
                                background-color:transparent;
                                color:rgb({color});
                                border-radius:5px;
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
                                    background: rgba({color},0.5); /*滑块颜色*/
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
                                QTextEdit {{
                                    background-color: rgba({background},{alpha}); /* 设置背景颜色为浅灰色 */
                                    color:rgba({color});           /* 设置文本颜色为深灰色 */
                                    border-radius: 5px;        /* 设置边框圆角为5像素 */
                                    padding: 10px;             /* 设置内边距为10像素 */
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                                }}


                                QPushButton
                                {{
                                background-color:rgb({background},0.3);
                                color:rgb({color});
                                border-radius:5px
                                }}
                                QPushButton:hover
                                {{	/*鼠标悬浮时*/
                                    background-color: rgba({color},0.3);
                                }}
                                QPushButton::pressed
                                {{
                                background-color:rgb({color},0.4);
                                color:rgb({color});
                                }}
                                QPushButton:disabled
                                {{
                                background-color:rgb({color},0.1);
                                color:rgb({color});
                                }}
                                
                                
                                /*图标按钮*/
                                #play_Button,
                                #up_time_Button,
                                #down_time_Button,
                                #up_Button,
                                #down_Button,
                                #state_Button,
                                #volume_Button,
                                #clock_Button,
                                #like_Button,
                                #interrupt_Button
                                {{
                                background-color:rgb(0,0,0,0);
                                color:rgb({color});
                                }}
                                
                                QPushButton:disabled
                                {{
                                color:rgb({color});
                                }}
                                
                                QPushButton::pressed
                                {{
                                color:rgb({color});
                                }}
                                
                                /* 封面按钮 */
                                #cover_button
                                {{
                                background: transparent;
                                border: none;
                                }}



                                QListWidget {{
                                    border-radius:5px;
                                    background-color: rgba({background},{alpha}); /* 设置QListWidget的背景色 */
                                }}
                                QListWidget::item {{
                                    background-color: rgba({background},0); /* 设置QListWidgetItem的背景色 */
                                    color:rgb({color}); /* 设置文字颜色 */
                                    padding: 5px; /* 设置每个项的内边距 */
                                    border-radius:5px;
                                }}
                                QListWidget::item:selected {{
                                    background-color: rgba({color},0.2); /* 设置选中项的背景色 */
                                    color:rgb({color}); /* 设置选中项的文字颜色 */
                                }}
                                QListWidget::item:hover {{
                                    background-color: rgba({color},0.1); /* 设置鼠标悬停时项的背景色 */
                                    color:rgb({color}); /* 设置选中项的文字颜色 */
                                }}



                                QScrollBar:vertical {{
                                    border: none; /*无边框*/
                                    background:rgb(0, 0, 0,0); /*透明背景*/
                                    width:8px; /*宽度*/
                                }}
                                QScrollBar::handle:vertical {{
                                    background: rgba({color},0.5); /*滑块颜色*/
                                    min-height: 20px; /*手柄最小高度*/
                                    max-height: 20px; /*手柄最大高度*/
                                    margin: 0 0px 0 0px; /*无外边框*/
                                    border-radius: 3.5px; /*圆角*/
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
                                    background: rgba({color}, 0.2);
                                    border-radius: 2px;
                                }}
                                /* 加粗的圆形滑块手柄 */
                                QSlider::handle:horizontal {{
                                    background: rgb({color},0);
                                    width: 10px;                  /* 加宽手柄 */
                                    border-radius: 2px;          /* 完全圆形 */
                                }}
                                /* 滑动区域 */
                                QSlider::sub-page:horizontal {{
                                    background: rgba({color}, 0.5);
                                    height: 4px;
                                    border-radius: 2px;
                                }}
                                QSlider::add-page:horizontal {{
                                    background: rgba({color}, 0.1);
                                    height: 4px;
                                    border-radius: 2px;
                                }}
                                
                                
                                QMenu {{
                                    background-color: rgba({background},{alpha});
                                    border-radius: 5px;       /* 控制菜单整体圆角弧度 */
                                    font-weight: bold;
                                }}
                                QMenu::item {{
                                    padding: 5px 15px;
                                    color: rgb({color});
                                    border-radius: 5px;        /* 菜单项的圆角设置 */
                                }}
                                QMenu::item:selected {{
                                    background-color: rgba({color},0.2);
                                    color:rgb({color});
                                }}
                                QMenu::separator {{
                                    background: rgb({color},0.2);
                                }}
                                
                            
                                
                                QLineEdit
                                {{
                                    background-color: rgb({background},0.3);
                                    color: rgb({color});
                                    border-radius: 5px;
                                    selection-color:rgba({background});/* 选择的前景色 */
                                    selection-background-color:rgba({color},{alpha}) /* 选择的背景色 */
                                }}
                                QLineEdit:disabled
                                {{
                                    background-color: rgb({background},0.1);
                                    color: rgb({color});
                                    border-radius: 5px;
                                }}
                                QLineEdit:hover
                                {{
                                    background-color: rgba({color},0.3);
                                }}
                                QLineEdit:focus
                                {{
                                    background-color: rgb({background},0.4);
                                    border-bottom: 2px solid rgb({color});
                                }}
                                
                                
                                QComboBox {{
                                    border: 1px solid transparent;
                                    background-color: rgba({background},0.3);
                                    color: rgba({color});
                                    border-radius: 5px;
                                    padding: 5px;
                                    border: none;
                                }}
                                QComboBox:hover {{
                                    background-color: rgba({color},0.3);
                                }}            
                                QComboBox:disabled {{
                                    background-color: rgba({color},0.1);
                                    color: rgba({color},0.5);
                                }}
                                QComboBox::drop-down {{
                                    width: 20px;
                                    border-left: none;
                                    image: url(:/ico/MusicIco/down.png);
                                }}
                                QComboBox QAbstractItemView {{
                                    background: rgba({background});
                                    color: rgba({color});
                                    outline: none;
                                    border: none;
                                }}
                                QComboBox QAbstractItemView::item {{
                                    height: 20px;      /* 固定高度 */
                                    background-color: rgba({background},0.3);
                                    color: rgba({color});
                                    border-radius: 5px;
                                    padding: 5px;
                                    border: none;
                                }}
                                QComboBox QAbstractItemView::item:hover {{ 
                                    background: rgba({color},0.3);
                                    color: rgba({color});
                                }}
                                QComboBox::pressed{{
                                    background-color: rgba({color},0.3);
                                    color: rgb({background});
                                }}
                                '''

        return theme

