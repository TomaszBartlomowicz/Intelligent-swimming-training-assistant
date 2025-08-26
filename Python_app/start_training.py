import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer

import math
import time


class TrainingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.is_paused = False
        self.window_width = 1024
        self.window_height = 600
        self.setGeometry(100, 100, self.window_width, self.window_height)

        # Declaring buttons and labels
        self.label = QLabel("Choose training you want to start", self)
        self.training1_label = QPushButton("Training 1")
        self.training2_label = QPushButton("Training 2")
        self.training3_label = QPushButton("Training 3")
        self.training4_label = QPushButton("Training 4")
        self.training5_label = QPushButton("Training 5")
        self.training6_label = QPushButton("Training 6")
        self.buttons = [self.training1_label, self.training2_label, self.training3_label, self.training4_label,
                        self.training5_label, self.training6_label]

        self.main_layout = QVBoxLayout()
        self.init_ui()
        self.layout()


    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(0, 0, 1024, 600)
        gradient.setColorAt(0, QColor("#0f0f0f"))
        gradient.setColorAt(0.3, QColor("#1a1919"))
        gradient.setColorAt(0.6, QColor("#242323"))
        gradient.setColorAt(1, QColor("#333333"))
        painter.fillRect(self.rect(), gradient)


    def init_ui(self):
        self.label.setStyleSheet("color: white;"
                                "font: 20px 'Segoe UI' bold;")



        for button in self.buttons:
            button.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);"
                                 "font: 20px 'Segoe UI' bold;"
                                 "color: white;")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



    def layout(self):
        self.main_layout.addWidget(self.label)
        for button in self.buttons:
            self.main_layout.addWidget(button)
        self.setLayout(self.main_layout)



def main():
    app = QApplication(sys.argv)
    window = TrainingWindow()
    window.showFullScreen()
    window.resize(1024, 600)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()