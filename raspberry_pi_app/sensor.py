from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
from get_parameters import start_ble, stop_ble, is_connected, reading_parameters


class SensorWindow(QDialog):
    def __init__(self, width, height):
        super().__init__()

        self.setWindowTitle("Sensor")
        self.setWindowFlags(Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.window_width = width
        self.window_height = height

        # Stany
        self.is_connected = False
        self.is_connecting = False

        # Widgety
        self.connect_button = QPushButton("Connect", self)
        self.info_label = QLabel("Sensor Disconnected", self)
        self.data_label = QLabel("", self)

        # Layout
        self.main_layout = QVBoxLayout()
        self.setup_ui()

        # Timer do odświeżania statusu
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)

        self.refresh_status()

    def setup_ui(self):
        self.setFixedSize(self.window_width, self.window_height)

        button_size = int(self.window_width / 2.5)
        self.connect_button.setFixedSize(button_size, button_size)
        self.connect_button.clicked.connect(self.toggle_connection_state)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.info_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.data_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.main_layout.addLayout(layout)
        self.setLayout(self.main_layout)

        self.update_ui_state()

    def paintEvent(self, event):
        """Rysuje półprzezroczyste tło"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor(38, 38, 38, 240))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def toggle_connection_state(self):
        """Kliknięcie przycisku Connect / Disconnect"""
        if not self.is_connected and not self.is_connecting:
            # Rozpocznij łączenie
            self.is_connecting = True
            self.connect_button.setText("Connecting...")
            self.connect_button.setDisabled(True)
            self.info_label.setText("Connecting to sensor...")
            try:
                start_ble()
            except Exception as e:
                self.is_connecting = False
                self.info_label.setText(f"Connection Failed {str(e)}")
                self.update_ui_state()
                return
            
        elif self.is_connected:
            # Rozłącz
            self.connect_button.setText("Disconnecting...")
            self.connect_button.setDisabled(True)
            self.info_label.setText("Disconnecting...")
            stop_ble()

    def refresh_status(self):
        """Odświeżenie stanu BLE i danych"""
        connected_now = is_connected()

        # --- Łączenie ---
        if self.is_connecting:
            if connected_now:
                self.is_connected = True
                self.is_connecting = False
                self.info_label.setText("Sensor Connected")
                self.connect_button.setDisabled(False)
                self.update_ui_state()
            else:
                self.info_label.setText("Connecting to sensor...")
                # nadal connecting — przycisk wyłączony
                self.connect_button.setDisabled(True)
                self.connect_button.setText("Connecting...")
                return

        # --- Połączony ---
        elif connected_now and not self.is_connecting:
            self.is_connected = True
            params = reading_parameters()
            if params:
                bpm, spo2 = params
                self.data_label.setText(f"BPM: {bpm} | SpO₂: {spo2}%")
            else:
                self.data_label.setText("Reading data...")
            self.info_label.setText("Sensor Connected")
            self.connect_button.setDisabled(False)
            self.update_ui_state()

        # --- Rozłączony ---
        else:
            self.is_connected = False
            self.is_connecting = False
            self.data_label.setText("")
            self.info_label.setText("Sensor Disconnected")
            self.connect_button.setDisabled(False)
            self.update_ui_state()

    def update_ui_state(self):
        """Aktualizuje wygląd przycisku i etykiet"""
        radius = int(self.connect_button.width() / 2)
        base_style = f"""
        QPushButton {{
            font: bold 20pt 'Segoe UI';
            border-radius: {radius}px;
            border: 3px solid;
        }}
        """

        if self.is_connecting:
            self.connect_button.setText("Connecting...")
            self.connect_button.setStyleSheet(base_style + "color: gray; border-color: gray; background-color: #2c2c2c;")
            self.connect_button.setDisabled(True)
            self.info_label.setStyleSheet("color: #cccccc; font: bold 24pt 'Segoe UI';")

        elif self.is_connected:
            self.connect_button.setText("Disconnect")
            self.connect_button.setStyleSheet(base_style + "color: #ffffff; border-color: #a2f5bf; background-color: #1e1e1e;")
            self.info_label.setStyleSheet("color: #a2f5bf; font: bold 24pt 'Segoe UI';")

        else:
            self.connect_button.setText("Connect")
            self.connect_button.setStyleSheet(base_style + "color: #1abc9c; border-color: #1abc9c; background-color: #2c2c2c;")
            self.info_label.setStyleSheet("color: #3498db; font: bold 24pt 'Segoe UI';")

    def showEvent(self, event):
        """Wyśrodkowanie okna"""
        super().showEvent(event)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )


