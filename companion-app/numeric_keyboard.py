"""
Numeric virtual keyboard module for embedded touch interfaces.
Provides a specialized input dialog for age, distance, and repetition entry 
without requiring physical peripherals.
"""

import sys
from PyQt5.QtWidgets import QWidget, QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QLineEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt

class NumericKeyboard(QDialog):
    """
    Modal numeric keypad designed for high-visibility and touch-screen accuracy.
    
    Supports dynamic targeting of QLineEdit and QPlainTextEdit widgets, 
    featuring specialized backspace and enter functionality.
    """
    def __init__(self, target_line_edit=None):
        """Initializes the keypad layout and screen-relative geometry."""
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()
        
        self.setWindowTitle("Numeric Keyboard")
        self.setWindowFlags(Qt.Popup) # Borderless window that closes on lost focus
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.target_line_edit = target_line_edit

        # Define keyboard character mapping
        self.keyboard_rows = {
            "first_row": ["1", "2", "3"],
            "second_row": ["4", "5", "6"],
            "third_row": ["7", "8", "9"],
            "fourth_row": ["⌫", "0", "↵"],
        }

        self.buttons = []
        self.layouts = {
            "first_row": QHBoxLayout(),
            "second_row": QHBoxLayout(),
            "third_row": QHBoxLayout(),
            "fourth_row": QHBoxLayout()
        }

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.init_ui()
        self.create_keyboard()

    def init_ui(self):
        """Applies global stylesheet for high-contrast touch buttons."""
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 50, 70, 200);
                border: 1px solid rgba(0, 188, 212, 80);
                color: #E0F7FA;
                font-size: 22pt;
                font-weight: 600;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 188, 212, 150);
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(0, 188, 212, 220);
                color: #ffffff;
                border: 1px solid #00BCD4;
            }
        """)

    def paintEvent(self, event):
        """Renders the semi-transparent rounded background for the keyboard container."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(15, 25, 35, 220)) # Dark translucent theme
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)  

    def create_keyboard(self):
        """Dynamically instantiates buttons and binds them to input logic."""
        for row_name, keys in self.keyboard_rows.items():
            row_layout = self.layouts[row_name]
            row_layout.setSpacing(8)
            row_layout.addStretch(1)
            
            for key in keys:
                button = QPushButton(key)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(self.available_width // 21, self.available_height // 15)
                
                # Assign logic based on key type
                if key == "⌫":
                    button.clicked.connect(self.backspace)
                elif key == "↵":
                    button.clicked.connect(self.enter)
                else:
                    # Closure using k=key to ensure correct character mapping in loop
                    button.clicked.connect(lambda checked, k=key: self.add_text(k))
                    self.buttons.append(button)
                    
                row_layout.addWidget(button)
            
            row_layout.addStretch(1)
            self.main_layout.addLayout(row_layout)

        self.setLayout(self.main_layout)

    def add_text(self, text):
        """Inserts text at current cursor position in the target widget."""
        if not self.target_line_edit:
            return

        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.insert(text)
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            self.target_line_edit.insertPlainText(text)
    
    def enter(self):
        """Finalizes input, removes focus, and closes the keyboard dialog."""
        if self.target_line_edit:
            self.target_line_edit.clearFocus()
        self.close()

    def backspace(self):
        """Handles character deletion for different Qt input widget types."""
        if not self.target_line_edit:
            return

        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.backspace()
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            cursor = self.target_line_edit.textCursor()
            cursor.deletePreviousChar()
            self.target_line_edit.setTextCursor(cursor)

    def set_target(self, line_edit):
        """Binds a specific input widget to the keyboard for character redirection."""
        self.target_line_edit = line_edit