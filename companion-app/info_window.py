from app_config import INFO_LABEL_STYLE, PROJECT_PATH, OK_BUTTON_STYLE
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap
import sys

class InfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)



        self.agh_logo = QPixmap(f"{PROJECT_PATH}/icons/agh_logo.png")
        self.agh_logo = self.agh_logo.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)


        #Declaring buttons and labels
        self.label = QLabel(self)
        self.ok_button = QPushButton(self)
        self.ok_button.clicked.connect(self.accept)
        
        # Declaring layout
        self.layout = QVBoxLayout(self)

        # Calling necessary functions
        self.layout_managment()
        self.init_ui()
        

    def init_ui(self):
        self.label.setText(
            "Aplikacja jest częścią Projektu inżynierskiego\n"
            "realizowanego przez\n\n"
            "Tomasz Bartłomowicz"
            
        )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(INFO_LABEL_STYLE)

        self.ok_button.setText("Rozumiem")
        self.ok_button.setStyleSheet(OK_BUTTON_STYLE)
        
        

    def layout_managment(self):
        self.layout.setContentsMargins(12, 24, 12, 12)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.label)
        self.layout.addStretch(2)
        self.layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        """Rysuje jednolite tło z zaokrąglonymi rogami"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(255, 255, 255, 240))  # biale, lekko przezroczyste
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)  # 20px zaokrąglenie
        x = (self.width() - self.agh_logo.width()) // 2
        y = (self.height() - self.agh_logo.height()) // 2
        painter.drawPixmap(x, y+33, self.agh_logo)

