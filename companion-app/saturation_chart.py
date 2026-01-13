"""
Saturation (SpO2) visualization module for training analysis.
Utilizes PyQtGraph for efficient real-time-like rendering of blood oxygen 
levels recorded during the swim session.
"""

import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime
from app_config import RETURN_BUTTON_STYLE, PROJECT_PATH

import pyqtgraph as pg

class SPO2Chart(QWidget):
    """
    Analytics window for SpO2 (Oxygen Saturation) trends.
    
    Translates raw data from the ESP32 sensor into a visual timeline, 
    optimized for high-contrast viewing on embedded displays.
    """
    def __init__(self, directory, spo2_list):
        """
        Initializes the saturation chart.
        
        Args:
            directory (str): Session data directory path.
            spo2_list (list): Historical SpO2 percentage values.
        """
        super().__init__()

        # --- Screen Geometry Recovery ---
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.setCursor(Qt.BlankCursor) # UI polish for touch interfaces

        self.training_directory = directory
        self.y_axis = spo2_list
        self.x_axis = []

        # --- Time Domain Calculation ---
        # Maps raw sensor samples to a continuous minute-based scale
        minute = 0
        for value in self.y_axis:
            if len(self.x_axis) % 12 == 0: # Correlation logic: 12 samples = 1 minute
                minute += 1
            self.x_axis.append(minute)

        # Basic Widget Styling
        self.setStyleSheet("background-color: #121212;")
        
        # Navigation
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)

        # Plot Infrastructure
        self.main_layout = QVBoxLayout()
        self.plot_layout = QHBoxLayout()
        self.plot_widget = pg.PlotWidget(self)

        # Component Setup
        self.init_ui()
        self.create_plot()
        self.layout_managment()
    
    def init_ui(self):
        """Configures visual properties of navigation elements."""
        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        # Strategic positioning for ergonomic thumb access on touchscreens
        self.return_button.move(30, int(self.height() / 2) + 80)

    def create_plot(self):
        """
        Configures the SpO2 plot aesthetics and axis behavior.
        Focuses on high-contrast cyan lines on a dark background.
        """
        pg.setConfigOptions(antialias=True) # Ensure smooth curves

        # --- Data Plotting ---
        # Using a distinct Cyan color to differentiate SpO2 from Heart Rate
        self.plot_widget.plot(
            self.x_axis,
            self.y_axis,
            pen=pg.mkPen(color=(0, 220, 255), width=5)
        )

        self.plot_widget.setBackground("transparent")

        # --- Axis Configuration ---
        x_axis = self.plot_widget.getAxis('bottom')
        y_axis = self.plot_widget.getAxis('left')

        label_font = QFont("Segoe UI", 22)
        tick_font = QFont("Segoe UI", 16)

        x_axis.setLabel("Time", color="white")
        y_axis.setLabel("SPO2 (%)", color="white")

        x_axis.setTickFont(tick_font)
        y_axis.setTickFont(tick_font)
        x_axis.label.setFont(label_font)
        y_axis.label.setFont(label_font)

        # Grid for measurement precision
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # --- Dynamic Viewport Scaling ---
        # Squeezed Y-scale (±1%) for SpO2, as saturation changes are subtle
        # compared to heart rate fluctuations.
        min_y = min(self.y_axis)
        max_y = max(self.y_axis)
        self.plot_widget.setYRange(min_y - 1, max_y + 1)

        # Locked X-scale to session duration
        self.plot_widget.setXRange(0, max(self.x_axis) + 1)
        self.plot_widget.setContentsMargins(5, 5, 5, 5)

    def layout_managment(self):
        """Assembles the plot widget into the responsive layout structure."""
        self.plot_layout.addStretch(1)
        self.plot_layout.addWidget(self.plot_widget, stretch=8)
        self.plot_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.plot_layout, stretch=15)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)