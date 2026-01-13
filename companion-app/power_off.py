"""
Modal popup for system shutdown execution.
Triggers a sudo shutdown command and handles UI exit or cancellation.
"""
import os
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor

# Internal configuration for UI styling
from app_config import POWER_OFF_BUTTON_STYLE, CANCEL_BUTTON_STYLE, QUIT_LABEL_STYLE


class PowerOff(QDialog):
    """
    Modal dialog for handling system power-off sequences.
    
    Features a translucent, rounded-rect design for touch-screen optimization
    and direct integration with OS-level shutdown commands.
    """

    def __init__(self):
        """Initializes the power-off prompt and custom window flags."""
        super().__init__()
        
        # UI flags for overlay appearance
        self.setWindowFlags(Qt.Popup) # Frameless, stays on top
        self.setAttribute(Qt.WA_TranslucentBackground) # Required for paintEvent transparency

        # Widget declarations
        self.power_off_button = QPushButton(self)
        self.cancel_button = QPushButton(self)
        self.want_to_quit_label = QLabel(self)

        # Layout organization
        self.main_layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout()

        # Component setup
        self.init_ui()
        self.create_layout()
        self.connect_buttons()

    def init_ui(self):
        """Sets widget content, fixed dimensions, and CSS styles."""
        self.power_off_button.setFixedSize(180, 180)
        self.cancel_button.setFixedSize(180, 180)
        
        self.want_to_quit_label.setText("Do you really want to quit?")
        self.power_off_button.setText("Power Off")
        self.cancel_button.setText("Cancel")

        # Apply pre-defined styles from app_config
        self.power_off_button.setStyleSheet(POWER_OFF_BUTTON_STYLE)
        self.cancel_button.setStyleSheet(CANCEL_BUTTON_STYLE)
        self.want_to_quit_label.setStyleSheet(QUIT_LABEL_STYLE)

        self.want_to_quit_label.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        """Custom painter to render a rounded, semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent white background (RGBA)
        brush = QBrush(QColor(255, 255, 255, 240))  
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def create_layout(self):
        """Assembles the UI grid using stretch factors for responsive spacing."""
        # Horizontal button arrangement
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.power_off_button)
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addStretch(1)

        # Vertical stack for labels and button bar
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.want_to_quit_label)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addStretch(2)

    def connect_buttons(self):
        """Binds UI signals to system-level and dialog actions."""
        self.power_off_button.clicked.connect(self.power_off_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def power_off_clicked(self):
        """Executes a system-level shutdown command with superuser privileges."""
        os.system("sudo shutdown now")

    def cancel_clicked(self):
        """Closes the dialog and returns focus to the MainWindow."""
        self.close()