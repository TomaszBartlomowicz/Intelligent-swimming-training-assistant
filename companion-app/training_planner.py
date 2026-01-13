"""
Training Planner Module.
Handles the creation of new swimming workout routines by generating directory 
structures and managing task sequences through a dynamic UI.
"""

from app_config import (PROJECT_PATH, BACKGROUND, PLAN_WINDOW_PLUS_BUTTON_STYLE, SAVE_BUTTON_STYLE,
                        RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE, TRAINING_NAME_STYLE, MSG_STYLE)
import os
from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
    QSizePolicy, QLineEdit, QScrollArea)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
import math, time, shutil

# Internal components for input and task configuration
import virtual_keyboard, add_task

class PlanTraining(QWidget):
    """
    Interface for defining new training sessions.
    Manages filesystem operations (mkdir) and coordinates the flow 
    between naming a session and adding individual tasks.
    """
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()
        
        # Background scaling for responsive full-screen display
        self.background = QPixmap(BACKGROUND)
        self.background = self.background.scaled(self.available_width, self.available_height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Initializing buttons
        self.plus_button = QPushButton(self)
        self.save_button = QPushButton(self)
        self.return_button = QPushButton(self)
        self.save_button.hide() # Hidden until the first task is created

        # Operational Flags
        self.training_name_accepted = False
        self.is_training_created = False
        
        # Virtual keyboard integration for touchscreen data entry
        self.keyboard = virtual_keyboard.VirtualKeyboard()

        self.training_name = QLineEdit(self)
        self.task_counter = 1

        # Configuration of the warning message box for validation
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setWindowFlags(Qt.Popup)
        self.msg.setAttribute(Qt.WA_TranslucentBackground)

        # UI Layout architecture
        self.upper_layout = QHBoxLayout()
        self.training_name_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.plus_layout = QHBoxLayout()
        self.return_button_layout = QHBoxLayout()
        
        # Scrollable area for dynamic task list
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.adding_tasks_layout = QVBoxLayout(self.scroll_widget)
        
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        # Initialization sequence
        self.init_ui()
        self.layout_setting()
        self.connect_buttons()
        self.connect_line_edit_to_keyboard()

    def paintEvent(self, event):
        """Renders the global application background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawPixmap(0, 0, self.background)

    def init_ui(self):
        """Sets styling and fixed dimensions for interactive elements."""
        self.plus_button.setFixedSize(90, 80)
        self.plus_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.plus_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/plus.png"))
        self.plus_button.setIconSize(QSize(60, 60))
        
        self.save_button.setText("Save")
        self.save_button.setStyleSheet(SAVE_BUTTON_STYLE)
        self.save_button.setMaximumWidth(self.available_width // 4)

        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        # Validation for Training Name Input
        self.training_name.setStyleSheet(TRAINING_NAME_STYLE)
        self.training_name.setAlignment(Qt.AlignCenter)
        self.training_name.setPlaceholderText("Enter training name!")
        self.training_name.setMaximumHeight(self.available_height // 8)
        self.training_name.setMinimumWidth(self.available_width // 3)

        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)
        self.msg.setStyleSheet(MSG_STYLE)

    def layout_setting(self):
        """Assembles the UI hierarchy into the main layout."""
        self.training_name_layout.addStretch(12)
        self.training_name_layout.addWidget(self.training_name)
        self.training_name_layout.addStretch(12)

        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.save_button, stretch=5)
        self.lower_layout.addStretch(1)

        self.return_button_layout.addStretch(2)
        self.return_button_layout.addWidget(self.return_button)
        self.return_button_layout.addStretch(20)
        self.return_button_layout.addWidget(self.plus_button)
        self.return_button_layout.addStretch(2)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.training_name_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch=8)
        self.main_layout.addLayout(self.return_button_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)
        
        self.setLayout(self.main_layout)

    def plus_clicked(self):
        """
        Logic for adding a new task. 
        Validates the training name, creates the physical directory on disk, 
        and launches the task configuration window.
        """
        training_name = self.training_name.text()
        
        # Verification: Prevent empty training names
        if not training_name:
            self.msg.setText("Enter training name first!")
            self.msg.setWindowTitle("No trainign name chosen")
            self.msg.show() 
            return

        # Verification: Prevent overwriting existing trainings
        if not self.is_training_created:
            if training_name in os.listdir(f"{PROJECT_PATH}/planned_trainings"):
                self.msg.setText("Choose a different training name!")
                self.msg.setWindowTitle("Training name already exists!")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.show()
                return

        # Lock the training name once tasks begin to be added
        self.training_name.setDisabled(True)
        
        new_layout = QHBoxLayout()
        task_label = QLabel()
        task_label.setText("Task " + str(self.task_counter))
        task_name = task_label.text()

        new_layout.addStretch(21)
        new_layout.addWidget(task_label)
        new_layout.addStretch(20)

        index = self.adding_tasks_layout.indexOf(self.plus_layout)
        self.adding_tasks_layout.insertLayout(index, new_layout)
        self.adding_tasks_layout.insertStretch(index, 1)

        task_label.setStyleSheet("color: white;"
                                f"font: 30px 'Segoe UI';"
                                "font-weight: bold;")
        
        self.save_button.show()
        
        # Filesystem Operation: Create directory for the new training session
        if not self.is_training_created:
            os.mkdir(f"{PROJECT_PATH}/planned_trainings/{training_name}")
            with open(f"{PROJECT_PATH}/planned_trainings/{training_name}/training_data.txt", 'w') as file:
                file.write(f"Training Name: {training_name}\n")

        self.is_training_created = True
        self.task_counter += 1

        # Open task editor window
        self.task_window = add_task.AddTask(training_name, task_name)
        self.task_window.showFullScreen()

    def connect_buttons(self):
        """Binds UI signals to internal slots."""
        self.save_button.clicked.connect(self.save_button_clicked)
        self.plus_button.clicked.connect(self.plus_clicked)
        self.return_button.clicked.connect(self.return_button_clicked)

    def save_button_clicked(self):
        """Finalizes training creation and exits."""
        self.close()

    def return_button_clicked(self):
        """
        Abort logic. 
        If a training was partially created on disk, it is removed recursively.
        """
        training_name = self.training_name.text().strip()
        
        if not training_name:
            self.close()
            return

        # Cleanup: Remove partially created directory if operation is cancelled
        if os.path.exists(f"{PROJECT_PATH}/planned_trainings/{training_name}"):
            shutil.rmtree(f"{PROJECT_PATH}/planned_trainings/{training_name}")
        self.close()

    def connect_line_edit_to_keyboard(self):
        """Overrides mouse press to trigger virtual keyboard on touchscreen."""
        self.training_name.mousePressEvent = lambda event: self.show_keyboard(event)

    def show_keyboard(self, event):
        """Configures and displays the full alphanumeric virtual keyboard."""
        self.keyboard.set_target(self.training_name)

        keyboard_width = int(self.available_width // 1.15)
        keyboard_height = int(self.available_height // 2)
        x_cord = (self.available_width - keyboard_width) // 2
        y_cord = self.available_height // 2 - keyboard_height // 2 - 35
        
        self.keyboard.setGeometry(x_cord, y_cord, keyboard_width, keyboard_height)
        self.keyboard.show()
        return QLineEdit.mousePressEvent(self.training_name, event)