"""
Task configuration editor module.
Handles the detailed parameter entry for individual training sets, 
including Pacer synchronization logic and JSON data persistence.
"""

import sys
import app_config
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit, QLayout, QSpacerItem, QScrollArea, QLineEdit, QComboBox
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from app_config import PROJECT_PATH

# Input modules for touch-interface compatibility
from virtual_keyboard import VirtualKeyboard
from numeric_keyboard import NumericKeyboard

import math
import time
import json

class AddTask(QWidget):
    """
    Form-based UI for creating workout tasks.
    
    Features dynamic pacer interval generation based on the selected time limit 
    and multi-keyboard support for different data types.
    """
    def __init__(self, training_name, task_name):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.default_task_name = task_name
        self.training_name = training_name
        self.setCursor(Qt.BlankCursor) # Optimized for touchscreen use

        # --- Label Definitions ---
        self.meters_label = QLabel("meters", self)
        self.x_label = QLabel("x", self)
        self.time_limit_label = QLabel("Time limit:", self)
        self.hear_rate_label = QLabel("Target HR zone:", self)
        self.block_rep_label = QLabel("Total set repetitions:", self)
        self.pacer_label = QLabel("Pacer:")
        self.labels = [self.x_label, self.meters_label,
                       self.time_limit_label, self.hear_rate_label,
                       self.block_rep_label, self.pacer_label]

        # --- User Input Widgets ---
        self.hear_rate = QComboBox(self)
        self.task_name = QLineEdit(self)
        self.meters_input = QLineEdit(self)
        self.time_limit = QComboBox(self)
        self.reps_input = QLineEdit(self)
        self.block_rep = QLineEdit(self)
        self.block_rep.setPlaceholderText("1")
        self.detailed_description = QPlainTextEdit(self)
        self.pace_limit = QComboBox(self)

        self.editables = [self.task_name, self.meters_input, self.reps_input, self.detailed_description,
                           self.hear_rate, self.time_limit, self.block_rep, self.pace_limit]

        # Grouping for keyboard targeting
        self.editable_line_edits = [self.meters_input, self.reps_input, self.detailed_description,
                            self.block_rep]

        # Save trigger
        self.save_button = QPushButton(self)
        self.save_button.clicked.connect(self.save_button_clicked)

        # Responsive font sizing
        self.font_size = int(self.available_height * 0.04)
        self.font_size_2 = int(self.available_height * 0.03)
        self.font_size_3 = int(self.available_height * 0.05)

        # Layout containers
        self.upper_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.repetitions_layout = QHBoxLayout()
        self.description_layout = QHBoxLayout()
        self.pacer_layout = QHBoxLayout()
        self.target_hr_layout = QHBoxLayout()
        self.time_limit_layout = QHBoxLayout()
        self.block_rep_layout = QHBoxLayout()

        # Keyboard systems initialization
        self.keyboard = VirtualKeyboard()
        self.keyboard.finished.connect(self.init_ui)
        self.numeric_keyboard = NumericKeyboard()
        self.numeric_keyboard.hide()

        # Setup Sequence
        self.init_ui()
        self.layout_setting()
        self.time_limit_managment()
        self.hear_rate_zones_managment()
        self.connect_line_edits()
        self.pacer_managment()

    def paintEvent(self, event):
        """Renders a custom linear gradient background for the editor."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 1920, 1080)
        gradient.setColorAt(0, QColor("#0f0f0f"))
        gradient.setColorAt(0.3, QColor("#1a1919"))
        gradient.setColorAt(0.6, QColor("#242323"))
        gradient.setColorAt(1, QColor("#333333"))
        painter.fillRect(self.rect(), gradient)

    def init_ui(self):
        """Applies unified styling and dimensions to input widgets."""
        for label in self.labels:
            label.setStyleSheet(f"color: white; font: {self.font_size}px 'Segoe UI'; font-weight: bold;")

        for editable in self.editables:
            editable.setStyleSheet("background-color: rgb(0, 0, 0); color: white; border-radius: 10px; "
                                   "padding: 10px; font: 25px 'Segoe UI'; font-weight: bold;")
            if isinstance(editable, QLineEdit):
                editable.setAlignment(Qt.AlignCenter)

        self.save_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.8);
                    font: {self.font_size_3}px 'Segoe UI';
                    font-weight: bold; border-radius: 10px; color: black;
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 0, 0, 0.6); padding-top: 3px; padding-left: 3px;
                }}
                """)
        self.save_button.setText("Save")
        self.save_button.setMinimumSize(self.available_width // 4, self.available_height // 20)

        self.task_name.setReadOnly(True)
        self.detailed_description.setMaximumWidth(int(self.available_width // 1.1))
        self.task_name.setMinimumWidth(self.available_width // 3)

        # Specific widget sizing for ergonomic touch targets
        self.time_limit.setFixedSize(self.available_width // 10, self.available_height // 14)
        self.hear_rate.setFixedSize(self.available_width // 3, self.available_height // 14)
        self.block_rep.setFixedSize(self.available_width // 15, self.available_height // 15)
        self.reps_input.setFixedSize(self.available_width // 15, self.available_height // 15)
        self.meters_input.setFixedSize(self.available_width // 13, self.available_height // 15)

        self.detailed_description.setPlaceholderText("Enter detailed description here...")
        self.task_name.setPlaceholderText(self.default_task_name)

    def layout_setting(self):
        """Builds the vertical layout structure for the configuration form."""
        self.target_hr_layout.addWidget(self.hear_rate_label)
        self.target_hr_layout.addWidget(self.hear_rate)
        self.target_hr_layout.setAlignment(Qt.AlignCenter)
        
        self.time_limit_layout.addWidget(self.time_limit_label)
        self.time_limit_layout.addWidget(self.time_limit)
        
        self.description_layout.addStretch(1)
        self.description_layout.addWidget(self.detailed_description, stretch=14)
        self.description_layout.addStretch(1)

        self.block_rep_layout.addStretch(1)
        self.block_rep_layout.addWidget(self.block_rep_label)
        self.block_rep_layout.addWidget(self.block_rep)
        self.block_rep_layout.addStretch(1)
     
        self.repetitions_layout.addStretch(2)
        self.repetitions_layout.addWidget(self.reps_input)
        self.repetitions_layout.addWidget(self.x_label)
        self.repetitions_layout.addWidget(self.meters_input)
        self.repetitions_layout.addWidget(self.meters_label)  
        self.repetitions_layout.addStretch(4)
        self.repetitions_layout.addLayout(self.time_limit_layout)
        self.repetitions_layout.addStretch(2)

        self.pacer_layout.addStretch(1)
        self.pacer_layout.addWidget(self.pacer_label)
        self.pacer_layout.addWidget(self.pace_limit)
        self.pacer_layout.addStretch(1)

        self.main_layout.addWidget(self.task_name, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.repetitions_layout)
        self.main_layout.addLayout(self.description_layout, stretch=14)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.pacer_layout)
        self.main_layout.addLayout(self.block_rep_layout)
        self.main_layout.addLayout(self.target_hr_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

    def save_button_clicked(self):
        """
        Serializes form data into a JSON file for the specific training plan.
        """
        task_data = {
            "task_name": self.task_name.text() if self.task_name.text() else self.default_task_name,
            "ammount_reps": self.reps_input.text(),
            "meters": self.meters_input.text(),
            "detailed_description": self.detailed_description.toPlainText(),
            "target_heart_rate": self.hear_rate.currentText(),
            "time_limit": self.time_limit.currentText(),
            "block_reps": self.block_rep.text() if self.block_rep.text() else "1",
            "pacer": self.pace_limit.currentText()
        }
        # File I/O: Writing task configuration to disk
        path = f"{PROJECT_PATH}/planned_trainings/{self.training_name}/{self.default_task_name}.json"
        with open(path, 'w') as task_file:
            json.dump(task_data, task_file, indent=4)

        self.close()

    def time_limit_managment(self):
        """Dynamically populates the time limit dropdown with 5s increments."""
        self.time_limit.addItem("None")
        for minutes in range(0, 15):
            for seconds in range(0, 60, 5):
                if not (minutes == 0 and seconds <= 20):
                    self.time_limit.addItem(f"{str(minutes)}'{str(seconds).zfill(2)}")
        self.time_limit.currentIndexChanged.connect(self.pacer_managment)

    def hear_rate_zones_managment(self):
        """Loads customized physiological heart rate zones from global config."""
        self.hear_rate.addItem("None")
        try:
            with open(f"{PROJECT_PATH}/hr_zones.json", "r") as file:
                data = json.load(file)
                for zone, range_val in data.items():
                    self.hear_rate.addItem(f"{zone} {range_val}")
        except FileNotFoundError: print("HR Zones config missing.")

    def pacer_managment(self):
        """
        Critical logic: Generates valid pacer beep intervals.
        Ensures the pacer frequency does not exceed the total task time limit.
        """
        current_limit = self.time_limit.currentText()
        if current_limit == "None":
            self.pacer_label.hide()
            self.pace_limit.hide()
            self.pace_limit.clear()
            return
        
        self.pacer_label.show()
        self.pace_limit.show()
        self.pace_limit.clear()

        limit_sec = int(current_limit.split("'")[1])
        limit_min = int(current_limit.split("'")[0])
        total_limit = limit_min * 60 + limit_sec

        # Populate pacer options up to the selected time limit
        for minutes in range(0, 15):
            for seconds in range(0, 60, 5):
                current_total = minutes * 60 + seconds
                if current_total >= total_limit: break
                if minutes == 0 and seconds <= 20: continue
                self.pace_limit.addItem(f"{str(minutes)}'{str(seconds).zfill(2)}")
            else: continue
            break

    def connect_line_edits(self):
        """Binds touchscreen mouse events to specific virtual keyboard types."""
        for line_edit in self.editable_line_edits:
            if line_edit == self.detailed_description:
                line_edit.mousePressEvent = lambda event, e=line_edit: self.show_keyboard(event, e)
            else:
                line_edit.mousePressEvent = lambda event, e=line_edit: self.show_numeric_keyboard(event, e)

    def show_keyboard(self, event, editable):
        """Displays the alphanumeric keyboard for descriptions."""
        self.keyboard.set_target(editable)
        width, height = int(self.available_width // 1.15), int(self.available_height // 2)
        x, y = (self.available_width - width) // 2, self.available_height // 2 - height // 2 + 175
        self.detailed_description.move(x, 10) # Move widget to prevent overlap
        self.keyboard.setGeometry(x, y, width, height)
        self.keyboard.show()
        return QPlainTextEdit.mousePressEvent(editable, event)

    def show_numeric_keyboard(self, event, editable):
        """Displays the simplified numeric keypad for reps/meters."""
        self.numeric_keyboard.set_target(editable)
        self.numeric_keyboard.show()
        return QLineEdit.mousePressEvent(editable, event)

    def mousePressEvent(self, event):
        """Global click listener to auto-close virtual keyboards."""
        for window in QApplication.topLevelWidgets():
            if window.windowTitle() in ["Virtual Keyboard", "Numeric Keyboard"]:
                window.close()