import sys
import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QSplashScreen, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime
import main_window

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.info_label = QLabel()
        self.agh_logo = QPixmap("icons/agh_logo.png")
        self.agh_logo = self.agh_logo.scaled(330, 330, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setStyleSheet("background-color: white;")
        self.main_window = main_window.MainWindow()
        self.project_label = QLabel(self)
        self.title_label = QLabel(self)

        self.main_layout = QVBoxLayout()
        self.init_ui()
        self.create_layout()
        QTimer.singleShot(5000, self.show_main)

    def show_main(self):
        self.main_window.showFullScreen()
        QTimer.singleShot(500, self.close_splash_screen)


    def paintEvent(self, event):
        painter = QPainter(self)
        x = (self.width() - self.agh_logo.width()) // 2
        y = (self.height() - self.agh_logo.height()) // 2
        painter.drawPixmap(x, y, self.agh_logo)

    def init_ui(self):
        self.project_label.setStyleSheet("color: black;"
                                      "font: 30pt 'Segoe UI';"
                                      "font-weight: bold;")

        self.title_label.setStyleSheet("color: black;"
                                      "font: 30pt 'Segoe UI';"
                                      "font-weight: bold;")
        
        self.project_label.setText("Projekt inżynierski\nTomasz Bartłomowicz")
        self.title_label.setText("Inteligentny asystent treningu pływackiego")
        self.project_label.setAlignment(Qt.AlignCenter)

    def create_layout(self):
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addStretch(15)
        self.main_layout.addWidget(self.project_label)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)
    
    def close_splash_screen(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    splash = LoadingScreen()
    splash.showFullScreen()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()