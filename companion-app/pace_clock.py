"""
Standalone professional pool pace clock module.
Implements a traditional 4-arrow rotating clock (60s cycle) using 
real-time trigonometric calculations and high-frequency UI updates.
"""

import json
import sys
import os
import math
import time
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

# Internal project configuration
from app_config import RETURN_BUTTON_STYLE, PROJECT_PATH

class PaceClock(QWidget):
    """
    Visual implementation of a four-arm swimming pace clock.
    
    The clock uses four distinct colored arrows offset by 15 seconds each, 
    replicating professional poolside analog clocks for interval training.
    """
    def __init__(self):
        """Initializes clock geometry, timing engine, and control interface."""
        super().__init__()
        self.setWindowTitle("Professional Pace Clock")
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        # --- Arrow Initial State (Angles in Radians) ---
        self.angle_0 = 0  # Primary arrow
        self.angle_1 = 90
        self.angle_2 = 180
        self.angle_3 = 270

        # Dynamic positioning based on screen center
        self.clock_x_center = self.available_width // 2
        self.clock_y_center = self.available_height // 2

        # Session reference for elapsed time calculation
        self.start_time = time.time()

        # Navigation Controls
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)
        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        self.return_button.move(30, int(self.height() / 2) + 80)

        # --- Graphical Constants ---
        self.arrow_length = 295
        self.arrows_thickness = 30
        self.yellow_circle_radius = 25
        self.marker_thickness_1 = 18 # Major ticks (15s)
        self.marker_thickness_2 = 14 # Minor ticks (5s/1s)
        self.font_size_4 = int(self.available_height * 0.05)

        # Refresh timer (100ms for smooth 10FPS movement)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(100)

        # Pre-calculate initial state
        self.update_angle()

    def paintEvent(self, event):
        """
        Main rendering engine for the clock face.
        Draws digits, markers, and rotating arrows using polar-to-cartesian conversion.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(0, 0, self.available_width, self.available_height, QColor("white"))

        # --- Drawing Digits (60, 10, 20...) ---
        angle_and_marks = {270: "60", 330: "10", 30: "20", 90: "30", 150: "40", 210: "50"}
        
        font = painter.font()
        font.setPointSize(35)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor("black")))

        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            text_box_width = text_box_height = 85

            # Quadrant-based digit alignment logic
            if mark in ["50", "40"]:
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2
            elif mark in ["10", "20"]:
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2
            elif mark == "60":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle)
            elif mark == "30":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height

            painter.drawText(QRect(int(box_x), int(box_y), text_box_width, text_box_height), Qt.AlignCenter, mark)

        # --- Drawing Perimeter Markers ---
        for i in range(60):
            angle = math.radians(i * 6) # 360 degrees / 60 seconds
            clk_marker_start_pos = self.available_width * 0.25
            clk_marker_end_pos = self.available_width * 0.27

            # Distinctive thickness for major intervals (90 deg / 30 deg)
            if (i * 6) % 90 == 0:
                painter.setPen(QPen(QColor("black"), self.marker_thickness_1))
                clk_marker_start_pos = self.available_width * 0.238  
            elif (i * 6) % 30 == 0:
                painter.setPen(QPen(QColor("black"), self.marker_thickness_1))
                clk_marker_start_pos = self.available_width * 0.240
            else:
                painter.setPen(QPen(QColor("black"), self.marker_thickness_2))
            
            painter.drawLine(
                int(self.clock_x_center + clk_marker_start_pos * math.cos(angle)),
                int(self.clock_y_center + clk_marker_start_pos * math.sin(angle)),
                int(self.clock_x_center + clk_marker_end_pos * math.cos(angle)),
                int(self.clock_y_center + clk_marker_end_pos * math.sin(angle))
            )

        # --- Drawing Rotating Arrows ---
        # Traditional colors: Black, Blue, Red, Green
        colors = ["black", "#032782", "#820903", "#1c8203"]
        angles = [self.angle_0, self.angle_1, self.angle_2, self.angle_3]

        for i in range(4):
            pen = QPen(QColor(colors[i]), self.arrows_thickness)
            pen.setCapStyle(Qt.RoundCap) # Aesthetic rounded tips
            painter.setPen(pen)
            
            # Destination coordinates based on current time-driven angle
            x_end = int(self.clock_x_center + self.arrow_length * math.cos(angles[i]))
            y_end = int(self.clock_y_center + self.arrow_length * math.sin(angles[i]))

            painter.drawLine(int(self.clock_x_center), int(self.clock_y_center), x_end, y_end)

        # Center cap (Small yellow pivot)
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        painter.drawEllipse(int(self.clock_x_center) - self.yellow_circle_radius,
                            int(self.clock_y_center) - self.yellow_circle_radius,
                            int(self.yellow_circle_radius * 2), int(self.yellow_circle_radius * 2))

    def update_angle(self):
        """
        Calculates arrow positions based on real-world elapsed time.
        Each arrow is permanently offset by a 15-second interval.
        """
        elapsed_seconds = time.time() - self.start_time
        
        # 6 degrees per second conversion (360/60)
        self.angle_0 = math.radians((elapsed_seconds * 6) % 360)
        self.angle_1 = math.radians(((elapsed_seconds + 15) * 6) % 360)
        self.angle_2 = math.radians(((elapsed_seconds + 30) * 6) % 360)
        self.angle_3 = math.radians(((elapsed_seconds + 45) * 6) % 360)
        
        # Trigger UI repaint
        self.update()

    def closeEvent(self, event):
        """Ensures the background timer is safely terminated on exit."""
        self.timer.stop()