from app_config import PARAMETERS_STYLE, LABELS_STYLE, TEXT_EDIT_STYLE, START_BUTTON_STYLE, SKIP_BUTTON_STYLE
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

from buzzer import buzzer_beep_short, buzzer_beep_long
from base_training_window import GeneralTaskWindow
import math
import time
import get_parameters
import os
import shutil


class CurrentTask(GeneralTaskWindow):
    def __init__(self, current_directory, task_number):
        super().__init__(training_directory=current_directory)
        self.is_paused = False
        self.current_training_directory = current_directory


        # Overwriting task number
        self.task_number = task_number

        # Task/time labels
        self.first_15_seconds = True
        self.current_set_label.setText("Current set:")


        # Buttons on bottom (style like TrainingWindow1)
        self.pause_or_resume_button = QPushButton(self, text="PAUSE")  # toggluje pauzę/resume
        self.next_task_button = QPushButton(self)


        self.last_beep_seconds = None

        # Timing for start/pause/resume
        self.displayed_time_start_time = time.time() 
        self.start_time = time.time()
        self.pause_clicked_time = 0
        self.resume_clicked_time = 0
        self.total_paused_time = 0
        self.limit_offset = 0

     
        self.lower_layout = QHBoxLayout()

        self.short_beep_done = False
        self.long_beep_done = False


        # Timers
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.timeout.connect(self.update_angle)   # updates angles & triggers repaint
        self.wall_clock_timer.timeout.connect(self.update_timer)   # updates text timer
        self.wall_clock_timer.start(60)

        self.parameters_timer = QTimer(self)
        self.parameters_timer.timeout.connect(lambda: self.update_parameters())
        self.parameters_timer.start(1000)

        self.time_limit_exist = False
        if self.time_limit != "None":
            self.time_limit_exist = True
            self.time_limit_splitted = self.time_limit.split("'")
            self.limit_minutes = int(self.time_limit_splitted[0])
            self.limit_seconds = int(self.time_limit_splitted[1])
            self.time_limit_in_seconds = (self.limit_minutes * 60) + self.limit_seconds

        # Build UI
        self.add_lower_layout()
        self.update_ui()
        self.connecting_buttons()
        self.pause_or_resume_button.setText("PAUSE")  # initial state
        self.resume_button = None  # not used now (kept from earlier version)
        self.get_task_info()
        self.set_task_info()
        # finalize lower layout to match TrainingWindow1 look

        self.is_last_task()

        print(self.task_number, "w current")

   
    def update_ui(self):

        # Lower layout buttons style 
        self.pause_or_resume_button.setStyleSheet(START_BUTTON_STYLE)
        self.next_task_button.setStyleSheet(SKIP_BUTTON_STYLE)
        self.next_task_button.setText("NEXT TASK")

        for button in [self.pause_or_resume_button, self.next_task_button]:
            button.setFixedHeight(50)


    def add_lower_layout(self):
        # Lower layout will be filled/updated by update_lower_layout()
        self.lower_layout.addStretch(1)
        # show start/resume and end/return like TrainingWindow1
        self.lower_layout.addWidget(self.pause_or_resume_button)
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.next_task_button)
        self.lower_layout.addStretch(30)

        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)



    def connecting_buttons(self):
        # Start button toggles pause/resume
        self.pause_or_resume_button.clicked.connect(self.pause_or_resume)
        # End button closes training (like in TrainingWindow1)
        self.next_task_button.clicked.connect(self.next_task_button_clicked)

    def pause_or_resume(self):
        if not self.is_paused:
            # Pause
            self.wall_clock_timer.stop()
            self.pause_clicked_time = time.time() - self.start_time
            self.is_paused = True
            self.pause_or_resume_button.setText("RESUME")

        else:
            # Resume
            self.wall_clock_timer.start()
            self.resume_clicked_time = time.time() - self.start_time
            # accumulate paused duration
            self.total_paused_time += self.resume_clicked_time - self.pause_clicked_time
            self.is_paused = False
            self.pause_or_resume_button.setText("PAUSE")



    def update_timer(self):
        remaining_to_start = self.start_time + 15 + self.total_paused_time - time.time()
        ## First 15 seconds - display countdown for a swimmer to get ready
        if remaining_to_start >= 0 and self.first_15_seconds: 
            seconds = self.start_time + 15 + self.total_paused_time - time.time()
            secs = round(seconds) % 60
            to_display = f"{secs}"    

            if to_display == "0":
                to_display =   "GO!"   
        
            self.clock_time = to_display

            if secs in [3, 2, 1, 0] and self.last_beep_second != secs:
                if secs == 0:
                    buzzer_beep_long()
                else:
                    buzzer_beep_short()
                    self.last_beep_second = secs
            elif secs > 3 or secs < 0:
                self.last_beep_second = None
            return

        elapsed_seconds = max(0, time.time() - (self.start_time + 14.5) - self.total_paused_time - self.limit_offset)
        secs = int(elapsed_seconds % 60)

        if self.time_limit_exist:
            remaining_seconds = self.time_limit_in_seconds - int(elapsed_seconds)

        
        ## 3, 2, 1 go! countdown before start
        if self.time_limit_exist:
            # Beep tylko jeśli nie było jeszcze beep dla tej sekundy
            if remaining_seconds in [3, 2, 1, 0] and self.last_beep_second != remaining_seconds:
                if remaining_seconds == 0:
                    buzzer_beep_long()
                else:
                    buzzer_beep_short()
                    self.last_beep_second = remaining_seconds
            # Reset flagi, gdy remaining_seconds wychodzi poza 3,2,1
            elif remaining_seconds > 3 or remaining_seconds < 0:
                self.last_beep_second = None


        mins = int(elapsed_seconds // 60)
        
        
        ## Check if time limit exists
        if self.time_limit != "None":
            ## Check if time limit has been reached
            if (mins == self.limit_minutes) and (secs == self.limit_seconds):
                self.limit_offset += self.time_limit_in_seconds


        to_display = f"{mins:02d}:{secs:02d}" 
        if to_display == "00:00":
            to_display = "GO!"  
        self.clock_time = to_display


    def update_angle(self):
        # Keep the same clock behavior (angles depend on elapsed seconds)
        current_time = time.time()
        elapsed_seconds = current_time - self.start_time - self.total_paused_time
        self.angle_0 = math.radians((elapsed_seconds * 6) % 360)
        self.angle_1 = math.radians(((elapsed_seconds + 15) * 6) % 360)
        self.angle_2 = math.radians(((elapsed_seconds + 30) * 6) % 360)
        self.angle_3 = math.radians(((elapsed_seconds + 45) * 6) % 360)
        # Repaint will be triggered by paintEvent after update_timer/ this timeout
        self.update()


    def next_task_button_clicked(self):
        self.close()   
        self.wall_clock_timer.stop()


    def finish_training(self):
        self.wall_clock_timer.stop()
        src = self.current_training_directory
        dst = "finished_trainings/" + src.split("/")[-1]
        shutil.move(src, dst)
        for window in QApplication.topLevelWidgets():
            print(window.windowTitle())
            if window.windowTitle() != "Inteligent swimer's training assistant":
                window.close()
        

    def is_last_task(self):
        if (len(os.listdir(self.current_training_directory))-1 == self.task_number):
            self.next_task_button.setStyleSheet(f"""
            background-color: #a3170d;
            color: white;
            font: bold;
            font-size: {self.font_size_3}px;
            border-radius: 10px;
            padding: 10px;
        """)
            self.next_task_button.setText("FINISH TRAINING")

            self.next_task_button.clicked.connect(self.finish_training)


