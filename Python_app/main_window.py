import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("SwimTracker")
        self.window_width = 1024
        self.window_height = 600
        self.setGeometry(0, 0, self.window_width, self.window_height)

        self.plan_training_button = QPushButton(self, text="Plan Training")
        self.start_training_button = QPushButton(self, text="Start Training")
        self.training_history_button = QPushButton(self, text="Training History")
        self.connect_to_sensor_button = QPushButton(self, text="Connect to sensor")

        self.info_button = QPushButton(self)
        self.settings_button = QPushButton(self)

        self.main_buttons = [self.plan_training_button, self.start_training_button, self.training_history_button, self.connect_to_sensor_button]
        self.main_buttons_icons = ["icons/plan.png", "icons/swimmer.png", "icons/training_history.png", "icons/connect.png"]

        self.time = datetime.now().strftime("%H:%M")
        self.date = datetime.now().strftime("%d.%m.%Y")
        self.time_label = QLabel(self)
        self.date_label = QLabel(self)
        self.time_label.setText(self.time)
        self.date_label.setText(self.date)

        self.main_buttons_layout = QGridLayout()
        self.main_layout = QVBoxLayout()
        self.time_date_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()

        self.time_updating_timer = QTimer(self)
        self.time_updating_timer.start(1000)
        self.time_updating_timer.timeout.connect(self.update_time_and_date)

        self.layout_settings()
        self.init_ui()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.drawPixmap(self.rect(), self.background)


    def init_ui(self):
        for i in range(len(self.main_buttons)):
            self.main_buttons[i].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.main_buttons[i].setStyleSheet("background-color: rgba(0, 0, 0, 0.8);"
                                 "color: white;"
                                 "font: 30px 'Segoe UI' bold;"
                                 "font-weight: bold;"
                                 "border-radius: 15px;")
            self.main_buttons[i].setIcon(QIcon(self.main_buttons_icons[i]))
            self.main_buttons[i].setIconSize(QSize(80, 80))


        self.info_button.setIcon(QIcon("icons/info_icon.png"))
        self.settings_button.setIcon(QIcon("icons/settings.png"))

        self.settings_button.setStyleSheet("background-color: #787878;"
                                           "background-color: rgba(0, 0, 0, 0.8);"
                                           "border-radius: 10px;")

        self.info_button.setStyleSheet("background-color: #787878;"
                                       "border-radius: 10px;"
                                       "background-color: rgba(0, 0, 0, 0.8);")
        self.info_button.setIconSize(QSize(30, 30))
        self.settings_button.setIconSize(QSize(30, 30))

        self.time_label.setStyleSheet("color: black;"
                                      "font: bold;"
                                      "font-size: 25px;")

        self.date_label.setStyleSheet("color: black;"
                                      "font: bold;"
                                      "font-size: 25px;")




    def layout_settings(self):
        self.time_date_layout.addWidget(self.time_label)
        self.time_date_layout.addStretch(1)
        self.time_date_layout.addWidget(self.date_label)

        self.main_buttons_layout.addWidget(self.plan_training_button, 0, 0)
        self.main_buttons_layout.addWidget(self.start_training_button, 0, 1)
        self.main_buttons_layout.addWidget(self.training_history_button, 1, 0)
        self.main_buttons_layout.addWidget(self.connect_to_sensor_button, 1, 1)

        self.lower_layout.addWidget(self.info_button)
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.settings_button)

        self.main_layout.addLayout(self.time_date_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.main_buttons_layout, stretch=10)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.lower_layout)

        self.setLayout(self.main_layout)


    def update_time_and_date(self):
        time = datetime.now().strftime("%H:%M")
        date = datetime.now().strftime("%d.%m.%Y")
        self.time_label.setText(time)
        self.date_label.setText(date)

    def toggle_emoji_size(self):
        if self.heart_rate_button.iconSize() == QSize(70, 70):
            self.heart_rate_button.setIconSize(QSize(60, 60))
            self.saturation_button.setIconSize(QSize(60, 60))
        else:
            self.heart_rate_button.setIconSize(QSize(70, 70))
            self.saturation_button.setIconSize(QSize(70, 70))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

main()