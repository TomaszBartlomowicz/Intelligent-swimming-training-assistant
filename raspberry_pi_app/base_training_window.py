import json
import sys
from app_config import RETURN_BUTTON_STYLE, PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, END_BUTTON_STYLE
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

import get_parameters
import math
import os


class GeneralTaskWindow(QWidget):
    def __init__(self , training_directory):
        super().__init__()

        # Get used screen parameters
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.current_training_directory = training_directory

        # Declaring buttons and labels
        self.heart_rate_button = QPushButton(self)
        self.saturation_button = QPushButton(self)
        self.parameters_buttons = [self.heart_rate_button, self.saturation_button]
        self.current_set_label = QLabel(self)

        self.task_label = QLabel(self)
        self.clock_time = "00:00"

        # Declaring task information
        self.task_number = 1
        print(self.task_number)
        #self.task = ""
        self.num_reps = ""
        self.distance = ""
        self.description = ""
        self.time_limit = ""
        self.target_hr = ""

        # Declaring Text edit windows
        self.details_text_window = QPlainTextEdit()
        self.target_heart_rate_window = QPlainTextEdit()
        self.time_limit_window = QPlainTextEdit()
        self.text_edits = [self.target_heart_rate_window, self.time_limit_window]

        # Available font sizes
        self.font_size_1 = int(self.available_height * 0.02)
        self.font_size_2 = int(self.available_height * 0.035)
        self.font_size_3 = int(self.available_height * 0.04)
        self.font_size_4 = int(self.available_height * 0.05)
        self.font_size_5 = int(self.available_height * 0.06)


        # Available button sizes
        self.big_button = (int(self.available_width / 6), int(self.available_height / 8))
        self.small_button = (int(self.available_width / 10), int(self.available_height / 12))

        # Declaring layouts
        self.upper_layout = QHBoxLayout()
        self.current_set_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.target_parameters_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        # Pool clock
        self.angle_0 = math.radians(0)
        self.angle_1 = math.radians(90)
        self.angle_2 = math.radians(180)
        self.angle_3 = math.radians(270)


        self.clock_widget = QPixmap(self.size())
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.start(10)

        # Thickness and other
        self.font_size = int(self.available_height * 0.04)
        self.clock_x_center = self.available_width * 0.72
        self.clock_y_center = self.available_height * 0.5
        self.arrow_length = 295
        self.arrows_thickness = 30
        self.yellow_circle_radius = 25
        self.marker_thickness_1 = 18
        self.marker_thickness_2 = 14

        self.emoji_timer = QTimer(self)
        self.emoji_timer.start(1000)
        self.emoji_timer.timeout.connect(lambda: self.toggle_emoji_size())

        self.parameters_timer = QTimer(self)
        self.parameters_timer.timeout.connect(lambda: self.update_parameters())


        # Functions calling
        self.layout_settings()
        self.init_ui()
        self.get_task_info()
        self.set_task_info()

        
        # w GUI, w __init__:
        #get_parameters.start_ble()  # startuje BLE w tle

        # Start timera odczytującego wartości co sekundę
        self.parameters_timer.start(1000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(0, 0, self.available_width, self.available_height, QColor("#121212"))

        # Painitng clock
        accent_color = QColor("#E0C341")
        painter.setPen(QPen(accent_color))
        angle_and_marks = {
            270: "60",
            330: "10",
            30: "20",
            90: "30",
            150: "40",
            210: "50"
        }

        font = painter.font()
        font.setPointSize(35)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor("yellow")))

        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            text_box_width = 85
            text_box_height = 85

            if mark == "50":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "40":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "10":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "20":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "60":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle)

            elif mark == "30":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height

            text_rect = QRect(int(box_x), int(box_y), text_box_width, text_box_height)
            painter.drawText(text_rect, Qt.AlignCenter, mark)

        # Painting markers
        for i in range(60):
            angle = math.radians(i * 6)
            clk_marker_start_pos = self.available_width * 0.25
            clk_marker_end_pos = self.available_width * 0.27

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

        ## Painiting arrows
        colors = ["#fc5d00", "#032782", "#820903", "#1c8203"]
        angles = [self.angle_0, self.angle_1, self.angle_2, self.angle_3]

        for i in range(4):
            pen = QPen(QColor(colors[i]), self.arrows_thickness)
            pen.setCapStyle(Qt.RoundCap)  # <--- tutaj ważne!
            painter.setPen(pen)

            x_end = int(self.clock_x_center + self.arrow_length * math.cos(angles[i]))
            y_end = int(self.clock_y_center + self.arrow_length * math.sin(angles[i]))

            painter.drawLine(int(self.clock_x_center), int(self.clock_y_center), x_end, y_end)



        # Small middle circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        circle_width = int(self.yellow_circle_radius * 2)
        circle_height = int(self.yellow_circle_radius * 2)
        painter.drawEllipse(int(self.clock_x_center) - self.yellow_circle_radius,
                            int(self.clock_y_center) - self.yellow_circle_radius,
                            circle_width, circle_height)

        # Timer
        painter.setPen(QPen(QColor("white")))
        text_box_width = 200
        text_box_height = 100

        box_x = self.clock_x_center - (text_box_width / 2)
        box_y = self.clock_y_center * 0.5
        text_rect = QRect(int(box_x), int(box_y), text_box_width, text_box_height)
        font = painter.font()
        font.setPointSize(self.font_size_4)
        font.setBold(True)
        painter.setFont(font)
        if self.clock_time == "GO!":
            painter.setPen(QPen(QColor("green")))
        painter.drawText(text_rect, Qt.AlignCenter, self.clock_time)


    def init_ui(self):
        # Heart rate and saturation button style
        self.heart_rate_button.setIcon(QIcon("icons/heart_rate.png"))
        self.saturation_button.setIcon(QIcon("icons/saturation.png"))

        for button in self.parameters_buttons:
            button.setStyleSheet(PARAMETERS_STYLE)
            button.setIconSize(QSize(90, 90))
            button.setFixedSize(self.big_button[0], self.big_button[1])

        # Labels style
        self.current_set_label.setStyleSheet(LABELS_STYLE)
        self.task_label.setStyleSheet(LABELS_STYLE)

        # Text edits
        for x in self.text_edits:
            x.setStyleSheet(TEXT_EDIT_STYLE)
        self.details_text_window.setStyleSheet(TEXT_EDIT_STYLE)
    
        
       

    def set_task_info(self):
        self.details_text_window.clear()
        self.target_heart_rate_window.clear()
        self.time_limit_window.clear()
        if self.num_reps:
            self.task_label.setText(f" {self.num_reps} x {self.distance}m")
        self.details_text_window.appendPlainText(self.description)
        self.details_text_window.appendPlainText("\n")
        self.target_heart_rate_window.appendPlainText(f"Target HR: {self.target_hr}")
        self.time_limit_window.appendPlainText(f"Time limit: {self.time_limit}")


    def layout_settings(self):

        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.heart_rate_button)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.saturation_button)
        self.upper_layout.addStretch(20)

        self.current_set_layout.addWidget(self.current_set_label)
        self.current_set_layout.addWidget(self.task_label)
        self.current_set_layout.addStretch(100)
        self.current_set_layout.addStretch(73)

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
        if self.heart_rate_button.iconSize() == QSize(90, 90):
            self.heart_rate_button.setIconSize(QSize(80, 80))
            self.saturation_button.setIconSize(QSize(80, 80))
        else:
            self.heart_rate_button.setIconSize(QSize(90, 90))
            self.saturation_button.setIconSize(QSize(90, 90))

    def get_task_info(self):
        current_task = f"Task {self.task_number}.json"
        with open(f"{self.current_training_directory}/{current_task}", 'r') as f:
            task_data = json.load(f)
            self.num_reps = task_data['ammount_reps']
            self.distance = task_data['meters']
            self.description = task_data["detailed_description"]
            self.time_limit = task_data["time_limit"]
            self.target_hr = task_data["target_heart_rate"]





    def update_parameters(self):
        latest = get_parameters.latest_values
        bpm = latest.get("bpm")
        spo2 = latest.get("spo2")
        print(f"[DEBUG1] BPM={bpm}, SpO2={spo2}")  # <- tymczasowo

        if bpm is not None and spo2 is not None:
            if bpm <= 300 and spo2 <= 255:
                self.heart_rate_button.setText(str(bpm))
                self.saturation_button.setText(f"{spo2}%")
                print(f"[DEBUG2] BPM={bpm}, SpO2={spo2}") 
        else:
            self.heart_rate_button.setText("121")
            self.saturation_button.setText("98%")

