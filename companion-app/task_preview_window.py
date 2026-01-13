"""
Overview module for upcoming training tasks with session timestamping.
Inherits from GeneralTaskWindow to display parameters before workout activation 
and handles the initial session logging.
"""

import json
import sys
from app_config import PROJECT_PATH, RETURN_BUTTON_STYLE, PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, END_BUTTON_STYLE
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
import current_active_task
from base_training_window import GeneralTaskWindow
import bluetooth_connection
import os
from datetime import datetime
import math 

class NextTask(GeneralTaskWindow):
    """
    UI controller for the 'Pre-task' state. 

    """
    def __init__(self, training_directory):
        """Initializes the window with workout context and navigation controls."""
        # Initialize base class (GeneralTaskWindow) with current workout path
        super().__init__(training_directory=training_directory)

        # --- Button and Label Declarations ---
        self.start_button = QPushButton(self, text="START")
        self.end_button = QPushButton(self, text="END TRAINING")
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)
        
        self.lower_layout_buttons = [self.return_button, self.start_button, self.end_button]
        self.current_set_label.setText("Next set:")

        # Component assembly
        self.connecting_buttons()
        self.add_lower_layout()
        self.update_ui()

    def update_ui(self):         
        """Applies styles and icons to the workout navigation bar."""
        self.start_button.setStyleSheet(START_BUTTON_STYLE)
        self.end_button.setStyleSheet(END_BUTTON_STYLE)
        
        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        
        for button in self.lower_layout_buttons:
            button.setFixedHeight(50)

    def add_lower_layout(self):
        """Builds the footer navigation layout."""
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
        """
        Transitions the system to active training state.
        Handles the critical 'First Task' logic: logs the session start time 
        before starting telemetry acquisition.
        """
        log_path = f"{self.current_training_directory}/training_data.txt"
        
        with open(log_path, "a") as file:
            # Session Initialization: Capture timestamp only on Task 1
            if self.task_number == 1:
                # Capture current system time (Raspberry Pi local clock)
                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"SESSION START: {start_time}\n")
                file.write("------------------------------\n")
            
            # Record task-specific separator in the telemetry file
            file.write(f"-----TASK{self.task_number}-----\n")

        # Instantiate the active task execution window (CurrentTask)
        self.training_window = current_active_task.CurrentTask(
            current_directory=self.current_training_directory, 
            task_number=self.task_number
        )
        self.training_window.showFullScreen()

        # Update index for the background task pre-loader
        QTimer.singleShot(10, self.load_next_task)

    def load_next_task(self):
        """
        Increments task index and pre-loads next task metadata from JSON.
        Ensures continuous workout flow without UI interruption.
        """
        # Directory check logic to confirm more tasks are available
        if (len(os.listdir(self.current_training_directory)) - 1 > self.task_number):
            self.task_number += 1
            
            # Inherited methods from base class to refresh UI content
            self.get_task_info()
            self.set_task_info()

    def connecting_buttons(self):
        """Maps UI signals to transition logic."""
        self.start_button.clicked.connect(self.start_button_clicked)

    def closeEvent(self, event):
        """Stops the telemetry polling timer to prevent background resource leaks."""
        self.parameters_timer.stop()