"""
Training selection module for stored workout plans.
Implements a scrollable list of planned sessions with dual-action buttons 
(Short press: Start, Long press: Delete).
"""

from app_config import (PROJECT_PATH, BACKGROUND, MAIN_BUTTON_STYLE, RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE)
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy, QLabel
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QElapsedTimer
import os

# Internal dialog and state management modules
import base_training_window, delete_window
import next_task

class ChooseTraining(QWidget):
    """
    Interface for browsing and managing planned swimming sessions.
    
    Dynamically generates buttons based on the file system structure and 
    handles workout lifecycle transitions.
    """
    def __init__(self):
        """Initializes geometry, background assets, and dynamic button mapping."""
        super().__init__()
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()

        self.background = QPixmap(BACKGROUND)

        # --- Navigation Controls ---
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)

        # --- Dynamic Training Repository Scan ---
        # Fetch directories representing individual training plans
        self.planned_trainings = os.listdir(f"{PROJECT_PATH}/planned_trainings")
        self.buttons = []
        self.timer_pressed_time = 0

        # High-resolution timer for gesture recognition (Short vs. Long press)
        self.long_press_timer = QElapsedTimer()

        if self.planned_trainings:
            for training_name in self.planned_trainings:
                button = QPushButton(training_name)
                # Map press/release events to determine interaction duration
                button.pressed.connect(lambda: self.long_press_timer.start())
                button.released.connect(self.save_pressing_time)
                self.buttons.append(button)
        else:
            # Fallback state if no trainings are found
            button = QPushButton(self, text="Add a training first")
            button.setDisabled(True)
            self.buttons.append(button)

        # --- Scrollable Viewport Structure ---
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.buttons_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout = QHBoxLayout()

        # Build UI Components
        self.init_ui()
        self.layout()
        self.connect_buttons()

    def save_pressing_time(self):
        """Captures the total duration of the button press event in milliseconds."""
        self.timer_pressed_time = self.long_press_timer.elapsed()

    def paintEvent(self, event):
        """Renders the global application background image."""
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def init_ui(self):
        """Applies configuration-based styles to dynamic buttons and the scroll area."""
        for button in self.buttons:
            button.setStyleSheet(MAIN_BUTTON_STYLE)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(self.available_height // 6)

        # Return button configuration
        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

    def layout(self):
        """Assembles the UI with a fixed return button and a dynamic scroll area."""
        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        
        self.buttons_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.return_button, stretch=1)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch=8)
        self.main_layout.addStretch(3)
        self.setLayout(self.main_layout)

    def button_clicked(self, directory, button):
        """
        Interaction dispatcher. 
        If pressed for >= 500ms, triggers deletion; otherwise, starts the workout.
        """
        if self.timer_pressed_time >= 500:
            # --- Deletion Workflow ---
            window_width = int(self.available_width // 3)
            window_height = int(self.available_height // 3)
            x_cord = self.available_width // 2 - window_width // 2
            y_cord = self.available_height // 2 - window_height // 2
            
            self.delete_window = delete_window.DeleteWindow(button)
            self.delete_window.setGeometry(x_cord, y_cord, window_width, window_height)
            self.delete_window.exec_() # Modal confirmation dialog

            self.timer_pressed_time = 0
        else:
            # --- Activation Workflow ---
            self.training_window = next_task.NextTask(directory)
            self.training_window.showFullScreen()

    def connect_buttons(self):
        """Maps directory paths to button click events using lambda closures."""
        for button in self.buttons:
            training_path = f"{PROJECT_PATH}/planned_trainings/{button.text()}" 
            button.clicked.connect(lambda checked=False, d=training_path, b=button: self.button_clicked(d, b))