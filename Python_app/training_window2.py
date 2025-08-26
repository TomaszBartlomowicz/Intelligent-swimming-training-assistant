import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer

import math
import time


class TrainingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.is_paused = False
        self.window_width = 1024
        self.window_height = 600
        self.showFullScreen()
        self.setGeometry(100, 100, self.window_width, self.window_height)

        # Declaring buttons and labels

        self.heart_rate_button = QPushButton(self, text=" 74")
        self.saturation_button = QPushButton(self, text=" 98%")
        self.time_label = QLabel("15 seconds to GO!", self)
        self.heart_rate_button.setIcon(QIcon("icons/heart_rate.png"))
        self.saturation_button.setIcon(QIcon("icons/saturation.png"))

        self.current_set_label = QLabel(self)
        self.current_set_label.setText(" Current set:")
        self.task_label = QLabel(self)
        self.task_label.setText(" 10 x 100m ")
        self.stop_button = QPushButton(self, text="PAUSE")
        self.skip_button = QPushButton(self, text="SKIP SET")
        self.resume_button = QPushButton(self, text="RESUME")


        self.details = "Breaststroke"
        self.limit = "1:50"
        self.desired_heart_rate = "120 - 130"
        self.details_text_window = QPlainTextEdit()

        self.details_text_window.appendPlainText(self.details)
        self.details_text_window.appendPlainText("\n")
        self.details_text_window.appendPlainText(f"Time limit: {self.limit}\nHeart rate range: {self.desired_heart_rate}")
        self.details_text_window.setReadOnly(True)


        self.start_time = time.time()
        self.pause_clicked_time = 0
        self.resume_clicked_time = 0
        self.total_paused_time = 0

        # Declaring layouts
        self.upper_layout = QHBoxLayout()
        self.current_set_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        # Pool clock
        self.angle_0 = math.radians(0)
        self.angle_1 = math.radians(90)
        self.angle_2 = math.radians(180)
        self.angle_3 = math.radians(270)

        self.clock_widget = QPixmap(self.size())
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.timeout.connect(self.update_angle)
        self.wall_clock_timer.timeout.connect(self.update_timer)
        self.wall_clock_timer.start(33)
        self.x_center = 730
        self.y_center = 600 / 2
        self.arrow_length = 230
        self.clock_widget = QPixmap(self.size())
        self.draw_clock(self.clock_widget)



        self.emoji_timer = QTimer(self)
        self.emoji_timer.start(1000)
        self.emoji_timer.timeout.connect(lambda: self.toggle_emoji_size())



        # Functions calling
        self.layout_settings()
        self.init_ui()
        self.connecting_buttons()
        self.resume_button.hide()
        self.update_lower_layout()




    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dodaj kolory do gradientu
        painter.drawPixmap(0, 0, self.clock_widget)

        #painter.fillRect(self.rect(), gradient)

        painter.setPen(QPen(QColor("black"), 20))
        x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_0))
        y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_0))

        # Zegar lines
        for i in range(4):
            if i == 1:
                painter.setPen(QPen(QColor("#032782"), 20)) # niebieski
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_1))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_1))
            elif i == 2:
                painter.setPen(QPen(QColor("#820903"), 20)) # czerwony
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_2))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_2))
            elif i == 3:
                painter.setPen(QPen(QColor("#1c8203"), 20)) # zielony
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_3))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_3))

            painter.drawLine(int(self.x_center), int(self.y_center), x_end, y_end)

        # Small middle circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        radius = 20
        painter.drawEllipse(int(self.x_center) - radius, int(self.y_center) - radius, 2 * radius, 2 * radius)

        painter.setPen(QPen(QColor("white")))
        font = painter.font()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(int(self.x_center)-40, 420, str("9 left"))


    def init_ui(self):
        self.heart_rate_button.setStyleSheet("background-color: transparent;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 40px;")

        self.saturation_button.setStyleSheet("background-color: transparent;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 40px;")

        self.stop_button.setStyleSheet("background-color: darkred;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 30px;"
                                             "border-radius: 10px;"
                                             "padding: 10px;")

        self.resume_button.setStyleSheet("background-color: darkgreen;"
                                       "color: white;"
                                       "font: bold;"
                                       "font-size: 30px;"
                                       "border-radius: 10px;"
                                        "padding: 10px;"
                                         )

        self.skip_button.setStyleSheet("background-color: #252526;"
                                       "color: white;"
                                       "font: bold;"
                                       "font-size: 30px;"
                                       "border-radius: 10px;"
                                       "padding: 10px;")


        self.time_label.setStyleSheet("background-color: none;"
                                         "color: white;"
                                         "font: bold;"
                                         "font-size: 40px;")

        self.current_set_label.setStyleSheet("background-color: none;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 32px;")

        self.task_label.setStyleSheet("background-color: none;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 32px;")

        self.details_text_window.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                               "color: white;"
                                               "font: 20px 'Segoe UI';"
                                               "border: 3px solid black;"
                                               "border-radius: 20px;"
                                               "padding: 10px")


        self.heart_rate_button.setIconSize(QSize(70, 70))
        self.saturation_button.setIconSize(QSize(70, 70))

        self.heart_rate_button.setFixedSize(220, 100)
        self.saturation_button.setFixedSize(220, 100)

        self.stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def layout_settings(self):

        #self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.heart_rate_button)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.saturation_button)
        self.upper_layout.addStretch(400)

        self.current_set_layout.addWidget(self.current_set_label)
        self.current_set_layout.addWidget(self.task_label)
        self.current_set_layout.addStretch(100)
        self.current_set_layout.addWidget(self.time_label)
        self.current_set_layout.addStretch(86)

        self.middle_layout.addWidget(self.details_text_window, stretch=7)
        self.middle_layout.addStretch(10)


        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(2)
        self.main_layout.addLayout(self.current_set_layout)
        #self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.middle_layout, stretch=20)
        self.main_layout.addStretch(3)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(3)
        self.setLayout(self.main_layout)


    def connecting_buttons(self):
        self.resume_button.clicked.connect(self.resume_clicked)
        self.stop_button.clicked.connect(self.pause_clicked)

    def pause_clicked(self):
        self.wall_clock_timer.stop()
        self.pause_clicked_time = time.time() - self.start_time
        self.is_paused = True
        self.update_lower_layout()


    def resume_clicked(self):
        self.wall_clock_timer.start()
        self.resume_clicked_time = time.time() - self.start_time
        self.is_paused = False
        self.total_paused_time += self.resume_clicked_time - self.pause_clicked_time
        self.update_lower_layout()

    def update_lower_layout(self):
        # usuń wszystkie elementy z lower_layout
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

        self.lower_layout.addStretch(2)
        self.lower_layout.addWidget(self.skip_button)
        self.lower_layout.addStretch(20)

    def toggle_emoji_size(self):
        if self.heart_rate_button.iconSize() == QSize(70, 70):
            self.heart_rate_button.setIconSize(QSize(60, 60))
            self.saturation_button.setIconSize(QSize(60, 60))
        else:
            self.heart_rate_button.setIconSize(QSize(70, 70))
            self.saturation_button.setIconSize(QSize(70, 70))


    def update_timer(self):
        if self.start_time + 15 + self.total_paused_time - time.time() >= 1:
            seconds = self.start_time + 15 + self.total_paused_time -  time.time()
            secs = round(seconds) % 60
            self.time_label.setText(f"{secs}")
        elif 0 < self.start_time + 15 + self.total_paused_time - time.time() < 1 :
            self.time_label.setStyleSheet("background-color: none;"
                                              "color: green;"
                                              "font: bold;"
                                              "font-size: 40px;")
            self.time_label.setText("GO!")
        else:
            self.time_label.setStyleSheet("background-color: none;"
                                              "color: white;"
                                              "font: bold;"
                                              "font-size: 40px;")
            elapsed_seconds = time.time() - self.start_time - self.total_paused_time - 15
            mins = round(elapsed_seconds // 60)
            secs = round(elapsed_seconds) % 60

            self.time_label.setText(f"{mins:02d}:{secs:02d}")


    def draw_clock(self, clock_widget):
        painter = QPainter(clock_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient Seeting
        gradient = QLinearGradient(0, 0, 1024, 600)
        gradient.setColorAt(0, QColor("#0f0f0f"))
        gradient.setColorAt(0.3, QColor("#1a1919"))
        gradient.setColorAt(0.6, QColor("#242323"))
        gradient.setColorAt(1, QColor("#333333"))
        painter.fillRect(self.rect(), gradient)
        #painter.drawPixmap(self.rect(), self.background)

        ## Draw number
        angle_and_marks = {
            270: "60",  # godzina 12:00 (na górze)
            330: "10",
            30: "20",
            90: "30",  # godzina 6:00 (na dole)
            150: "40",
            210: "50"
        }
        painter.setPen(QPen(QColor("#b09405")))
        font = painter.font()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)

        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            x_coordinate = self.x_center + 180 * math.cos(angle)
            y_coordinate = self.y_center + 180 * math.sin(angle)

            if degree == 270 or degree == 90:
                painter.drawText(int(x_coordinate) - 20, int(y_coordinate) + 10, mark)
            elif mark == "10":
                painter.drawText(int(x_coordinate), int(y_coordinate), mark)
            elif mark == "20":
                painter.drawText(int(x_coordinate), int(y_coordinate) + 25, mark)
            elif mark == "40":
                painter.drawText(int(x_coordinate) - 45, int(y_coordinate) + 25, mark)
            elif mark == "50":
                painter.drawText(int(x_coordinate) - 45, int(y_coordinate), mark)

        painter.setPen(QPen(QColor("#696003"), 5))
        for i in range(60):
            angle = math.radians(i * 6)
            end_point = 250
            if (i * 6) % 90 == 0:
                painter.setPen(QPen(QColor("#b09405"), 17))
                end_point = 220
            elif (i * 6) % 30 == 0:
                painter.setPen(QPen(QColor("#b09405"), 15))
            else:
                painter.setPen(QPen(QColor("#b09405"), 10))
            x_start = int(self.x_center + end_point * math.cos(angle))
            y_start = int(self.y_center + end_point * math.sin(angle))

            x_end = int(self.x_center + 275 * math.cos(angle))
            y_end = int(self.y_center + 275 * math.sin(angle))
            painter.drawLine(x_start, y_start, x_end, y_end)

    def update_angle(self):
        #if not self.is_paused:
            current_time = time.time()
            elapsed_seconds = current_time - self.start_time - self.total_paused_time  # ile sekund (z ułamkiem) minęło od startu
        # Wskazówka obraca się o 6 stopni na sekundę
            self.angle_0 = math.radians((elapsed_seconds * 6) % 360)
            self.angle_1 = math.radians(((elapsed_seconds + 15) * 6) % 360)
            self.angle_2 = math.radians(((elapsed_seconds + 30) * 6) % 360)
            self.angle_3 = math.radians(((elapsed_seconds + 45) * 6) % 360)

            self.update()



def main():
    app = QApplication(sys.argv)
    window = TrainingWindow()
    window.showFullScreen()
    window.resize(1024, 600)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
