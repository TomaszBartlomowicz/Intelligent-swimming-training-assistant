"""
Training history browser for the swimming assistant.
Displays a dynamic list of completed training sessions and provides access 
to detailed performance analytics and data overview.
"""

from app_config import (PROJECT_PATH, BACKGROUND, MAIN_BUTTON_STYLE, RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE)
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout,
                             QScrollArea, QSizePolicy)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QElapsedTimer
import os

# Sub-modules for historical data visualization and management
import training_overwiev, delete_window


class TrainingHistory(QWidget):
    """
    Archive manager for completed swim workouts.
    
    Populates UI elements based on the 'finished_trainings' directory. 
    Implements a dual-interaction model: single click for analytics overview 
    and long press for record deletion.
    """

    def __init__(self):
        """Initializes the history view, screen geometry, and archival scan."""
        super().__init__()
        # Retrieve display parameters for full-screen UI scaling
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()

        self.background = QPixmap(BACKGROUND)

        # Precise timer for touch-gesture duration monitoring
        self.long_press_timer = QElapsedTimer()

        # UI Navigation
        self.return_button = QPushButton()
        self.return_button.clicked.connect(self.close)

        # --- Dynamic History Population ---
        # Fetch completed workout sessions from persistent storage
        self.finished_trainings = os.listdir(f"{PROJECT_PATH}/finished_trainings")
        self.timer_pressed_time = 0
        self.buttons = []
        
        if self.finished_trainings:
            for training_name in self.finished_trainings:
                button = QPushButton(training_name)
                # Registering press/release cycles for long-press logic
                button.pressed.connect(lambda: self.long_press_timer.start())
                button.released.connect(self.save_pressing_time)
                self.buttons.append(button)
        else:
            # Placeholder for empty archive state
            button = QPushButton(self, text="No finished trainings yet")
            button.setDisabled(True)
            self.buttons.append(button)

        # --- Layout Components ---
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.buttons_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout = QHBoxLayout()
        
        self.init_ui()
        self.layout()
        self.connect_buttons()

    def save_pressing_time(self):
        """Records the duration of the last touch event in milliseconds."""
        self.timer_pressed_time = self.long_press_timer.elapsed()

    def paintEvent(self, event):
        """Renders the pool-themed background scaled to the device display."""
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def init_ui(self):
        """Applies consistent styling to historical record entries and navigation."""
        for button in self.buttons:
            button.setStyleSheet(MAIN_BUTTON_STYLE)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(self.available_height // 6)

        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

    def layout(self):
        """Organizes the archival list into a vertically scrollable layout."""
        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        self.buttons_layout.setAlignment(Qt.AlignCenter)

        # Side-aligned return button with stretchable margins
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.return_button, stretch=1)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch=8)
        self.main_layout.addStretch(3)

        self.setLayout(self.main_layout)

    def button_clicked(self, directory, button):
        """
        Handles user interaction with historical records.
        
        Short tap (<500ms): Opens the 'TrainingOverview' for data analysis.
        Long press (>=500ms): Opens a deletion confirmation modal.
        """
        if self.timer_pressed_time >= 500:
            # Execute deletion sequence for the selected record
            window_width = int(self.available_width // 3)
            window_height = int(self.available_height // 3)
            x_cord = self.available_width // 2 - window_width // 2
            y_cord = self.available_height // 2 - window_height // 2
            
            self.delete_window = delete_window.DeleteWindow(button)
            self.delete_window.setGeometry(x_cord, y_cord, window_width, window_height)
            self.delete_window.exec_() # Modal dialog prevents background interaction

            self.timer_pressed_time = 0
        else:
            # Transition to detailed data analytics view
            self.training_window = training_overwiev.TrainingOverwiev(directory)
            self.training_window.showFullScreen()
            self.close()

    def connect_buttons(self):
        """Maps dynamic record buttons to their respective file system paths."""
        for button in self.buttons:
            directory = f"{PROJECT_PATH}/finished_trainings/{button.text()}"
            # Use default arguments in lambda to capture the current loop state
            button.clicked.connect(lambda checked=False, d=directory, b=button: self.button_clicked(d, b))