import json
import sys
from app_config import RETURN_BUTTON_STYLE, PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, END_BUTTON_STYLE
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
import training_window2
from base_training_window import GeneralTaskWindow
import get_parameters
import math
import os



class NextTask(GeneralTaskWindow):
    def __init__(self, training_directory):
        # przekazujemy katalog do klasy bazowej (bazowa ustawi self.current_training_directory)
        super().__init__(training_directory=training_directory)

        # Declaring buttons and labels
        self.task_label = QLabel(self)
        self.start_button = QPushButton(self, text="START")
        self.end_button = QPushButton(self, text="END TRAINING")
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)
        self.lower_layout_buttons = [self.return_button, self.start_button, self.end_button]
        self.current_set_label.setText("Next set:")

        self.connecting_buttons()
        self.add_lower_layout()
        self.update_ui()

        # w GUI, w __init__:
        #get_parameters.start_ble()  # startuje BLE w tle

        # Start timera odczytującego wartości co sekundę
        self.parameters_timer.start(1000)



    def update_ui(self):        
        ## Start button
        self.start_button.setStyleSheet(START_BUTTON_STYLE)

        ## End button
        self.end_button.setStyleSheet(END_BUTTON_STYLE)
        
        ## Return button 
        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        for button in self.lower_layout_buttons:
            button.setFixedHeight(50)
              

    def add_lower_layout(self):
        self.lower_layout.addStretch(2)
        self.lower_layout.addWidget(self.start_button)
        self.lower_layout.addStretch(2)
        self.lower_layout.addWidget(self.end_button)
        self.lower_layout.addStretch(30)
        self.lower_layout.addWidget(self.return_button)
        self.lower_layout.addStretch(1)

        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)



    def start_button_clicked(self):
        self.training_window = training_window2.CurrentTask(current_directory=self.current_training_directory)
        
        if (len(os.listdir(self.current_training_directory))-1>self.task_number):
            self.task_number += 1
        self.get_task_info()
        self.set_task_info()

        self.training_window.showFullScreen()


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



    def start_button_clicked(self):
        self.training_window = training_window2.CurrentTask(current_directory=self.current_training_directory, task_number=self.task_number)
        if (len(os.listdir(self.current_training_directory))-1>self.task_number):
            self.task_number += 1

        self.get_task_info()
        self.set_task_info()

        self.training_window.showFullScreen()

    def connecting_buttons(self):
        self.start_button.clicked.connect(self.start_button_clicked)
