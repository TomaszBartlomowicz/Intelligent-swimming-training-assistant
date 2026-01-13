"""
Confirmation dialog for deleting training records.
Handles recursive directory removal from both planned and finished training repositories.
"""

from app_config import DELETE_BUTTON_STYLE, CANCEL_BUTTON_STYLE2, DELETE_LABEL_STYLE, PROJECT_PATH
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
import os
import shutil


class DeleteWindow(QDialog):
    """
    Modal popup triggered by a long-press gesture to remove workout data.
    
    Provides a safe way to clean up the file system by deleting training directories 
    and dynamically updating the parent UI list.
    """
    def __init__(self, button):
        """
        Initializes the deletion prompt.
        
        Args:
            button (QPushButton): The specific UI button representing the training to be deleted.
        """
        super().__init__()
        
        # UI flags for overlay behavior
        self.setWindowFlags(Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Link to the parent button to retrieve its name and trigger its removal
        self.parent_button = button
        self.button_name = self.parent_button.text()

        # Widget declarations
        self.delete_button = QPushButton(self)
        self.cancel_button = QPushButton(self)
        self.want_to_quit_label = QLabel(self)

        # Layout organization
        self.main_layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout()

        # Setup sequence
        self.init_ui()
        self.create_layout()
        self.connect_buttons()

    def init_ui(self):
        """Applies configuration-based styles and dynamic text to the dialog."""
        self.delete_button.setFixedSize(120, 120)
        self.cancel_button.setFixedSize(120, 120)
        
        self.want_to_quit_label.setText(f"Do you want to delete {self.button_name}?")
        self.delete_button.setText("Delete")
        self.cancel_button.setText("Cancel")

        # Theming from app_config
        self.delete_button.setStyleSheet(DELETE_BUTTON_STYLE)
        self.cancel_button.setStyleSheet(CANCEL_BUTTON_STYLE2)
        self.want_to_quit_label.setStyleSheet(DELETE_LABEL_STYLE)

        self.want_to_quit_label.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        """Renders a custom dark rounded rectangle background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(18, 18, 18)) # Dark theme background
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def create_layout(self):
        """Builds the vertical structure with horizontal button alignment."""
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.want_to_quit_label)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addStretch(2)

    def connect_buttons(self):
        """Binds button signals to internal logic slots."""
        self.delete_button.clicked.connect(self.delete_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def delete_clicked(self):
        """
        Executes the file system cleanup.
        
        Determines the path (planned vs finished) based on directory existence, 
        removes the folder tree, and cleans up the UI element.
        """
        training_id = self.parent_button.text()
        planned_path = f"{PROJECT_PATH}/planned_trainings/{training_id}"
        finished_path = f"{PROJECT_PATH}/finished_trainings/{training_id}"

        # File system operation: Recursive removal of the training folder
        if os.path.exists(planned_path):
            shutil.rmtree(planned_path)
        else:
            shutil.rmtree(finished_path)

        # UI operation: Safely remove the button from the parent layout
        self.parent_button.deleteLater()
        self.close()

    def cancel_clicked(self):
        """Closes the dialog without any modifications."""
        self.close()