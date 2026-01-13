import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime
from app_config import RETURN_BUTTON_STYLE, PROJECT_PATH
from heart_rate_chart import HearRateChart
from saturation_chart import SPO2Chart

class TrainingOverwiev(QWidget):
    def __init__(self, directory):
        super().__init__()

        self.background = QPixmap(f"{PROJECT_PATH}/icons/basen3.jpg")
        self.trainig_name = directory.split("/")[6]

        self.current_training_directory = directory

        self.training_name_label = QLabel(self)
        self.training_duration_label = QLabel(self)
        #self.total_disctance_label = QLabel(self)
        self.average_heart_rate_label = QLabel(self)
        self.max_heart_rate_label = QLabel(self)
        self.min_heart_rate_label = QLabel(self)
        self.average_spo2_label = QLabel(self)
        self.max_spo2_label = QLabel(self)
        self.min_spo2_label = QLabel(self)

        self.labels = [self.training_name_label, self.training_duration_label, 
                       self.average_heart_rate_label, self.max_heart_rate_label, self.min_heart_rate_label,
                       self.average_spo2_label, self.max_spo2_label, self.min_spo2_label]


        self.average_heart_rate = ""
        self.max_heart_rate = ""
        self.min_heart_rate = ""
        self.average_spo2 = ""
        self.max_spo2 = ""
        self.min_spo2 = ""
        self.parameters = [self.average_heart_rate, self.max_heart_rate, self.min_heart_rate,
                       self.average_spo2, self.max_spo2, self.min_spo2]

        self.hear_rate_chart_button = QPushButton(self)
        self.hear_rate_chart_button.clicked.connect(self.hear_rate_chart_clicked)
        self.spo2_chart_button = QPushButton(self)
        self.spo2_chart_button.clicked.connect(self.spo2_chart_clicked)
        self.see_chart_buttons = [self.hear_rate_chart_button, self.spo2_chart_button]
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)

        self.main_layout = QVBoxLayout()

        self.heart_rate_layout = QVBoxLayout()
        self.spo2_layout = QVBoxLayout()

        self.lower_layout = QHBoxLayout()
        self.upper_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.lower_layout.setContentsMargins(0, 0, 0, 0)
        self.upper_layout.setContentsMargins(0, 0, 0, 0)
        self.heart_rate_layout.setContentsMargins(0, 0, 0, 0)
        self.spo2_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setSpacing(0)
        self.lower_layout.setSpacing(0)
        self.upper_layout.setSpacing(0)
        self.heart_rate_layout.setSpacing(10)
        self.spo2_layout.setSpacing(10)

        
        self.HR_list = []
        self.Spo2_list = []

        # Calling necessary functions

        self.init_ui()
        self.create_layout()
        self.get_parametrs_values()
        self.set_labels_text()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)


        color = QColor(0, 0, 0, 160)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(200, 280, int(self.width() - 400), 280, 35.0, 35.0)
        painter.end()


    def get_parametrs_values(self):

        with open(f"{self.current_training_directory}/training_data.txt", "r") as file:
            for line in file:
                if "," not in line:
                    continue

                splitted = line.split(',')
                hr = int(splitted[0])
                spo2 = int(splitted[1])
                self.HR_list.append(hr)
                self.Spo2_list.append(spo2)

        avg_hr = int(sum(self.HR_list)/len(self.HR_list))
        min_hr = min(self.HR_list)
        max_hr = max(self.HR_list)

        avg_spo2 = int(sum(self.Spo2_list)/len(self.Spo2_list))
        min_spo2 = min(self.Spo2_list)
        max_spo2 = max(self.Spo2_list)


        self.average_heart_rate = f"{str(avg_hr)} bpm"
        self.max_heart_rate = f"{str(max_hr)} bpm"
        self.min_heart_rate = f"{str(min_hr)} bpm"
        self.average_spo2 = f"{str(avg_spo2)}%"
        self.max_spo2 = f"{str(max_spo2)}%"
        self.min_spo2 = f"{str(min_spo2)}%"

    def calculate_training_duration(self):
            """
            Calculates total training duration in minutes.
            Simple and direct subtraction of session timestamps.
            """
            start_dt = end_dt = None
            log_path = f"{self.current_training_directory}/training_data.txt"
            
            try:
                if not os.path.exists(log_path):
                    return "Duration: -- min"

                with open(log_path, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        if "SESSION START:" in line:
                            start_str = line.split("SESSION START: ")[1].strip()
                            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                        if "SESSION END:" in line:
                            end_str = line.split("SESSION END: ")[1].strip()
                            end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")

                # Check if both timestamps were successfully parsed
                if start_dt and end_dt:
                    # .total_seconds() gives the full span, then we convert to whole minutes
                    duration_seconds = (end_dt - start_dt).total_seconds()
                    duration_minutes = int(duration_seconds // 60)
                    return f"Duration: {duration_minutes} min"
                
            except Exception as e:
                print(f"Error calculating duration: {e}")
                return "Duration: -- min"

            # Return this if file exists but timestamps are missing
            return "Duration: -- min"
    def set_labels_text(self):

        self.training_name_label.setText(self.trainig_name)
        self.training_duration_label.setText("Training Duration: 1h 25m")
        self.average_heart_rate_label.setText("Average HR: " + str(self.average_heart_rate))
        self.max_heart_rate_label.setText("Max HR: " + str(self.max_heart_rate))
        self.min_heart_rate_label.setText("Min HR: " + str(self.min_heart_rate))

        self.average_spo2_label.setText("Average SpO₂: " + str(self.average_spo2))
        self.max_spo2_label.setText("Max SpO₂: " + str(self.max_spo2))
        self.min_spo2_label.setText("Min SpO₂: " + str(self.min_spo2))

        self.hear_rate_chart_button.setText("Heart Rate Chart")
        self.spo2_chart_button.setText("Saturation Chart")

    def init_ui(self):

        for label in self.labels:
            if label == self.training_name_label:
                label.setStyleSheet("""
                    color: #FFD740;
                    font: 700 32pt 'Segoe UI';
                """)
            else:
                label.setStyleSheet("""
                    color: white;
                    font: 600 20pt 'Segoe UI';
                """)
            label.setAlignment(Qt.AlignCenter)

        for button in self.see_chart_buttons:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(30, 30, 30, 0.9);  /* ciemne tło */
                    color: #FFD740;                             /* jasny żółty tekst */
                    font: bold 22pt 'Segoe UI';
                    border-radius: 18px;
                    padding: 12px 25px;
                    border: 2px solid rgba(255,255,255,0.1);   /* delikatna ramka */
                }
                QPushButton:hover {
                    background-color: rgba(50, 50, 50, 0.95);  /* jaśniejsze przy najechaniu */
                }
                QPushButton:pressed {
                    background-color: rgba(70, 70, 70, 1);     /* ciemniejszy przy kliknięciu */
                    padding-top: 3px;
                    padding-left: 3px;
                }
            """)
            button.setMinimumHeight(65)
            button.setMaximumWidth(320)

        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.move(30, int(self.height() / 2) + 80)

    def create_layout(self):

        self.upper_layout.addStretch(4)
        self.upper_layout.addWidget(self.training_name_label)
        self.upper_layout.addStretch(2)
        self.upper_layout.addWidget(self.training_duration_label)
        self.upper_layout.addStretch(2)
        self.upper_layout.setAlignment(Qt.AlignCenter)

        self.heart_rate_layout.addStretch(3)
        self.heart_rate_layout.addWidget(self.average_heart_rate_label)
        self.heart_rate_layout.addStretch(1)
        self.heart_rate_layout.addWidget(self.max_heart_rate_label)
        self.heart_rate_layout.addStretch(1)
        self.heart_rate_layout.addWidget(self.min_heart_rate_label)
        self.heart_rate_layout.addStretch(2)
        self.heart_rate_layout.addWidget(self.hear_rate_chart_button)
        self.heart_rate_layout.addStretch(2)
        self.heart_rate_layout.setAlignment(Qt.AlignCenter)

        self.spo2_layout.addStretch(3)
        self.spo2_layout.addWidget(self.average_spo2_label)
        self.spo2_layout.addStretch(1)
        self.spo2_layout.addWidget(self.max_spo2_label)
        self.spo2_layout.addStretch(1)
        self.spo2_layout.addWidget(self.min_spo2_label)
        self.spo2_layout.addStretch(2)
        self.spo2_layout.addWidget(self.spo2_chart_button)
        self.spo2_layout.addStretch(2)
        self.spo2_layout.setAlignment(Qt.AlignCenter)

        self.lower_layout.addStretch(3)
        self.lower_layout.addLayout(self.heart_rate_layout, stretch=7)
        self.lower_layout.addStretch(2)
        self.lower_layout.addLayout(self.spo2_layout, stretch=7)
        self.lower_layout.addStretch(3)
        self.lower_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addLayout(self.upper_layout, stretch=1)
        self.main_layout.addLayout(self.lower_layout, stretch=2)

        self.setLayout(self.main_layout)

    def hear_rate_chart_clicked(self):
        self.HR_chart_window = HearRateChart(directory=self.current_training_directory, hr_list=self.HR_list)
        self.HR_chart_window.showFullScreen()

    
    def spo2_chart_clicked(self):
        self.SPO2_chart_window = SPO2Chart(directory=self.current_training_directory, spo2_list=self.Spo2_list)
        self.SPO2_chart_window.showFullScreen()


