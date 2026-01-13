"""
Personalized Heart Rate Zone Calculator.
Implements the Tanaka formula to define physiological training zones 
and persists results for session planning.
"""

import app_config
from app_config import (PROJECT_PATH, BACKGROUND, HR_MAX_LABEL_STYLE, SAVE_BUTTON_STYLE, GET_HR_MAX_STYLE, MSG_STYLE,
                        RETURN_BUTTON_STYLE, RECOVERY_LAVBEL_STYLE, AEROBIC_CAPACITY_STYLE, AEROBIC_ENDURANCE_STYLE, 
                        ANAEROBIC_STYLE, VO2_MAX_STYLE, TRAINING_NAME_STYLE)
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPainter, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QTimer
import json
import numeric_keyboard
import sys

class CalculateHrMax(QWidget):
    """
    UI for calculating HR Max and defining 5 distinct training zones.
    Ensures that workout intensity targets are tailored to the individual's age.
    """
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.background = QPixmap(BACKGROUND)

        # --- Button Initialization ---
        self.calculate_button = QPushButton(self)
        self.calculate_button.clicked.connect(self.calculate_button_clicked)
        
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)
        
        self.save_button = QPushButton(self)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.save_button.hide() # Hidden until calculation is performed

        # Virtual numeric keypad for embedded touchscreen entry
        self.numeric_keyboard = numeric_keyboard.NumericKeyboard()

        # Age input field
        self.users_age = QLineEdit(self)

        # Result Labels
        self.hr_max_label = QLabel(self)
        self.recovery_label = QLabel(self)
        self.aerobic_endurance_label = QLabel(self)
        self.aerobic_capacity_label = QLabel(self)
        self.anaerobic_label = QLabel(self)
        self.vo2max_label = QLabel(self)

        self.zones = [self.recovery_label, self.aerobic_endurance_label, 
                      self.aerobic_capacity_label, self.anaerobic_label, self.vo2max_label]

        # Warning MessageBox for validation
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setWindowFlags(Qt.Popup)
        self.msg.setAttribute(Qt.WA_TranslucentBackground)

        # Layout Containers
        self.main_layout = QVBoxLayout()
        self.hr_zones_layout = QVBoxLayout()
        self.upper_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()

        # Calculation state
        self.is_hr_max_calculated = False
        self.hr_max = None
        self.recovery = self.aerobic_e = self.aerobic_c = self.anaerobic = self.vo2_max = None

        self.init_ui()
        self.manage_layout()
        self.connect_users_age_to_numeric_keyboard()

    def paintEvent(self, event):
        """Renders the background and a semi-transparent panel upon successful calculation."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawPixmap(self.rect(), self.background)

        # Dynamic UI: Draw a dark overlay only when results are visible
        color = QColor(0, 0, 0, 180)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        if self.is_hr_max_calculated:
            painter.drawRoundedRect(200, 240, int(self.width() - 400), 330, 25.0, 25.0)

    def init_ui(self):
        """Applies configuration-based styles to labels and buttons."""
        self.calculate_button.setText("Get HR Max")
        self.calculate_button.setStyleSheet(GET_HR_MAX_STYLE)
        self.calculate_button.setMinimumWidth(self.available_width // 3)
        self.calculate_button.setMaximumHeight(self.available_height // 8)

        self.save_button.setText("Save")
        self.save_button.setStyleSheet(SAVE_BUTTON_STYLE)
        self.save_button.setMinimumWidth(self.available_width // 5)
        self.save_button.setMaximumHeight(self.available_height // 8)

        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.move(30, int(self.height()/2) + 80)

        self.users_age.setStyleSheet(TRAINING_NAME_STYLE)
        self.users_age.setAlignment(Qt.AlignCenter)
        self.users_age.setPlaceholderText("Enter your age!")
        self.users_age.setMaximumHeight(self.available_height // 8)
        self.users_age.setMinimumWidth(self.available_width // 3)

        self.hr_max_label.setStyleSheet(HR_MAX_LABEL_STYLE)

        # Apply specific zone colors for immediate visual recognition
        self.recovery_label.setStyleSheet(RECOVERY_LAVBEL_STYLE)
        self.aerobic_endurance_label.setStyleSheet(AEROBIC_ENDURANCE_STYLE)
        self.aerobic_capacity_label.setStyleSheet(AEROBIC_CAPACITY_STYLE)
        self.anaerobic_label.setStyleSheet(ANAEROBIC_STYLE)
        self.vo2max_label.setStyleSheet(VO2_MAX_STYLE)

        self.msg.setStyleSheet(MSG_STYLE)

    def manage_layout(self):
        """Builds the vertical UI structure."""
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.users_age)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.calculate_button)
        self.upper_layout.addStretch(1)
        
        for zone in self.zones:
            self.hr_zones_layout.addWidget(zone, alignment=Qt.AlignCenter)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(2)
        self.main_layout.addWidget(self.hr_max_label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(3)
        self.main_layout.addLayout(self.hr_zones_layout, stretch=10)
        self.main_layout.addStretch(4)
        self.main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)

    def connect_users_age_to_numeric_keyboard(self):
        """Intercepts touch events to launch the numeric keypad."""
        self.users_age.mousePressEvent = lambda event: self.show_numeric_keyboard(event)

    def show_numeric_keyboard(self, event):
        """Configures and displays the custom numeric keypad."""
        self.numeric_keyboard.set_target(self.users_age)
        self.numeric_keyboard.show()
        return QLineEdit.mousePressEvent(self.users_age, event)
   
    def calculate_button_clicked(self):
        """
        Executes the physiological calculation.
        Uses the Tanaka Formula: HRmax = 208 - (0.7 * age).
        """
        age_entered = self.users_age.text()
        if not age_entered:
            self.msg.setText("Enter your age first!")
            self.msg.show()
            return
        
        self.is_hr_max_calculated = True
        age = int(age_entered)
        # Applying the Tanaka equation for superior athletic accuracy
        self.hr_max = round(208 - (0.7 * age))
        self.hr_max_label.setText(f"Your HR Max is: {self.hr_max} bpm.")

        self.calculate_hr_zones()

        # Update labels with calculated BPM ranges
        self.recovery_label.setText(f"Recovery Zone (50-60% HR max): {self.recovery}")
        self.aerobic_endurance_label.setText(f"Aerobic Endurance (60-70% HR max): {self.aerobic_e}")
        self.aerobic_capacity_label.setText(f"Aerobic Capacity (70-80% HR max): {self.aerobic_c}")
        self.anaerobic_label.setText(f"Anaerobic zone (80-90% HR max): {self.anaerobic}")
        self.vo2max_label.setText(f"VO2Max Zone (90-100% HR max): {self.vo2_max}")

        self.save_button.show()
        self.update() # Trigger repaint for the results overlay

    def calculate_hr_zones(self):
        """Calculates specific BPM thresholds for 5 intensity levels."""
        prct50 = int(self.hr_max * 0.5)
        prct60 = int(self.hr_max * 0.6)
        prct70 = int(self.hr_max * 0.7)
        prct80 = int(self.hr_max * 0.8)
        prct90 = int(self.hr_max * 0.9)

        self.recovery = f"{prct50} - {prct60} bpm"
        self.aerobic_e = f"{prct60} - {prct70} bpm"
        self.aerobic_c = f"{prct70} - {prct80} bpm"
        self.anaerobic = f"{prct80} - {prct90} bpm"
        self.vo2_max = f"{prct90} - {self.hr_max} bpm"

    def save_button_clicked(self):
        """
        Persists calculated zones to a JSON file.
        This data is consumed by the Training Planner to suggest targets.
        """
        data = {
            "Recovery:": self.recovery,
            "Endurance:": self.aerobic_e,
            "Tempo:": self.aerobic_c,
            "Threshold:": self.anaerobic,
            "VO2 Max:": self.vo2_max
        }
        with open(f"{PROJECT_PATH}/hr_zones.json", "w") as f:
            json.dump(data, f, indent=4)

        # Clear UI to provide "Saved" confirmation feedback
        for zone in self.zones: zone.setText(" ")
        self.aerobic_capacity_label.setText("Saved!")

        # Automated transition back to main menu after delay
        QTimer.singleShot(1000, self.close)