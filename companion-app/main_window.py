from app_config import (BACKGROUND, MAIN_BUTTON_STYLE, MAIN_WINDOW_MAIN_BUTTON_ICONS, 
                        MAIN_WINDOW_LOWER_BUTTONS_STYLE, TIME_DATE_STYLE, SENSOR_BUTTON_STYLE, MAIN_WINDOW_LOWER_BUTTONS_ICONS)
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QHBoxLayout,
                              QVBoxLayout, QLabel, QSizePolicy, QGridLayout)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import QSize, QTimer
from datetime import datetime

import start_training, plan_training, sensor, training_history, info_window, power_off, calculate_hr_max


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inteligent swimer's training assistant")
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()

        ## Set up background

        self.background = QPixmap(BACKGROUND)

        # Declaring buttons
        self.plan_training_button = QPushButton(self, text="Training Planner")
        self.start_training_button = QPushButton(self, text="Start Training")
        self.training_history_button = QPushButton(self, text="Training History")
        self.get_hr_max_button = QPushButton(self, text="HR max Calculator")
        

        self.active_windows = []
        
        self.info_button = QPushButton(self)
        self.connect_to_sensor_button = QPushButton(self)
        self.power_off_button = QPushButton(self)

        self.main_buttons = [self.plan_training_button, self.start_training_button, self.training_history_button, self.get_hr_max_button]
        self.lower_buttons = [self.info_button, self.power_off_button]


        # Setting time and date
        self.time = datetime.now().strftime("%H:%M")
        self.date = datetime.now().strftime("%d.%m.%Y")
        self.time_label = QLabel(self)
        self.date_label = QLabel(self)
        self.time_label.setText(self.time)
        self.date_label.setText(self.date)

        # Initializing layouts
        self.main_buttons_layout = QGridLayout()
        self.main_layout = QVBoxLayout()
        self.time_date_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()

        # Available button sizes
        self.big_button = (int(self.available_width / 7), int(self.available_height / 10))
        self.small_button = (int(self.available_width / 16), int(self.available_height / 16))

        # Timers
        self.time_updating_timer = QTimer(self)
        self.time_updating_timer.start(1000)
        self.time_updating_timer.timeout.connect(self.update_time_and_date)

        # Calling necessary functions
        self.layout_settings()
        self.init_ui()
        self.connect_buttons()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)


    def init_ui(self):
        ## Main buttons style
        for i in range(len(self.main_buttons)):
            self.main_buttons[i].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.main_buttons[i].setStyleSheet(MAIN_BUTTON_STYLE)
            self.main_buttons[i].setIcon(QIcon(MAIN_WINDOW_MAIN_BUTTON_ICONS[i]))
            self.main_buttons[i].setIconSize(QSize(80, 80))

        ## Lower buttons style
        for i in range(len(self.lower_buttons)):
            self.lower_buttons[i].setStyleSheet(MAIN_WINDOW_LOWER_BUTTONS_STYLE)
            self.lower_buttons[i].setIcon(QIcon(MAIN_WINDOW_LOWER_BUTTONS_ICONS[i]))
            self.lower_buttons[i].setIconSize(QSize(self.small_button[0], self.small_button[1]))

        ## Time and date style
        self.time_label.setStyleSheet(TIME_DATE_STYLE)
        self.date_label.setStyleSheet(TIME_DATE_STYLE)

        # Connect to sensor button 
        self.connect_to_sensor_button.setFixedSize(80, 80)  # kwadrat
        self.connect_to_sensor_button.setStyleSheet(SENSOR_BUTTON_STYLE)
        self.connect_to_sensor_button.setIcon(QIcon("icons/sensor_connected.png"))
        self.connect_to_sensor_button.setIconSize(QSize(80, 80))
        self.connect_to_sensor_button.move((self.available_width // 2) - 40, 0)


    def layout_settings(self):
        self.time_date_layout.addWidget(self.time_label)
        self.time_date_layout.addStretch(1)
        self.time_date_layout.addWidget(self.date_label)

        self.main_buttons_layout.addWidget(self.plan_training_button, 0, 0)
        self.main_buttons_layout.addWidget(self.start_training_button, 0, 1)
        self.main_buttons_layout.addWidget(self.training_history_button, 1, 0)
        self.main_buttons_layout.addWidget(self.get_hr_max_button, 1, 1)

        self.lower_layout.addWidget(self.info_button)
        self.lower_layout.addStretch(1)
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.power_off_button)

        self.main_layout.addLayout(self.time_date_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.main_buttons_layout, stretch=40)
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


    def show_window(self, window):
        print("funckcja show wywolana")
        if (window == power_off.PowerOff or window == info_window.InfoDialog or window == sensor.SensorWindow):
            self.setEnabled(False)
            window_width = int(self.available_width // 2)
            window_height = int(self.available_height // 2)
            x_cord = self.available_width // 2 - window_width // 2
            y_cord = self.available_height // 2 - window_height // 2
            
            window = window(window_width, window_height)
            window.finished.connect(lambda: self.setEnabled(True))
            window.setGeometry(x_cord, y_cord, window_width, window_height)
            window.exec_()

        else:
            window = window()
            window.showFullScreen()
            self.active_windows.append(window)
            window.destroyed.connect(lambda: self.active_windows.remove(window))


    def connect_buttons(self):
        self.start_training_button.clicked.connect(lambda: self.show_window(start_training.ChooseTraining))
        self.plan_training_button.clicked.connect(lambda: self.show_window(plan_training.PlanTraining))
        self.training_history_button.clicked.connect(lambda: self.show_window(training_history.TrainingHistory))
        self.get_hr_max_button.clicked.connect(lambda: self.show_window(calculate_hr_max.CalculateHrMax))


        self.connect_to_sensor_button.clicked.connect(lambda: self.show_window(sensor.SensorWindow))
        self.info_button.clicked.connect(lambda: self.show_window(info_window.InfoDialog))
        self.power_off_button.clicked.connect(lambda: self.show_window(power_off.PowerOff))