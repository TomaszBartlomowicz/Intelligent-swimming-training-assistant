import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer
import math

class TrainingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplikacja")
        self.setGeometry(100, 100, 1024, 600)

        self.heart_rate_button = QPushButton(self, text=" 74")
        self.saturation_button = QPushButton(self, text=" 98%")
        self.time_label = QLabel("00:00", self)
        self.heart_rate_button.setIcon(QIcon("icons/heart_rate.png"))
        self.saturation_button.setIcon(QIcon("icons/saturation.png"))

        self.current_set_label = QLabel("Current set:")
        self.repetition_counter = QLabel("")
        self.task_label = QLabel(" 10 x 100m")
        self.stop_button = QPushButton("PAUSE")
        self.skip_button = QPushButton("SKIP SET")
        self.resume_button = QPushButton("RESUME")

        self.details_text_window = QPlainTextEdit()
        self.details_text_window.setPlainText("Pierwsza kraul, druga wg. zmiennego\nCo druga max reszta tempo tlenowe")
        self.details_text_window.setReadOnly(True)

        self.upper_layout = QHBoxLayout()
        self.current_set_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        self.angle_0 = math.radians(90)
        self.angle_1 = math.radians(180)
        self.angle_2 = math.radians(270)
        self.angle_3 = math.radians(360)

        self.clock_widget = QPixmap(self.size())
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.timeout.connect(self.update_angle)
        self.wall_clock_timer.start(10)

        self.x_center = 730
        self.y_center = 600 / 2
        self.arrow_length = 230
        self.clock_widget = QPixmap(self.size())
        self.draw_clock(self.clock_widget)

        self.emoji_timer = QTimer(self)
        self.emoji_timer.start(1000)
        self.emoji_timer.timeout.connect(lambda: self.toggle_emoji_size())

        self.is_paused = False
        self.counter = 0
        self.stoper = QTimer(self)
        self.stoper.start(1000)
        self.stoper.timeout.connect(self.update_timer)

        self.layout_settings()
        self.init_ui()
        self.connecting_buttons()
        self.resume_button.hide()
        self.update_lower_layout()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self.clock_widget)

        for i in range(4):
            if i == 0:
                painter.setPen(QPen(QColor("#c9b037"), 25))  # złoty
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_0))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_0))
            elif i == 1:
                painter.setPen(QPen(QColor("#708090"), 25))  # srebrny
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_1))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_1))
            elif i == 2:
                painter.setPen(QPen(QColor("#8b0000"), 25))  # burgund
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_2))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_2))
            elif i == 3:
                painter.setPen(QPen(QColor("#006400"), 25))  # zieleń butelkowa
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_3))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_3))
            painter.drawLine(int(self.x_center), int(self.y_center), x_end, y_end)

        painter.setPen(QPen(QColor("#ffd700")))
        painter.setBrush(QColor("#ffd700"))
        radius = 20
        painter.drawEllipse(int(self.x_center) - radius, int(self.y_center) - radius, 2 * radius, 2 * radius)

    def init_ui(self):
        self.heart_rate_button.setStyleSheet("background-color: transparent; color: white; font: bold; font-size: 40px;")
        self.saturation_button.setStyleSheet("background-color: transparent; color: white; font: bold; font-size: 40px;")

        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
                font: bold;
                font-size: 30px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #a40000;
            }
        """)

        self.resume_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                font: bold;
                font-size: 30px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)

        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font: bold;
                font-size: 30px;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

        self.time_label.setStyleSheet("color: white; font: bold; font-size: 40px;")
        self.current_set_label.setStyleSheet("color: white; font: bold; font-size: 32px;")
        self.task_label.setStyleSheet("color: white; font: bold; font-size: 32px;")
        self.repetition_counter.setStyleSheet("color: white; font: bold; font-size: 32px;")

        self.details_text_window.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.4);
            color: #f0f0f0;
            font: 18px 'Segoe UI';
            border: 2px solid #888;
            border-radius: 15px;
            padding: 10px;
        """)

        self.heart_rate_button.setIconSize(QSize(70, 70))
        self.saturation_button.setIconSize(QSize(70, 70))
        self.heart_rate_button.setFixedSize(220, 100)
        self.saturation_button.setFixedSize(220, 100)

    def layout_settings(self):
        self.upper_layout.addWidget(self.heart_rate_button)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.saturation_button)
        self.upper_layout.addStretch(400)

        self.current_set_layout.addWidget(self.current_set_label)
        self.current_set_layout.addWidget(self.task_label)
        self.current_set_layout.addStretch(5)
        self.current_set_layout.addWidget(self.time_label)
        self.current_set_layout.addStretch(4)

        self.middle_layout.addWidget(self.details_text_window, stretch=2)
        self.middle_layout.addStretch(3)

        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.current_set_layout)
        self.main_layout.addLayout(self.middle_layout, stretch=20)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

    def connecting_buttons(self):
        self.resume_button.clicked.connect(self.pause_resume_clicked)
        self.stop_button.clicked.connect(self.pause_resume_clicked)

    def pause_resume_clicked(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.stoper.stop()
            self.wall_clock_timer.stop()
        else:
            self.stoper.start()
            self.wall_clock_timer.start()
        self.update_lower_layout()

    def update_lower_layout(self):
        while self.lower_layout.count():
            item = self.lower_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.lower_layout.addStretch(1)
        if self.is_paused:
            self.lower_layout.addWidget(self.resume_button)
            self.resume_button.show()
        else:
            self.lower_layout.addWidget(self.stop_button)

        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.skip_button)
        self.lower_layout.addStretch(10)

    def toggle_emoji_size(self):
        size = QSize(60, 60) if self.heart_rate_button.iconSize() == QSize(70, 70) else QSize(70, 70)
        self.heart_rate_button.setIconSize(size)
        self.saturation_button.setIconSize(size)

    def update_timer(self):
        self.counter += 1
        mins = self.counter // 60
        secs = self.counter % 60
        self.time_label.setText(f"{mins:02d}:{secs:02d}")

    def draw_clock(self, clock_widget):
        painter = QPainter(clock_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 1024, 600)
        gradient.setColorAt(0, QColor("#1c1c1e"))
        gradient.setColorAt(1, QColor("#2c2c2e"))
        painter.fillRect(self.rect(), gradient)

        angle_and_marks = {
            270: "60", 330: "10", 30: "20", 90: "30", 150: "40", 210: "50"
        }

        font = painter.font()
        font.setPointSize(20)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("#f8f8f8"))

        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            x = self.x_center + 180 * math.cos(angle)
            y = self.y_center + 180 * math.sin(angle)

            offset_x = -20 if degree in [270, 90] else -10
            offset_y = 10 if degree == 270 else 25 if degree in [30, 150] else 0
            painter.drawText(int(x) + offset_x, int(y) + offset_y, mark)

        for i in range(60):
            angle = math.radians(i * 6)
            end_point = 250
            if (i * 6) % 90 == 0:
                painter.setPen(QPen(QColor("black"), 17))
                end_point = 220
            elif (i * 6) % 30 == 0:
                painter.setPen(QPen(QColor("black"), 15))
            else:
                painter.setPen(QPen(QColor("black"), 10))
            x_start = int(self.x_center + end_point * math.cos(angle))
            y_start = int(self.y_center + end_point * math.sin(angle))
            x_end = int(self.x_center + 275 * math.cos(angle))
            y_end = int(self.y_center + 275 * math.sin(angle))
            painter.drawLine(x_start, y_start, x_end, y_end)

    def update_angle(self):
        delta = math.radians(0.06)
        self.angle_0 = (self.angle_0 + delta) % (2 * math.pi)
        self.angle_1 = (self.angle_1 + delta) % (2 * math.pi)
        self.angle_2 = (self.angle_2 + delta) % (2 * math.pi)
        self.angle_3 = (self.angle_3 + delta) % (2 * math.pi)
        self.update()


def main():
    app = QApplication(sys.argv)
    window = TrainingWindow()
    window.show()
    sys.exit(app.exec_())

main()
