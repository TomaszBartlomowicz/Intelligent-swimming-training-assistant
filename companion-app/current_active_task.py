"""
Active training execution module.
Handles real-time pool clock animation, multi-stage countdowns, 
synchronized buzzer signaling, and final session archiving.
"""

from app_config import PROJECT_PATH, PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, SKIP_BUTTON_STYLE
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

# Hardware and communication interfaces
from buzzer import buzzer_beep_short, buzzer_beep_long
from base_training_window import GeneralTaskWindow
import math
import time
import bluetooth_connection
import os
import shutil
import json
from datetime import datetime

class CurrentTask(GeneralTaskWindow):
    """
    Controller for the active swimming set.
    
    Manages the 15s 'pre-start' countdown, recurring time limits, 
    BLE pacer synchronization, and session persistent storage.
    """
    def __init__(self, current_directory, task_number):
        """Initializes the active workout state with pause/resume logic and task metadata."""
        super().__init__(training_directory=current_directory)
        self.is_paused = False
        self.current_training_directory = current_directory
        self.task_number = task_number

        # --- State Management ---
        self.first_15_seconds = True
        self.current_set_label.setText("Current set:")
        self.last_beep_second = None # Tracks beep events to prevent duplicates per second

        # Navigation Controls
        self.pause_or_resume_button = QPushButton(self, text="PAUSE")
        self.next_task_button = QPushButton(self)

        # --- Timing Engine ---
        self.start_time = time.time()
        self.pause_clicked_time = 0
        self.total_paused_time = 0
        self.limit_offset = 0

        self.lower_layout = QHBoxLayout()

        # High-frequency timer for smooth UI/Clock updates
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.timeout.connect(self.update_angle) 
        self.wall_clock_timer.timeout.connect(self.update_timer)
        self.wall_clock_timer.start(60)

        # Load task parameters
        self.get_task_info()
        self.set_task_info()

        # --- Time Limit Logic ---
        self.time_limit_exist = False
        if self.time_limit != "None":
            self.time_limit_exist = True
            minutes, seconds = self.time_limit.split("'")
            self.limit_minutes, self.limit_seconds = int(minutes), int(seconds)
            self.time_limit_in_seconds = (self.limit_minutes * 60) + self.limit_seconds

        # Build Interface
        self.add_lower_layout()
        self.update_ui()
        self.connecting_buttons()
        self.is_last_task()

    def update_ui(self):
        """Applies styles to active workout control buttons."""
        self.pause_or_resume_button.setStyleSheet(START_BUTTON_STYLE)
        self.next_task_button.setStyleSheet(SKIP_BUTTON_STYLE)
        self.next_task_button.setText("NEXT TASK")

        for button in [self.pause_or_resume_button, self.next_task_button]:
            button.setFixedHeight(50)

    def add_lower_layout(self):
        """Assembles the footer layout with responsive spacing."""
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.pause_or_resume_button)
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.next_task_button)
        self.lower_layout.addStretch(30)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

    def connecting_buttons(self):
        """Maps signals to session control logic."""
        self.pause_or_resume_button.clicked.connect(self.pause_or_resume)
        self.next_task_button.clicked.connect(self.next_task_button_clicked)

    def pause_or_resume(self):
        """Toggles the execution state, managing timer suspension and duration offset."""
        if not self.is_paused:
            self.wall_clock_timer.stop()
            self.pause_clicked_time = time.time() - self.start_time
            self.is_paused = True
            self.pause_or_resume_button.setText("RESUME")
        else:
            self.wall_clock_timer.start()
            resume_time = time.time() - self.start_time
            self.total_paused_time += resume_time - self.pause_clicked_time
            self.is_paused = False
            self.pause_or_resume_button.setText("PAUSE")

    def update_timer(self):
        """
        Core logic for the digital display and synchronized signaling.
        Handles the 15s preparation countdown and recurring intervals.
        """
        # --- Pre-start Phase (15s Countdown) ---
        remaining_to_start = self.start_time + 15 + self.total_paused_time - time.time()
        
        if remaining_to_start >= 0 and self.first_15_seconds: 
            secs = round(remaining_to_start) % 60
            to_display = f"{secs}" if secs > 0 else "GO!"
            self.clock_time = to_display

            # Trigger BLE pacer command exactly at GO!
            if to_display == "GO!":
                try:
                    with open(f"{self.current_training_directory}/Task {self.task_number}.json", "r") as file:
                        task_data = json.load(file)
                        p_min, p_sec = task_data.get("pacer", "0'00").split("'")
                        interval = int(p_min) * 60 + int(p_sec)
                        bluetooth_connection.send_timer_seconds(interval)
                except Exception: pass

            # Physical Buzzer Countdown (3, 2, 1, Long Beep at 0)
            if secs in [3, 2, 1, 0] and self.last_beep_second != secs:
                if secs == 0: buzzer_beep_long()
                else: buzzer_beep_short()
                self.last_beep_second = secs
            return

        # --- Active Task Phase ---
        elapsed = max(0, time.time() - (self.start_time + 14.5) - self.total_paused_time - self.limit_offset)
        secs, mins = int(elapsed % 60), int(elapsed // 60)

        # Handle recurring time limits (Interval-based countdowns)
        if self.time_limit_exist:
            remaining = self.time_limit_in_seconds - int(elapsed)
            
            # Local buzzer signaling for the end of an interval
            if remaining in [3, 2, 1, 0] and self.last_beep_second != remaining:
                if remaining == 0: buzzer_beep_long()
                else: buzzer_beep_short()
                self.last_beep_second = remaining
            elif remaining > 3: self.last_beep_second = None

            # Reset timer for the next interval in the set
            if mins == self.limit_minutes and secs == self.limit_seconds:
                self.limit_offset += self.time_limit_in_seconds

        to_display = f"{mins:02d}:{secs:02d}"
        self.clock_time = "GO!" if to_display == "00:00" else to_display

    def update_angle(self):
        """Calculates clock arrow positions relative to the net workout duration."""
        elapsed = time.time() - self.start_time - self.total_paused_time
        for i in range(4):
            # 6 degrees per second per arrow with 15s offsets
            angle_rad = math.radians(((elapsed + (i * 15)) * 6) % 360)
            setattr(self, f"angle_{i}", angle_rad)
        self.update()

    def next_task_button_clicked(self):
        """Gracefully closes the current set and disables the BLE pacer."""
        bluetooth_connection.send_timer_seconds(0)
        self.wall_clock_timer.stop()
        self.close()

    def finish_training(self):
        """
        Concludes the entire session. 
        Logs the end timestamp, moves the directory to archives, and cleans up UI.
        """
        # Log session termination time
        with open(f"{self.current_training_directory}/training_data.txt", "a") as file:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"------------------------------\n")
            file.write(f"SESSION END: {end_time}\n")

        self.wall_clock_timer.stop()
        bluetooth_connection.send_timer_seconds(0)

        # Directory relocation: Planned -> Finished
        src = self.current_training_directory
        dst = os.path.join(PROJECT_PATH, "finished_trainings", src.split("/")[-1])
        try:
            shutil.move(src, dst)
        except Exception as e: print(f"Move error: {e}")

        # Safety: Close all auxiliary windows and return to main dashboard
        for window in QApplication.topLevelWidgets():
            if window.windowTitle() != "Inteligent swimer's training assistant":
                window.close()

    def is_last_task(self):
        """Dynamically reconfigures the 'Next' button if no more tasks remain."""
        if len(os.listdir(self.current_training_directory)) - 1 == self.task_number:
            self.next_task_button.setStyleSheet("background-color: #a3170d; color: white; "
                                                "font: 650 24pt 'Segoe UI'; border-radius: 10px; padding: 10px;")
            self.next_task_button.setText("FINISH TRAINING")
            # Unlink previous connection and bind to finish_training
            try: self.next_task_button.clicked.disconnect()
            except: pass
            self.next_task_button.clicked.connect(self.finish_training)

    def closeEvent(self, event):
        """Ensures polling threads are terminated to prevent memory leaks."""
        self.parameters_timer.stop()