from PyQt5.QtWidgets import QWidget, QDialog, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from datetime import datetime

import start_training
import plan_training


class SensorWindow(QDialog):
    def __init__(self, width, height):
        super().__init__()


        self.setWindowTitle(" ")
        self.window_width = width
        self.window_height = height

        self.setStyleSheet("background-color: #363434;")

        self.is_conected = True

        # Buttons and labels
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.toggle_connection_state)
        self.info_label = QLabel(self)

        self.main_layout = QHBoxLayout()
        self.info_layout = QVBoxLayout()


        self.init_ui()
        self.layout_manager()
        self.update_ui_state()

    def init_ui(self):
        self.button_size = int(self.window_width / 2.5)
        self.connect_button.setFixedSize(self.button_size, self.button_size)


    def toggle_connection_state(self):

        self.is_conected = not self.is_conected
        self.update_ui_state()


    def update_ui_state(self):

        radius = self.button_size // 2

        button_style = f"""
        QPushButton {{
                        background-color: rgba(0, 0, 0, 0.7);
                        font: bold 20pt 'Segoe UI';
                        border-radius: {radius}px;
                        }}
                        
        QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.6);
                        padding-top: 3px;
                        padding-left: 3px;
                        }}
        """

        if self.is_conected == 1:
            self.connect_button.setText("Disconnect")
            self.info_label.setText("Sensor Connected")
            self.info_label.setStyleSheet("color: #4CAF50; font: bold 24pt 'Segoe UI';")
            self.connect_button.setStyleSheet(button_style + """QPushButton {
                    color: #F44336;
                    border: 3px solid #F44336;
                }""")
        elif self.is_conected == 0:
            self.connect_button.setText("Connect")
            self.info_label.setText("Sensor Disconnected")
            self.info_label.setStyleSheet("color: #F44336; font: bold 24pt 'Segoe UI';")
            self.connect_button.setStyleSheet(button_style + """QPushButton {
                                color: #4CAF50;
                                border: 3px solid #4CAF50;
                            }""")
        # else:
        #     self.connect_button.setText("Connecting...")
        #     self.info_label.setText(" ")
        #     self.info_label.setStyleSheet("color: #F44336; font: bold 24pt 'Segoe UI';")
        #     self.connect_button.setStyleSheet(button_style + """QPushButton {
        #                                     color: #white;
        #                                     border: 3px solid #4CAF50;
        #                                 }""")
        #     self.connect_button.setDisabled(True)

    def layout_manager(self):
        self.info_layout.addStretch(1)
        self.info_layout.addWidget(self.info_label, alignment=Qt.AlignCenter)
        self.info_layout.addStretch(1)
        self.info_layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)
        self.info_layout.addStretch(1)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.info_layout, stretch=3)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)




# def main():
#     app = QApplication(sys.argv)
#     window = SensorWindow()
#     window.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == "__main__":
#     main()
#
#
#




