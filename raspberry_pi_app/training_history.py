from app_config import (BACKGROUND, MAIN_BUTTON_STYLE, RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE)
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout,
    QScrollArea, QSizePolicy)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
import os
import training_overwiev


class TrainingHistory(QWidget):
    def __init__(self):
        super().__init__()
        # Get used screen parameters
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()

        self.background = QPixmap(BACKGROUND)

        # Declaring buttons
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)

        self.finished_trainings = os.listdir("finished_trainings")
        self.buttons = []
        for training_name in self.finished_trainings:
            button = QPushButton(training_name)
            self.buttons.append(button)

        # Scroll area and layouts
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.buttons_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout = QHBoxLayout()
        self.init_ui()
        self.layout()
        self.connect_buttons()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def init_ui(self):
        #Main buttons
        for button in self.buttons:
            button.setStyleSheet(MAIN_BUTTON_STYLE)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(self.available_height // 6)

        # Return button    
        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        #Scroll area
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

    def layout(self):
        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        self.buttons_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.return_button)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch=8)
        self.main_layout.addStretch(2)

        self.setLayout(self.main_layout)

    def button_clicked(self, directory):
        self.training_window = training_overwiev.TrainingOverwiev(directory)
        self.training_window.showFullScreen()
        self.close()

    def connect_buttons(self):
        for button in self.buttons:
            directory = f"finished_trainings/{button.text()}"
            button.clicked.connect(lambda checked = False, d = directory : self.button_clicked(d))

