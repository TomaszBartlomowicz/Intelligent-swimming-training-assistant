"""
Main Navigation Hub for the Intelligent Swimmer's Training Assistant.
This module manages the primary dashboard, global layout settings, 
and transitions between all functional sub-windows.
"""

from app_config import (PROJECT_PATH, BACKGROUND, MAIN_BUTTON_STYLE, MAIN_WINDOW_MAIN_BUTTON_ICONS,
                        MAIN_WINDOW_LOWER_BUTTONS_STYLE, TIME_DATE_STYLE, CLOCK_BUTTON_STYLE,
                        SENSOR_BUTTON_STYLE, MAIN_WINDOW_LOWER_BUTTONS_ICONS)
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QHBoxLayout,
                             QVBoxLayout, QLabel, QSizePolicy, QGridLayout)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime
import bluetooth_connection
import os

# Sub-module imports for window transitions
import start_training, plan_training, sensor, training_history, info_window, power_off, calculate_hr_max, pace_clock

class MainWindow(QWidget):
    """
    The main UI controller. It handles the 2x2 grid menu, status indicators,
    and coordinates the lifecycle of modal and full-screen windows.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inteligent swimer's training assistant")
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        
        # Geometry setup based on hardware display parameters
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.setGeometry(0, 0, self.available_width, self.available_height)
        
        # Background and cursor management for embedded touchscreen use
        self.background = QPixmap(BACKGROUND)
        self.setCursor(Qt.BlankCursor)

        # Widget Declarations
        self.plan_training_button = QPushButton(self, text="Training Planner")
        self.start_training_button = QPushButton(self, text="Start Training")
        self.training_history_button = QPushButton(self, text="Training History")
        self.get_hr_max_button = QPushButton(self, text="HR max Calculator")
        
        self.pace_clock_button = QPushButton(self)

        self.active_windows = []
        
        self.info_button = QPushButton(self)
        self.connect_to_sensor_button = QPushButton(self)
        self.power_off_button = QPushButton(self)

        self.main_buttons = [self.plan_training_button, self.start_training_button, self.training_history_button, self.get_hr_max_button]
        self.lower_buttons = [self.info_button, self.power_off_button]

        # Initialization of Real-Time Clock data
        self.time = datetime.now().strftime("%H:%M")
        self.date = datetime.now().strftime("%d.%m.%Y")
        self.time_label = QLabel(self)
        self.date_label = QLabel(self)
        self.time_label.setText(self.time)
        self.date_label.setText(self.date)

        # Layout Architectures
        self.main_buttons_layout = QGridLayout()
        self.main_layout = QVBoxLayout()
        self.time_date_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()

        # Dynamic sizing constants
        self.big_button = (int(self.available_width / 7), int(self.available_height / 10))
        self.small_button = (int(self.available_width / 16), int(self.available_height / 16))

        # System Timers
        self.time_updating_timer = QTimer(self)
        self.time_updating_timer.start(1000)
        self.time_updating_timer.timeout.connect(self.update_time_and_date)

        # Setup sequence
        self.layout_settings()
        self.init_ui()
        self.connect_buttons()
        self.showFullScreen()

    def paintEvent(self, event):
        """Renders the custom background pixmap."""
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def init_ui(self):
        """Applies styles, icons, and specific positions to all UI components."""
        ## Styling the 2x2 Grid Buttons
        for i in range(len(self.main_buttons)):
            self.main_buttons[i].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.main_buttons[i].setStyleSheet(MAIN_BUTTON_STYLE)
            self.main_buttons[i].setIcon(QIcon(MAIN_WINDOW_MAIN_BUTTON_ICONS[i]))
            self.main_buttons[i].setIconSize(QSize(80, 80))

        ## Lower Utility Buttons
        for i in range(len(self.lower_buttons)):
            self.lower_buttons[i].setStyleSheet(MAIN_WINDOW_LOWER_BUTTONS_STYLE)
            self.lower_buttons[i].setIcon(QIcon(MAIN_WINDOW_LOWER_BUTTONS_ICONS[i]))
            self.lower_buttons[i].setIconSize(QSize(self.small_button[0], self.small_button[1]))

        ## Global Time/Date Labels
        self.time_label.setStyleSheet(TIME_DATE_STYLE)
        self.date_label.setStyleSheet(TIME_DATE_STYLE)

        # BLE Connection Indicator Management
        self.connect_to_sensor_button.setFixedSize(80, 80)
        self.connect_to_sensor_button.setStyleSheet(SENSOR_BUTTON_STYLE)
        if bluetooth_connection.is_connected():
            self.connect_to_sensor_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/sensor_connected.png"))
        else:
            self.connect_to_sensor_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/sensor_disconnected.png"))
        self.connect_to_sensor_button.setIconSize(QSize(80, 80))
        self.connect_to_sensor_button.move((self.available_width // 2) - 40, 0)  

        # Central Pace Clock Access Point
        self.pace_clock_button.setFixedSize(100, 100)
        self.pace_clock_button.setStyleSheet(CLOCK_BUTTON_STYLE)
        self.pace_clock_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/pace_clock.png"))
        self.pace_clock_button.setIconSize(QSize(100, 100))
        self.pace_clock_button.move((self.available_width // 2) - 50, (self.available_height // 2) - 50)

    def layout_settings(self):
        """Builds the vertical and horizontal layout hierarchy."""
        self.time_date_layout.addWidget(self.time_label)
        self.time_date_layout.addStretch(1)
        self.time_date_layout.addWidget(self.date_label)

        # 2x2 Grid Core
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
        """Synchronizes UI text with System Time."""
        time = datetime.now().strftime("%H:%M")
        date = datetime.now().strftime("%d.%m.%Y")
        self.time_label.setText(time)
        self.date_label.setText(date)

    def toggle_emoji_size(self):
        """UI interaction logic for icon feedback."""
        if self.heart_rate_button.iconSize() == QSize(70, 70):
            self.heart_rate_button.setIconSize(QSize(60, 60))
            self.saturation_button.setIconSize(QSize(60, 60))
        else:
            self.heart_rate_button.setIconSize(QSize(70, 70))
            self.saturation_button.setIconSize(QSize(70, 70))

    def show_window(self, window):
        """
        State machine for window transitions.
        Handles both modal dialogs (setEnabled(False)) and full-screen windows.
        """
        if (window == power_off.PowerOff or window == info_window.InfoDialog or window == sensor.SensorWindow):
            self.setEnabled(False)
            window_width = int(self.available_width // 2)
            window_height = int(self.available_height // 2)
            x_cord = self.available_width // 2 - window_width // 2
            y_cord = self.available_height // 2 - window_height // 2

            window = window()
            window.finished.connect(lambda: self.setEnabled(True))
            window.finished.connect(lambda: self.init_ui()) # Refreshes BLE icon status
            window.setGeometry(x_cord, y_cord, window_width, window_height)
            window.exec_()
        else:
            window = window()
            window.setGeometry(0, 0, self.available_width, self.available_height)
            window.showFullScreen()
            self.active_windows.append(window)
            window.destroyed.connect(lambda: self.active_windows.remove(window))

        window.setCursor(Qt.BlankCursor) # Ensures no cursor is visible on touchscreen

    def connect_buttons(self):
        """Mapping signals to window transition slots."""
        self.start_training_button.clicked.connect(lambda: self.show_window(start_training.ChooseTraining))
        self.plan_training_button.clicked.connect(lambda: self.show_window(plan_training.PlanTraining))
        self.training_history_button.clicked.connect(lambda: self.show_window(training_history.TrainingHistory))
        self.get_hr_max_button.clicked.connect(lambda: self.show_window(calculate_hr_max.CalculateHrMax))

        self.pace_clock_button.clicked.connect(lambda: self.show_window(pace_clock.PaceClock))

        self.connect_to_sensor_button.clicked.connect(lambda: self.show_window(sensor.SensorWindow))
        self.info_button.clicked.connect(lambda: self.show_window(info_window.InfoDialog))
        self.power_off_button.clicked.connect(lambda: self.show_window(power_off.PowerOff))

    def closeEvent(self, event):
        """Safe shutdown sequence: disconnects BLE and restores OS cursor."""
        bluetooth_connection.disconnect_ble()
        os.system("pkill unclutter") 
        event.accept()