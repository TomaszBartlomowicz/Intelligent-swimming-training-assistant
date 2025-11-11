from app_config import (BACKGROUND, MAIN_BUTTON_STYLE, RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE)
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy, QLabel
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
import os

import base_training_window
import training_window

class ChooseTraining(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()

        self.background = QPixmap(BACKGROUND)
        print("okno zrobione")
        # Declaring buttons
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)

        # Dynamic declaration of training buttons
        self.planned_trainings = os.listdir("planned_trainings")
        print(self.planned_trainings)
        self.buttons = []
        if self.planned_trainings:
            for training_name in self.planned_trainings:
                button = QPushButton(training_name)
                self.buttons.append(button)
        else:
            button = QPushButton(self, text = "Add a training first")
            button.setDisabled(True)
        

        # Layouts and scroll area
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.buttons_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout = QHBoxLayout()

        # Calling necessary functions
        self.init_ui()
        self.layout()
        self.connect_buttons()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)


    def init_ui(self):
        # Main buttons 
        for button in self.buttons:
            button.setStyleSheet(MAIN_BUTTON_STYLE)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(self.available_height // 6)

        # Return button 
        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)


    def layout(self):
        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        self.buttons_layout.setAlignment(Qt.AlignCenter)
        print("layout kruwaaaaaaaa")
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.return_button, stretch = 1)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch = 8)
        self.main_layout.addStretch(3)

        self.setLayout(self.main_layout)
        print("layout_done")

    def button_clicked(self, directory):
        self.training_window = training_window.NextTask(directory)
        self.training_window.showFullScreen()



    def connect_buttons(self):
        for button in self.buttons:
            directory = f"planned_trainings/{button.text()}" 
            button.clicked.connect(lambda checked = False, d = directory : self.button_clicked(d))




