import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer

import math
import time
import training_window

class TrainingWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Get used screen parameters
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()

        # Declaring buttons

        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)

        # TODO Dynamic declaration of training buttons
        self.training1_label = QPushButton("Training 1")
        self.training2_label = QPushButton("Training 2")
        self.training3_label = QPushButton("Training 3")
        self.training4_label = QPushButton("Training 4")
        self.training5_label = QPushButton("Training 5")
        self.training6_label = QPushButton("Training 6")
        self.buttons = [self.training1_label, self.training2_label, self.training3_label, self.training4_label,
                        self.training5_label, self.training6_label]

        # TYMACZASOWE
        self.training1_label.clicked.connect(self.show_training1)

        self.background = QPixmap("icons/basen3.jpg")

        # Managing scroll area
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.buttons_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout = QHBoxLayout()
        self.init_ui()
        self.layout()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)


    def init_ui(self):
        for button in self.buttons:
            button.setStyleSheet(""" 
            QPushButton {
                                 background-color: rgba(0, 0, 0, 0.8);
                                 color: white;
                                 font: 30px 'Segoe UI';
                                 font-weight: bold;
                                 border-radius: 15px;
                                 }
                                 
            QPushButton:pressed {
                                background-color: rgba(25, 25, 25, 0.8);
                                /* Gdy wciśnięty, przesuwamy zawartość w dół i w prawo */
                                padding-top: 3px;
                                padding-left: 3px;
    }
            """
            )
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(self.available_height // 6)

            self.return_button.setIcon(QIcon("icons/return.png"))
            self.return_button.setStyleSheet(""" 
            QPushButton {
                                 background-color: rgba(0, 0, 0, 0.8);
                                 color: white;
                                 font: 30px 'Segoe UI';
                                 font-weight: bold;
                                 border-radius: 15px;
                                 }
                                 
            QPushButton:pressed {
                                background-color: rgba(25, 25, 25, 0.8);
                                padding-top: 3px;
                                padding-left: 3px;
    }
            """)
            self.return_button.setIconSize(QSize(80, 80))

            self.scroll_area.setStyleSheet("background-color: transparent; border: none;")



    def layout(self):
        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        self.buttons_layout.setAlignment(Qt.AlignCenter)


        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.return_button)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch = 4)
        self.main_layout.addStretch(2)

        self.setLayout(self.main_layout)


    # POKAZOWE
    def show_training1(self):
        self.training1_window = training_window.TrainingWindow1()
        self.training1_window.showFullScreen()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = TrainingWindow()
    window.showFullScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()