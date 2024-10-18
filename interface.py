import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QFileDialog
from PyQt5.QtGui import QIcon
from videoProc import recognize
from setting import Setting
import os
import queue
import threading


q = queue.Queue()
class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # 创建系统托盘对象
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self.app)  # 使用你的图标文件

        # 创建菜单
        self.menu = QMenu()

        # 添加菜单项
        self.show_action = QAction("Setting")
        self.exit_action = QAction("Exit")
        self.fun_dict = {}
        self.short_dict = {}
        # 将菜单项与功能连接
        self.show_action.triggered.connect(self.show_setting)
        self.exit_action.triggered.connect(self.exit)
        self.menu.addAction(self.show_action)
        self.menu.addAction(self.exit_action)

        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(self.menu)

        # 显示托盘图标
        self.tray_icon.show()
        self.recog_thread = None

    def exit(self):
        """退出应用"""
        if self.short_dict['delete'] == 1:
            folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", ".")
            os.rmdir(folder_path)
        self.tray_icon.hide()  # 隐藏托盘图标
        if self.recog_thread:
            self.recog_thread.join()
        self.app.exit()
        sys.exit()

    def run(self):
        """运行应用"""
        with open("function.txt", 'r') as f:
            for l in f.readlines():
                gesture = l.split(':')[0].replace('_', ' ')
                self.fun_dict[gesture] = l.split(':')[-1]
        with open('shortcut_setting.txt', 'r') as f:
            for l in f.readlines():
                gesture = l.split(':')[0].replace('_', ' ')
                self.short_dict[gesture] = l.split(':')[-1][:-1]
        self.recog_thread = threading.Thread(target=recognize, kwargs={'camera_device': 'test_videos/10033-vmake.mp4',
                                                                  'func_dict': self.fun_dict,
                                                                  'short_dict': self.short_dict,
                                                                  'short_time': 100})
        self.recog_thread.start()
        sys.exit(self.app.exec_())
        
    def show_setting(self):
        self.setting = Setting()
        self.setting.show()


if __name__ == "__main__":
    tray_app = TrayApp()
    tray_app.run()
