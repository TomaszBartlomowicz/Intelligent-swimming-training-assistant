import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime


class TrainingOverwiev(QWidget):
    def __init__(self, directory):
        super().__init__()

        self.background = QPixmap("icons/basen3.jpg")
        self.trainig_name = directory.split("/")[1]

        self.training_name_label = QLabel(self)
        self.training_duration_label = QLabel(self)
        self.total_disctance_label = QLabel(self)
        self.average_heart_rate_label = QLabel(self)
        self.max_heart_rate_label = QLabel(self)
        self.min_heart_rate_label = QLabel(self)
        self.average_spo2_label = QLabel(self)
        self.max_spo2_label = QLabel(self)
        self.min_spo2_label = QLabel(self)

        self.labels = [self.training_name_label, self.training_duration_label, self.total_disctance_label,
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
        self.spo2_chart_button = QPushButton(self)

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


        # Calling necessary functions

        self.init_ui()
        self.create_layout()
        self.get_parametrs_values()
        self.set_labels_text()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)


        color = QColor(0, 0, 0, 180)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(200, 280, int(self.width() - 400), 280, 25.0, 25.0)
        painter.end()


    def get_parametrs_values(self):

        self.average_heart_rate = "130 bpm"
        self.max_heart_rate = "190 bpm"
        self.min_heart_rate = "100 bpm"
        self.average_spo2 = "97%"
        self.max_spo2 = "99%"
        self.min_spo2 = "94%"

    def set_labels_text(self):

        self.training_name_label.setText(self.trainig_name)
        self.training_duration_label.setText("Training Duration: 1h 25m")
        self.total_disctance_label.setText("Total Disctance: 3.9km")
        self.average_heart_rate_label.setText("Average H: " + str(self.average_heart_rate))
        self.max_heart_rate_label.setText("Max HR: " + str(self.max_heart_rate))
        self.min_heart_rate_label.setText("Min HR): " + str(self.min_heart_rate))

        self.average_spo2_label.setText("Average SpO₂: " + str(self.average_spo2))
        self.max_spo2_label.setText("Max SpO₂: " + str(self.max_spo2))
        self.min_spo2_label.setText("Min SpO₂: " + str(self.min_spo2))

        self.hear_rate_chart_button.setText("Heart Rate Chart")
        self.spo2_chart_button.setText("Saturation Chart")

    def init_ui(self):

        for label in self.labels:
            if label == self.training_name_label:
                label.setStyleSheet("color: yellow;"
                                      "font: bold;"
                                      "font-size: 35px;")
            else:
                label.setStyleSheet("color: white;"
                                          "font: bold;"
                                          "font-size: 25px;")
            label.setAlignment(Qt.AlignCenter)

        # for parameter in self.parameters:
        #     parameter.setStyleSheet("color: red;"
        #                                   "font: bold;"
        #                                   "font-size: 35px;")

        for button in self.see_chart_buttons:
            button.setStyleSheet(""" 
                        QPushButton {
                                             background-color: rgba(0, 0, 0, 0.8);
                                             color: red;
                                             font: 25px 'Segoe UI';
                                             font-weight: bold;
                                             border-radius: 15px;
                                             }

                        QPushButton:pressed {
                                            background-color: rgba(25, 25, 25, 0.8);
                                            padding-top: 3px;
                                            padding-left: 3px;
                        }
                        """
                                               )

            button.setMinimumHeight(60)
            button.setMaximumWidth(300)


        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setStyleSheet(""" 
                    QPushButton {
                                         background-color: rgba(0, 0, 0, 0.8);
                                         color: white;
                                         font: 30px 'Segoe UI';
                                         font-weight: bold;
                                         border-radius: 15px;
                                         }

                    QPushButton:pressed {
                                        background-color: rgba(25, 25, 25, 0.8);
                                        padding-top: 3px;
                                        padding-left: 3px;
            }
                    """)
        self.return_button.setIconSize(QSize(60, 60))
        self.return_button.setMaximumWidth(80)

    def create_layout(self):

        self.upper_layout.addStretch(4)
        self.upper_layout.addWidget(self.training_name_label)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.training_duration_label)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.total_disctance_label)
        self.upper_layout.addStretch(2)
        self.upper_layout.setAlignment(Qt.AlignCenter)

        self.heart_rate_layout.addStretch(2)
        self.heart_rate_layout.addWidget(self.average_heart_rate_label)
        self.heart_rate_layout.addStretch(1)
        self.heart_rate_layout.addWidget(self.max_heart_rate_label)
        self.heart_rate_layout.addStretch(1)
        self.heart_rate_layout.addWidget(self.min_heart_rate_label)
        self.heart_rate_layout.addStretch(1)
        self.heart_rate_layout.addWidget(self.hear_rate_chart_button)
        self.heart_rate_layout.addStretch(2)
        self.heart_rate_layout.setAlignment(Qt.AlignCenter)

        self.spo2_layout.addStretch(2)
        self.spo2_layout.addWidget(self.average_spo2_label)
        self.spo2_layout.addStretch(1)
        self.spo2_layout.addWidget(self.max_spo2_label)
        self.spo2_layout.addStretch(1)
        self.spo2_layout.addWidget(self.min_spo2_label)
        self.spo2_layout.addStretch(1)
        self.spo2_layout.addWidget(self.spo2_chart_button)
        self.spo2_layout.addStretch(2)
        self.spo2_layout.setAlignment(Qt.AlignCenter)

        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.return_button, stretch=1)
        self.lower_layout.addStretch(1)
        self.lower_layout.addLayout(self.heart_rate_layout, stretch=7)
        self.lower_layout.addStretch(2)
        self.lower_layout.addLayout(self.spo2_layout, stretch=7)
        self.lower_layout.addStretch(3)
        self.lower_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addLayout(self.upper_layout, stretch=1)
        self.main_layout.addLayout(self.lower_layout, stretch=2)

        self.setLayout(self.main_layout)



