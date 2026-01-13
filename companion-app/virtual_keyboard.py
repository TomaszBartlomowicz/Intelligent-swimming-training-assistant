import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit, QLayout, QSpacerItem, QScrollArea, QLineEdit, QComboBox
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint

class VirtualKeyboard(QWidget):
    def __init__(self, target_line_edit=None):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()
        self.setWindowTitle("Virtual Keyboard")

 
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.target_line_edit = target_line_edit  # QLineEdit, do którego piszemy
        ##self.setStyleSheet("background-color: rgba(0, 0, 0, 1);")
        # Układ klawiszy
        self.keyboard_rows = {
            "numeric": ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-","=","⌫"],
            "first_row": ["Tab","q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            "second_row": ["Caps  ", "a", "s", "d", "f", "g", "h", "j", "k", "l", ":"],
            "third_row": ["Shift", "z", "x", "c", "v", "b", "n", "m",",",".", "/"],
            "fourth_row": [" ↲ ", "        Space        ", " Enter "]
        }

        self.buttons = []

        self.is_caps_clicked = False
        self.is_shift_clicked = False

        self.drag_active = False
        self.clicked_pos = None

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
        self.create_keayboard()

    def init_ui(self):

        # Styl ogólny klawiatury (ciemne półprzezroczyste tło)
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
        """Rysuje jednolite tło z zaokrąglonymi rogami"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(15, 25, 35, 220))  # biale, lekko przezroczyste
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)  

        
    def create_keayboard(self):
        for row_name, keys in self.keyboard_rows.items():
            row_layout = self.layouts[row_name]
            row_layout.setSpacing(8)
            row_layout.addStretch(1)
            for key in keys:
                button = QPushButton(key)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(self.available_width // 18, self.available_height // 13  )
                ## Special functions keys
                if (key == "⌫"):
                    button.clicked.connect(self.backspace)
                elif (key == " Enter "):
                    button.clicked.connect(self.enter)
                elif (key == "        Space        "):
                    button.clicked.connect(lambda: self.add_text(" "))
                elif(key == " ↲ "):
                    button.clicked.connect(lambda: self.add_text("\n"))
                elif(key == "Tab"):
                    button.clicked.connect(lambda: self.add_text("\t"))
                elif(key == "Caps  "):
                    button.clicked.connect(self.caps_clicked)    
                elif(key == "Shift"):
                    button.clicked.connect(self.shift_clicked) 
                # Standard keys
                else:
                    button.clicked.connect(lambda checked, k=key: self.add_text(k))
                    button.clicked.connect(self.is_shift_active)
                    self.buttons.append(button)
                row_layout.addWidget(button)
            row_layout.addStretch(1)

            self.main_layout.addLayout(row_layout)

        self.setLayout(self.main_layout)

    def add_text(self, text):
        if not self.target_line_edit:
            return
        
        if self.is_caps_clicked | self.is_shift_clicked:
            text_to_add = text.upper()
        else:
            text_to_add = text

        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.insert(text_to_add)
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            self.target_line_edit.insertPlainText(text_to_add)
    
    def enter(self):
        self.target_line_edit.clearFocus()
        self.close()

    def backspace(self):
        if isinstance(self.target_line_edit, QLineEdit):
            self.target_line_edit.backspace()
        elif isinstance(self.target_line_edit, QPlainTextEdit):
            cursor = self.target_line_edit.textCursor()
            cursor.deletePreviousChar()
            self.target_line_edit.setTextCursor(cursor)

    def set_target(self, line_edit):
        """Podpinamy QLineEdit do klawiatury"""
        self.target_line_edit = line_edit


    def caps_clicked(self):
        if not self.is_caps_clicked:
            for button in self.buttons:
                button.setText(button.text().upper()) 
        else:
            for button in self.buttons:
                button.setText(button.text().lower())

        self.is_caps_clicked = not self.is_caps_clicked


    def shift_clicked(self):
        if not self.is_shift_clicked:
            for button in self.buttons:
                button.setText(button.text().upper()) 
        else:
            for button in self.buttons:
                button.setText(button.text().lower())

        self.is_shift_clicked = not self.is_shift_clicked


    def is_shift_active(self):
        if self.is_shift_clicked:
            for button in self.buttons:
                button.setText(button.text().lower())

            self.is_shift_clicked = not self.is_shift_clicked
        

