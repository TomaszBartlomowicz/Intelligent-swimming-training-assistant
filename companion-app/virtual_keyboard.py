"""
Full alphanumeric virtual keyboard for embedded touch interfaces.
Provides comprehensive text input capabilities including Shift/Caps Lock logic 
and multi-line support for task descriptions.
"""

import sys
from PyQt5.QtWidgets import QWidget, QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QLineEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt

class VirtualKeyboard(QDialog):
    """
    Alphanumeric QWERTY keyboard dialog optimized for touchscreen use.
    
    Features dynamic case switching (Shift/Caps), specialized function keys, 
    and target-based text redirection.
    """
    def __init__(self, target_line_edit=None):
        """Initializes geometry and keyboard mapping layout."""
        super().__init__()

        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()
        
        self.setWindowTitle("Virtual Keyboard")
        self.setWindowFlags(Qt.Popup) # Closes when clicking outside
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.target_line_edit = target_line_edit
        
        # Alphanumeric layout mapping
        self.keyboard_rows = {
            "numeric": ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "⌫"],
            "first_row": ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            "second_row": ["Caps  ", "a", "s", "d", "f", "g", "h", "j", "k", "l", ":"],
            "third_row": ["Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
            "fourth_row": [" ↲ ", "        Space        ", " Enter "]
        }

        self.buttons = []
        self.is_caps_clicked = False
        self.is_shift_clicked = False

        self.layouts = {
            "numeric": QHBoxLayout(),
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
        """Applies global CSS for a modern dark-themed interactive UI."""
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
        """Renders the keyboard background with rounded corners."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(15, 25, 35)) # Deep navy background
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)  

    def create_keyboard(self):
        """Dynamically builds the keyboard interface and binds key signals."""
        for row_name, keys in self.keyboard_rows.items():
            row_layout = self.layouts[row_name]
            row_layout.setSpacing(8)
            row_layout.addStretch(1)
            
            for key in keys:
                button = QPushButton(key)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(self.available_width // 19, self.available_height // 13)
                
                # --- Map Special Function Keys ---
                if key == "⌫":
                    button.clicked.connect(self.backspace)
                elif key == " Enter ":
                    button.clicked.connect(self.enter)
                elif key == "        Space        ":
                    button.clicked.connect(lambda: self.add_text(" "))
                elif key == " ↲ ":
                    button.clicked.connect(lambda: self.add_text("\n"))
                elif key == "Tab":
                    button.clicked.connect(lambda: self.add_text("\t"))
                elif key == "Caps  ":
                    button.clicked.connect(self.caps_clicked)    
                elif key == "Shift":
                    button.clicked.connect(self.shift_clicked) 
                else:
                    # Map standard characters
                    button.clicked.connect(lambda checked, k=key: self.add_text(k))
                    button.clicked.connect(self.is_shift_active) # Auto-revert Shift
                    self.buttons.append(button)
                    
                row_layout.addWidget(button)
            
            row_layout.addStretch(1)
            self.main_layout.addLayout(row_layout)

        self.setLayout(self.main_layout)

    def add_text(self, text):
        """Processes character input with case sensitivity check."""
        if not self.target_line_edit:
            return
        
        # Apply uppercase if Shift or Caps Lock is active
        text_to_add = text.upper() if (self.is_caps_clicked or self.is_shift_clicked) else text

        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.insert(text_to_add)
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            self.target_line_edit.insertPlainText(text_to_add)
    
    def enter(self):
        """Commits input and releases focus."""
        if self.target_line_edit:
            self.target_line_edit.clearFocus()
        self.close()

    def backspace(self):
        """Safely removes the previous character for both single and multi-line widgets."""
        if not self.target_line_edit:
            return

        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.backspace()
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            cursor = self.target_line_edit.textCursor()
            cursor.deletePreviousChar()
            self.target_line_edit.setTextCursor(cursor)

    def set_target(self, line_edit):
        """Sets the focus widget for incoming keystrokes."""
        self.target_line_edit = line_edit

    def caps_clicked(self):
        """Toggles permanent uppercase mode for all letter buttons."""
        self.is_caps_clicked = not self.is_caps_clicked
        for button in self.buttons:
            new_text = button.text().upper() if self.is_caps_clicked else button.text().lower()
            button.setText(new_text)

    def shift_clicked(self):
        """Activates uppercase mode for the next single character input."""
        self.is_shift_clicked = not self.is_shift_clicked
        for button in self.buttons:
            new_text = button.text().upper() if self.is_shift_clicked else button.text().lower()
            button.setText(new_text)

    def is_shift_active(self):
        """Reverts character case after a Shift-modified keystroke is processed."""
        if self.is_shift_clicked:
            for button in self.buttons:
                button.setText(button.text().lower())
            self.is_shift_clicked = False