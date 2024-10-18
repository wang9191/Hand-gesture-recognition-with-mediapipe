import sys

from setting import Setting
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize your application's main window


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Setting()
    window.show()
    app.exec()