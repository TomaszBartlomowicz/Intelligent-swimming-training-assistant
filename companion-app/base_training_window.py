"""
Base graphical engine for training sessions.
Provides the shared infrastructure for Pace Clock rendering, BLE telemetry acquisition,
and dynamic task description loading from JSON.
"""

import json
import sys
from app_config import PROJECT_PATH, RETURN_BUTTON_STYLE, PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, END_BUTTON_STYLE
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

import bluetooth_connection
import math
import os

class GeneralTaskWindow(QWidget):
    """
    Core UI class for workout screens. 
    Manages the split-screen layout: real-time stats/task details on the left, 
    and the analog-style Pace Clock on the right.
    """
    def __init__(self, training_directory):
        super().__init__()

        # --- Display Configuration ---
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.setGeometry(0, 0, self.available_width, self.available_height)
        self.setCursor(Qt.BlankCursor) # Hide cursor for embedded touch use
        self.current_training_directory = training_directory

        # --- Metric Display Components ---
        self.heart_rate_button = QPushButton(self)
        self.saturation_button = QPushButton(self)
        self.parameters_buttons = [self.heart_rate_button, self.saturation_button]
        self.current_set_label = QLabel(self)
        self.task_label = QLabel(self)
        self.clock_time = "00:00"

        # --- Task State Data ---
        self.task_number = 1
        self.num_reps = ""
        self.distance = ""
        self.description = ""
        self.time_limit = ""
        self.target_hr = ""
        self.block_reps = ""

        # --- Descriptive UI Windows ---
        self.details_text_window = QTextEdit()
        self.target_heart_rate_window = QTextEdit()
        self.time_limit_window = QTextEdit()
        self.text_edits = [self.target_heart_rate_window, self.time_limit_window]

        # --- Responsive Font Sizing ---
        self.font_size_1 = int(self.available_height * 0.02)
        self.font_size_2 = int(self.available_height * 0.035)
        self.font_size_3 = int(self.available_height * 0.04)
        self.font_size_4 = int(self.available_height * 0.05)
        self.font_size_5 = int(self.available_height * 0.06)

        # --- Layout Assembly ---
        self.upper_layout = QHBoxLayout()
        self.current_set_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.target_parameters_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        # --- Pace Clock Graphical Settings ---
        self.angle_0 = math.radians(0)
        self.angle_1 = math.radians(90)
        self.angle_2 = math.radians(180)
        self.angle_3 = math.radians(270)

        # Constants for trigonometric clock rendering
        self.clock_x_center = self.available_width * 0.72
        self.clock_y_center = self.available_height * 0.5
        self.arrow_length = 295
        self.arrows_thickness = 30
        self.yellow_circle_radius = 25
        self.marker_thickness_1 = 18
        self.marker_thickness_2 = 14

        # --- Timing Systems ---
        # Animation timer for clock hands
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.start(10)

        # UI feedback timers
        self.emoji_timer = QTimer(self)
        self.emoji_timer.start(1000)
        self.emoji_timer.timeout.connect(self.toggle_emoji_size)

        # BLE data polling timer (1Hz)
        self.parameters_timer = QTimer(self)
        self.parameters_timer.timeout.connect(self.update_parameters)

        # Available button sizes
        self.big_button = (int(self.available_width / 6), int(self.available_height / 8))
        self.small_button = (int(self.available_width / 10), int(self.available_height / 12))

        # Core initialization
        self.layout_settings()
        self.get_task_info()
        self.set_task_info()
        self.init_ui()
        self.parameters_timer.start(1000)

    def paintEvent(self, event):
        """
        Custom rendering engine for the workout UI.
        Draws the dark theme background and the mathematical analog clock face.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(0, 0, self.available_width, self.available_height, QColor("#121212"))

        # --- Drawing Clock Numerals ---
        painter.setPen(QPen(QColor("#E0C341")))
        angle_and_marks = {270: "60", 330: "10", 30: "20", 90: "30", 150: "40", 210: "50"}

        font = painter.font()
        font.setPointSize(35)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor("yellow")))

        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            text_box_width = text_box_height = 85
            # Strategic positioning logic for clock digits
            if mark == "50" or mark == "40":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2
            elif mark == "10" or mark == "20":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2
            elif mark == "60":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle)
            elif mark == "30":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height

            painter.drawText(QRect(int(box_x), int(box_y), text_box_width, text_box_height), Qt.AlignCenter, mark)

        # --- Drawing Perimeter Markers (60 ticks) ---
        for i in range(60):
            angle = math.radians(i * 6)
            clk_marker_start_pos = self.available_width * 0.25
            clk_marker_end_pos = self.available_width * 0.27
            # Differentiate major (15s/5s) markers by thickness
            if (i * 6) % 90 == 0:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_1))
                clk_marker_start_pos = self.available_width * 0.238  
            elif (i * 6) % 30 == 0:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_1))
                clk_marker_start_pos = self.available_width * 0.240
            else:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_2))
            
            x_start = int(self.clock_x_center + clk_marker_start_pos * math.cos(angle))
            y_start = int(self.clock_y_center + clk_marker_start_pos * math.sin(angle))
            x_end = int(self.clock_x_center + clk_marker_end_pos * math.cos(angle))
            y_end = int(self.clock_y_center + clk_marker_end_pos * math.sin(angle))
            painter.drawLine(x_start, y_start, x_end, y_end)

        # --- Drawing Rotating Pace Arrows ---
        colors = ["#fc5d00", "#032782", "#820903", "#1c8203"]
        angles = [self.angle_0, self.angle_1, self.angle_2, self.angle_3]

        for i in range(4):
            pen = QPen(QColor(colors[i]), self.arrows_thickness)
            pen.setCapStyle(Qt.RoundCap) # Aesthetic rounded tips
            painter.setPen(pen)
            x_end = int(self.clock_x_center + self.arrow_length * math.cos(angles[i]))
            y_end = int(self.clock_y_center + self.arrow_length * math.sin(angles[i]))
            painter.drawLine(int(self.clock_x_center), int(self.clock_y_center), x_end, y_end)

        # Center Pivot Circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        painter.drawEllipse(int(self.clock_x_center) - self.yellow_circle_radius,
                            int(self.clock_y_center) - self.yellow_circle_radius,
                            int(self.yellow_circle_radius * 2), int(self.yellow_circle_radius * 2))

        # --- Digital Timer Overlay ---
        painter.setPen(QPen(QColor("white")))
        box_x = self.clock_x_center - 100
        box_y = self.clock_y_center * 0.5
        text_rect = QRect(int(box_x), int(box_y), 200, 100)
        font.setPointSize(45)
        painter.setFont(font)
        if self.clock_time == "GO!":
            painter.setPen(QPen(QColor("green")))
        painter.drawText(text_rect, Qt.AlignCenter, self.clock_time)

    def init_ui(self):
        """Applies configuration-based styling to permanent UI elements."""
        self.heart_rate_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/heart_rate.png"))
        self.saturation_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/saturation.png"))

        for button in self.parameters_buttons:
            button.setStyleSheet(PARAMETERS_STYLE)
            button.setIconSize(QSize(90, 90))
            button.setFixedSize(self.big_button[0], self.big_button[1])

        self.current_set_label.setStyleSheet(LABELS_STYLE)
        self.task_label.setStyleSheet(LABELS_STYLE)

        for x in self.text_edits:
            x.setStyleSheet(TEXT_EDIT_STYLE)
            x.setAlignment(Qt.AlignCenter)
            x.setDisabled(True)
        self.details_text_window.setStyleSheet(TEXT_EDIT_STYLE)

    def set_task_info(self):
        """Populates text windows with data parsed from the session JSON."""
        self.details_text_window.clear()
        self.target_heart_rate_window.clear()
        self.time_limit_window.clear()
        
        if self.num_reps:
            self.task_label.setText(f" {self.num_reps} x {self.distance}m")
        
        self.details_text_window.append(self.description)
        self.details_text_window.append("\n")
        
        if int(self.block_reps) >= 2:    
            self.details_text_window.append("---------------------------------------")
            self.details_text_window.append(f"Repeat Everything {self.block_reps} times")
        
        if ":" in self.target_hr:
            hr_value = self.target_hr.split(":")[1]
            self.target_heart_rate_window.append(f"Target HR:       {hr_value}")
        else:
            self.target_heart_rate_window.append(f"Target HR:       {self.target_hr}")
            
        self.time_limit_window.append(f"Time limit:    {self.time_limit}")
        self.details_text_window.setAlignment(Qt.AlignCenter)

    def layout_settings(self):
        """Assembles the UI components into a multi-layered nested layout."""
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.heart_rate_button)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.saturation_button)
        self.upper_layout.addStretch(20)

        self.current_set_layout.addWidget(self.current_set_label)
        self.current_set_layout.addWidget(self.task_label)
        self.current_set_layout.addStretch(10)

        self.middle_layout.addWidget(self.details_text_window, stretch=10)
        self.middle_layout.addStretch(13)

        self.target_parameters_layout.addWidget(self.target_heart_rate_window, stretch=5)
        self.target_parameters_layout.addWidget(self.time_limit_window, stretch=5)
        self.target_parameters_layout.addStretch(13)

        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.current_set_layout)
        self.main_layout.addLayout(self.middle_layout, stretch=18)
        self.main_layout.addLayout(self.target_parameters_layout, stretch=7 )
        self.main_layout.addStretch(1)

    def toggle_emoji_size(self):
        """Visual pulse effect for metrics to indicate active data polling."""
        size = 80 if self.heart_rate_button.iconSize() == QSize(90, 90) else 90
        for button in self.parameters_buttons:
            button.setIconSize(QSize(size, size))

    def get_task_info(self):
        """Filesystem read: extracts current task metadata from the training folder."""
        current_task = f"Task {self.task_number}.json"
        try:
            with open(f"{self.current_training_directory}/{current_task}", 'r') as f:
                task_data = json.load(f)
                self.num_reps = task_data['ammount_reps']
                self.distance = task_data['meters']
                self.description = task_data["detailed_description"]
                self.time_limit = task_data["time_limit"]
                self.target_hr = task_data["target_heart_rate"]
                self.block_reps = task_data["block_reps"]
        except Exception as e: print(f"JSON Read Error: {e}")

    def update_parameters(self):
        """
        Retrieves real-time telemetry from the BLE manager.
        Performs data validation and logs valid physiological points to disk.
        """
        latest = getattr(bluetooth_connection, "latest_values", {})
        bpm = latest.get("bpm")
        spo2 = latest.get("spo2")

        if bpm is not None and spo2 is not None:
            # Range validation for clinical/athletic plausibility
            if 30 <= bpm <= 220 and 50 <= spo2 <= 100:
                self.heart_rate_button.setText(f"{int(bpm)}")
                self.saturation_button.setText(f"{int(spo2)}%")
                # Persistent logging for post-training analytics
                with open(f"{self.current_training_directory}/training_data.txt", "a") as file:
                    file.write(f"{bpm},{spo2}\n")
            else:
                self.heart_rate_button.setText("--")
                self.saturation_button.setText("--")
        else:
            self.heart_rate_button.setText("--")
            self.saturation_button.setText("--")