from app_config import (BACKGROUND, HR_MAX_LABEL_STYLE, SAVE_BUTTON_STYLE, GET_HR_MAX_STYLE, MSG_STYLE,
                        RETURN_BUTTON_STYLE, RECOVERY_LAVBEL_STYLE, AEROBIC_CAPACITY_STYLE, AEROBIC_ENDURANCE_STYLE, ANAEROBIC_STYLE, VO2_MAX_STYLE, TRAINING_NAME_STYLE, MSG_STYLE)
import os
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPainter, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize, QTimer


import numeric_keyboard
import sys

class CalculateHrMax(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.background = QPixmap(BACKGROUND)

         # Initializing buttons
        self.calculate_button = QPushButton(self)
        self.calculate_button.clicked.connect(self.calculate_clicked)
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)
        self.save_button = QPushButton(self)
        self.save_button.hide()

        # Initializing virtual keyboard
        self.numeric_keyboard = numeric_keyboard.NumericKeyboard()

        # Line edit for user to enter his age
        self.users_age = QLineEdit(self)

        # HR max label
        self.hr_max_label = QLabel(self)

        # Hear rate zones labels
        self.recovery_label = QLabel(self)
        self.aerobic_endurance_label = QLabel(self)
        self.aerobic_capacity_label = QLabel(self)
        self.anaerobic_label = QLabel(self)
        self.vo2max_label = QLabel(self)

        self.zones = [self.recovery_label, self.aerobic_endurance_label, self.aerobic_capacity_label, self.anaerobic_label, self.vo2max_label]

        # Msg box
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setWindowFlags(Qt.Popup)
        self.msg.setAttribute(Qt.WA_TranslucentBackground)
        

        self.main_layout = QVBoxLayout()
        self.hr_zones_layout = QVBoxLayout()
        self.upper_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()


        self.is_hr_max_calculated = False

        self.init_ui()
        self.manage_layout()
        self.connect_users_age_to_numeric_keyboard()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawPixmap(self.rect(), self.background)


        color = QColor(0, 0, 0, 180)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        if self.is_hr_max_calculated:
            painter.drawRoundedRect(200, 240, int(self.width() - 400), 330, 25.0, 25.0)
            painter.end()


    def init_ui(self):
        # Calculate button style
        self.calculate_button.setText("Get HR Max")
        self.calculate_button.setStyleSheet(GET_HR_MAX_STYLE)
        self.calculate_button.setMinimumWidth(self.available_width // 3)
        self.calculate_button.setMaximumHeight(self.available_height // 8)
        self.calculate_button.setMinimumWidth(self.available_width // 3)

        # Use button style
        self.save_button.setText("Save")
        self.save_button.setStyleSheet(SAVE_BUTTON_STYLE)
        self.save_button.setMinimumWidth(self.available_width // 5)
        self.save_button.setMaximumHeight(self.available_height // 8)
        self.save_button.setMinimumWidth(self.available_width // 3)

        # Return button style
        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.move(30, int(self.height()/2) + 80)


        # Users age style
        self.users_age.setStyleSheet(TRAINING_NAME_STYLE)
        self.users_age.setAlignment(Qt.AlignCenter)
        self.users_age.setPlaceholderText("Enter your age!")
        self.users_age.setMaximumHeight(self.available_height // 8)
        self.users_age.setMinimumWidth(self.available_width // 3)

        # HR Max style
        self.hr_max_label.setStyleSheet(HR_MAX_LABEL_STYLE)

        # Heart rate zones style 
        self.recovery_label.setStyleSheet(RECOVERY_LAVBEL_STYLE)
        self.aerobic_endurance_label.setStyleSheet(AEROBIC_ENDURANCE_STYLE)
        self.aerobic_capacity_label.setStyleSheet(AEROBIC_CAPACITY_STYLE)
        self.anaerobic_label.setStyleSheet(ANAEROBIC_STYLE)
        self.vo2max_label.setStyleSheet(VO2_MAX_STYLE)

        # MSG Box
        self.msg.setStyleSheet(MSG_STYLE)
        


    def manage_layout(self):
        
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.users_age)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.calculate_button)
        self.upper_layout.addStretch(1)
       
        self.hr_zones_layout.addWidget(self.recovery_label, alignment=Qt.AlignCenter)
        self.hr_zones_layout.addWidget(self.aerobic_endurance_label, alignment=Qt.AlignCenter)
        self.hr_zones_layout.addWidget(self.aerobic_capacity_label, alignment=Qt.AlignCenter)
        self.hr_zones_layout.addWidget(self.anaerobic_label, alignment=Qt.AlignCenter)
        self.hr_zones_layout.addWidget(self.vo2max_label, alignment=Qt.AlignCenter)


        
        
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(2)
        self.main_layout.addWidget(self.hr_max_label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(2)
        self.main_layout.addLayout(self.hr_zones_layout, stretch=10)
        self.main_layout.addStretch(4)
        self.main_layout.addWidget(self.save_button, alignment= Qt.AlignCenter)
        self.main_layout.addStretch(1)


        self.setLayout(self.main_layout)
    
    def connect_users_age_to_numeric_keyboard(self):
        self.users_age.mousePressEvent = lambda event: self.show_numeric_keyboard(event)


    def show_numeric_keyboard(self, event):
        self.numeric_keyboard.set_target(self.users_age)
        self.numeric_keyboard.show()
        return QLineEdit.mousePressEvent(self.users_age, event)
    
    def calculate_clicked(self):
        age_entered = self.users_age.text()
        if not age_entered:
            self.msg.setText("Enter your age first!")
            self.msg.show()
            return
        
        self.is_hr_max_calculated = True
        age = int(self.users_age.text())
        hr_max = round(208 - (0.7 * age))
        self.hr_max_label.setText(f"Your HR Max is: {hr_max} bpm.")

        prct50 = int(hr_max * 0.5)
        prct60 = int(hr_max * 0.6)
        prct70 = int(hr_max * 0.7)
        prct80 = int(hr_max * 0.8)
        prct90 = int(hr_max * 0.9)

        self.recovery_label.setText(f"Recovery Zone (50-60% HR max): {prct50} - {prct60} bpm")
        self.aerobic_endurance_label.setText(f"Aerobic Endurance (60-70% HR max): {prct60} - {prct70} bpm")
        self.aerobic_capacity_label.setText(f"Aerobic Capacity (70-80% HR max): {prct70} - {prct80} bpm")
        self.anaerobic_label.setText(f"Anaerobic zone (80-90% HR max): {prct80} - {prct90} bpm")
        self.vo2max_label.setText(f"VO2Max Zone (90-100% HR max): {prct90} - {hr_max} bpm")

        self.save_button.show()
        self.update()

    def mousePressEvent(self, event):
        """Closes numeric keyboard whenerver you click anywhere else"""
        for window in QApplication.topLevelWidgets():
            if window.windowTitle() == "Numeric Keyboard":
                window.close()


