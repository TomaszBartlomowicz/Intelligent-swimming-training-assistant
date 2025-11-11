from app_config import POWER_OFF_BUTTON_STYLE, CANCEL_BUTTON_STYLE, QUIT_LABEL_STYLE
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
import os


class PowerOff(QDialog):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowFlags(Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.window_width = width
        self.window_height = height
        
        # Declaring widgets
        self.power_off_button = QPushButton(self)
        self.cancel_button = QPushButton(self)
        self.want_to_quit_label = QLabel(self)

        #Decalraing Layouts
        self.main_layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout()

        # Calling necessary functions
        self.init_ui()
        self.create_layout()
        self.connect_buttons()

    def init_ui(self):
        self.setFixedSize(self.window_width, self.window_height)
        self.power_off_button.setFixedSize(180, 180)
        self.cancel_button.setFixedSize(180, 180)
        self.want_to_quit_label.setText("Do you really want to quit?")
        self.power_off_button.setText("Power Off")
        self.cancel_button.setText("Cancel")

        self.power_off_button.setStyleSheet(POWER_OFF_BUTTON_STYLE)
        self.cancel_button.setStyleSheet(CANCEL_BUTTON_STYLE)
        self.want_to_quit_label.setStyleSheet(QUIT_LABEL_STYLE)

        self.want_to_quit_label.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(255, 255, 255, 240))  
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)


    def create_layout(self):
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.power_off_button)
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.want_to_quit_label)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addStretch(2)


    def connect_buttons(self):
        self.power_off_button.clicked.connect(self.power_off_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def power_off_clicked(self):
        os.system("sudo shutdown now")
        

    def cancel_clicked(self):
        self.close()