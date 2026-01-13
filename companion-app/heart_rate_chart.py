"""
Data visualization module for heart rate analytics.
Implements high-performance plotting using PyQtGraph to display 
biometric trends from finished training sessions.
"""

import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime
from app_config import RETURN_BUTTON_STYLE, PROJECT_PATH

import pyqtgraph as pg

class HearRateChart(QWidget):
    """
    Interactive chart for heart rate data analysis.
    
    Translates raw logged data points into a time-domain plot, 
    applying dynamic scaling and hardware-accelerated rendering.
    """
    def __init__(self, directory, hr_list):
        """
        Initializes the chart with session data.
        
        Args:
            directory (str): Path to the current training data.
            hr_list (list): List of recorded heart rate values (BPM).
        """
        super().__init__()

        # --- Display Configuration ---
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()

        self.training_directory = directory
        self.y_axis = hr_list
        self.x_axis = []

        # --- Timeline Logic ---
        # Converts sequential data points into a minute-based time scale
        minute = 0
        for value in self.y_axis:
            if len(self.x_axis) % 12 == 0: # Assuming 12 samples per minute logic
                minute += 1
            self.x_axis.append(minute)

        # --- UI Styling ---
        self.setStyleSheet("background-color: #121212;")
        self.return_button = QPushButton(self)
        self.return_button.clicked.connect(self.close)

        # --- Layout & Plot Widget ---
        self.main_layout = QVBoxLayout()
        self.plot_layout = QHBoxLayout()
        self.plot_widget = pg.PlotWidget(self) # High-performance plot container

        # Component Initialization
        self.init_ui()
        self.create_plot()
        self.layout_managment()
    
    def init_ui(self):
        """Sets up navigation controls and icons."""
        self.return_button.setIcon(QIcon(f"{PROJECT_PATH}/icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)
        # Position button relative to screen geometry
        self.return_button.move(30, int(self.height() / 2) + 80)

    def create_plot(self):
        """
        Configures the aesthetic and functional properties of the chart.
        Applies antialiasing, custom fonts, and dynamic axis scaling.
        """
        # Enable smooth line rendering
        pg.setConfigOptions(antialias=True)

        # --- Data Series Configuration ---
        # Plotting the HR line with a high-visibility stroke
        self.plot_widget.plot(
            self.x_axis,
            self.y_axis,
            pen=pg.mkPen(color=(255, 80, 80), width=5) # Athletic Red theme
        )

        self.plot_widget.setBackground("transparent")

        # --- Axis Styling ---
        x_axis = self.plot_widget.getAxis('bottom')
        y_axis = self.plot_widget.getAxis('left')

        label_font = QFont("Segoe UI", 22)
        tick_font = QFont("Segoe UI", 16)

        x_axis.setLabel("Time (minutes)", color="white")
        y_axis.setLabel("Heart Rate (bpm)", color="white")

        x_axis.setTickFont(tick_font)
        y_axis.setTickFont(tick_font)
        x_axis.label.setFont(label_font)
        y_axis.label.setFont(label_font)

        # Subtle grid for easier data reading
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)

        # --- Dynamic Viewport Scaling ---
        # Automatically adjust Y-range based on physiological data spread
        min_y = min(self.y_axis)
        max_y = max(self.y_axis)
        self.plot_widget.setYRange(min_y - 5, max_y + 5)

        # Set X-range to match training duration
        self.plot_widget.setXRange(0, max(self.x_axis) + 1)
        self.plot_widget.setContentsMargins(5, 5, 5, 5)

    def layout_managment(self):
        """Assembles the chart into the main application layout."""
        self.plot_layout.addStretch(1)
        self.plot_layout.addWidget(self.plot_widget, stretch=8)
        self.plot_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.plot_layout, stretch=15)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)