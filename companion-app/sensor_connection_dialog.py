"""
Bluetooth sensor management interface for the swimming assistant sensor.
"""

from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
import bluetooth_connection
from app_config import BATTERY_STYLE

class SensorWindow(QDialog):
    """
    Modal dialog for orchestrating BLE sensor connectivity.
    
    Implements a state machine to manage three distinct connection phases:
    Disconnected, Connecting, and Connected, with dedicated UI feedback 
    for each state.
    """

    def __init__(self):
        """Initializes the sensor manager, UI widgets, and background refresh timers."""
        super().__init__()

        self.setWindowTitle("Sensor")
        self.setWindowFlags(Qt.Popup) # Frameless overlay
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- GUI Widgets ---
        self.connect_button = QPushButton(self)
        self.connect_button.clicked.connect(self.toggle_connection_state)
        
        self.title_label = QLabel("BLUETOOTH SENSOR", self)
        self.info_label = QLabel("Sensor Disconnected", self)
        self.battery_voltage_label = QLabel(self)
        self.battery_percentage_label = QLabel(self)

        # Apply specialized styles for energy telemetry
        self.battery_voltage_label.setStyleSheet(BATTERY_STYLE)
        self.battery_percentage_label.setStyleSheet(BATTERY_STYLE)

        self.layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        self.create_layout()

        # --- BLE States Logic ---
        self.connected = False
        self.connecting = False
        self.update_ble_state()
 
        # --- Background Telemetry Refresh ---
        # Polling timer to synchronize UI with asynchronous BLE thread state
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ble_state)
        self.timer.timeout.connect(self.display_battery_condition)
        self.timer.start(1000) # 1Hz refresh rate for connection and battery status

        self.update_ui_state()

    def create_layout(self):
        """Organizes widgets into a centered horizontal layout with battery side-indicators."""
        self.layout.addStretch(1)
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)
        self.layout.addWidget(self.info_label, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)
        self.layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)
        self.layout.addStretch(2)

        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.battery_percentage_label)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.battery_voltage_label)
        self.main_layout.addStretch(1)

        fixed_width = 100 
        self.battery_voltage_label.setFixedWidth(fixed_width)
        self.battery_voltage_label.setAlignment(Qt.AlignCenter)
        self.battery_percentage_label.setFixedWidth(fixed_width)
        self.battery_percentage_label.setAlignment(Qt.AlignCenter)

        self.setLayout(self.main_layout)

    def update_ui_state(self):
        """
        Dynamically updates the visual style and interactivity of the UI.
        
        Applies a color-coded feedback system:
        - Amber: Connection in progress.
        - Green: Active stable link.
        - Red: No peripheral signal.
        """
        button_size = 220
        self.connect_button.setFixedSize(button_size, button_size)

        base_style = """
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 0.1);
            padding-top: 5px;
            padding-left: 5px;
        }
        QPushButton {
            font: bold 20pt 'Segoe UI';
            border-radius: 110px;
            border: 3px solid;
        """

        self.battery_percentage_label.hide()
        self.battery_voltage_label.hide()
        self.title_label.setStyleSheet("color: #b8b9ba; font: bold 16pt 'Segoe UI';")

        # 1. CONNECTING State (Yellow/Amber)
        if self.connecting:
            self.connect_button.setText("Connecting...")
            self.connect_button.setStyleSheet(base_style + """
                color: #FFC107; 
                border-color: #FFC107; 
                background-color: rgba(255, 193, 7, 0.1);
            }""")
            self.connect_button.setDisabled(True)
            self.info_label.setStyleSheet("color: #FFC107; font: 650 22pt 'Segoe UI';")

        # 2. CONNECTED State (Stable Green feedback)
        elif self.connected:
            self.connect_button.setText("Disconnect")
            self.connect_button.setStyleSheet(base_style + """
                color: #E0E0E0; 
                border-color: #E0E0E0; 
                background-color: transparent;
            }""")
            self.connect_button.setDisabled(False)
            self.info_label.setStyleSheet("color: #00E676; font: 650 22pt 'Segoe UI';")
            self.info_label.setText("Sensor Connected")
            
            # Show battery telemetry only when active
            self.battery_percentage_label.show()
            self.battery_voltage_label.show()

        # 3. DISCONNECTED State (Idle Red feedback)
        else:
            self.connect_button.setText("Connect")
            self.connect_button.setStyleSheet(base_style + """
                color: #E0E0E0; 
                border-color: #E0E0E0; 
                background-color: transparent;
            }""")
            self.connect_button.setDisabled(False)
            self.info_label.setStyleSheet("color: #FF5252; font: 650 22pt 'Segoe UI';")
            self.info_label.setText("Sensor Disconnected")

    def toggle_connection_state(self):
        """Dispatches connection or disconnection requests to the BLE threading module."""
        if not self.connected and not self.connecting:
            self.connecting = True
            self.update_ui_state()
            self.info_label.setText("Connecting to sensor...")
            # Spawns asynchronous thread to handle BLE scanning and handshaking
            bluetooth_connection.start_ble_in_thread()
        elif self.connected:
            self.info_label.setText("Disconnecting...")
            bluetooth_connection.disconnect_ble()
            self.connected = False
            self.connecting = False
            self.update_ui_state()

    def update_ble_state(self):
        """Synchronizes internal flags with the real-time status of the BLE hardware link."""
        if bluetooth_connection.is_connected(): 
            self.connected = True
            self.connecting = False
        else:
            if not self.connecting:
                self.connected = False
        self.update_ui_state()

    def paintEvent(self, event):
        """Renders the rounded dialog background with custom anti-aliasing."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(38, 38, 38)) # Dark theme consistency
        painter.setBrush(brush)
        painter.setPen(QColor(255, 255, 255))
        painter.drawRoundedRect(self.rect(), 25, 25)

    def display_battery_condition(self):
        """Fetches and displays the latest power metrics from the wearable peripheral."""
        latest = getattr(bluetooth_connection, "latest_values", {})

        battery_percentage