import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer, QRect

import math
import time


class TrainingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.is_paused = False

        # Get used screen parameters
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()
        self.setGeometry(0, 0, self.available_width, self.available_height)


        # Declaring buttons and labels

        self.heart_rate_button = QPushButton(self, text=" 74")
        self.saturation_button = QPushButton(self, text=" 98%")
        self.parameters_buttons = [self.heart_rate_button, self.saturation_button]
        self.saturation_button.setIcon(QIcon("icons/saturation.png"))
        self.clock_time = "00:00"
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


        # Thickness and other
        self.font_size = int(self.available_height * 0.04)
        self.clock_x_center = self.available_width * 0.72
        self.clock_y_center = self.available_height * 0.5
        self.arrow_length = self.available_height * 0.4
        self.arrows_thickness = self.available_height * 0.035
        self.yellow_circle_radius = int(self.available_height * 0.033)
        self.marker_thickness_1 = self.available_height * 0.035
        self.marker_thickness_2 = self.available_height * 0.02


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
        print(self.size())
        self.wall_clock_timer = QTimer(self)
        self.wall_clock_timer.timeout.connect(self.update_angle)
        self.wall_clock_timer.timeout.connect(self.update_timer)
        self.wall_clock_timer.start(33)
        self.x_center = 730
        self.y_center = 600 / 2
        self.clock_widget = QPixmap(self.available_width, self.available_height)
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
        painter.drawPixmap(0, 0, self.clock_widget)

        painter.setPen(QPen(QColor("black"), self.arrows_thickness))
        x_end = int(self.clock_x_center + self.arrow_length * math.cos(self.angle_0))
        y_end = int(self.clock_y_center + self.arrow_length * math.sin(self.angle_0))
        for i in range(4):
            if i == 1:
                painter.setPen(QPen(QColor("#032782"), self.arrows_thickness))  # niebieski
                x_end = int(self.clock_x_center + self.arrow_length * math.cos(self.angle_1))
                y_end = int(self.clock_y_center + self.arrow_length * math.sin(self.angle_1))
            elif i == 2:
                painter.setPen(QPen(QColor("#820903"), self.arrows_thickness))  # czerwony
                x_end = int(self.clock_x_center + self.arrow_length * math.cos(self.angle_2))
                y_end = int(self.clock_y_center + self.arrow_length * math.sin(self.angle_2))
            elif i == 3:
                painter.setPen(QPen(QColor("#1c8203"), self.arrows_thickness))  # zielony
                x_end = int(self.clock_x_center + self.arrow_length * math.cos(self.angle_3))
                y_end = int(self.clock_y_center + self.arrow_length * math.sin(self.angle_3))

            painter.drawLine(int(self.clock_x_center), int(self.clock_y_center), x_end, y_end)

        # Small middle circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        circle_width = int(self.yellow_circle_radius * 2)
        circle_height = int(self.yellow_circle_radius * 2)
        painter.drawEllipse(int(self.clock_x_center) - self.yellow_circle_radius,
                                int(self.clock_y_center) - self.yellow_circle_radius, circle_width, circle_height)

        # Timer
        painter.setPen(QPen(QColor("white")))
        font = painter.font()
        font.setPointSize(self.font_size)
        font.setBold(True)
        painter.setFont(font)
        text_box_width = 200
        text_box_height = 100
        # Wylicz pozycję X lewego górnego rogu pudełka, aby było na środku zegara
        box_x = self.clock_x_center - (text_box_width / 2)
        box_y = self.clock_y_center * 0.5
        text_rect = QRect(int(box_x), int(box_y), text_box_width, text_box_height)
        painter.drawText(text_rect, Qt.AlignCenter, self.clock_time)

    def init_ui(self):
        for button in self.parameters_buttons:
            button.setStyleSheet("background-color: rgba(0, 0, 0, 0);"
                                 "border: None;"
                                 "color: white;"
                                 "font: 50pt 'Segoe UI';"
                                 "font-weight: bold;")

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
            self.clock_time = f"{secs}"
        elif 0 < self.start_time + 15 + self.total_paused_time - time.time() < 1 :

            self.clock_time ="GO!"
        else:

            elapsed_seconds = time.time() - self.start_time - self.total_paused_time - 15
            mins = round(elapsed_seconds // 60)
            secs = round(elapsed_seconds) % 60

            self.clock_time = f"{mins:02d}:{secs:02d}"


    def draw_clock(self, clock_widget):
        painter = QPainter(clock_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient Seeting
        gradient = QLinearGradient(0, 0, 1920, 1080)
        gradient.setColorAt(0, QColor("#0f0f0f"))
        gradient.setColorAt(0.3, QColor("#1a1919"))
        gradient.setColorAt(0.6, QColor("#242323"))
        gradient.setColorAt(1, QColor("#333333"))
        painter.fillRect(self.rect(), gradient)

        ## Draw number
        angle_and_marks = {
            270: "60",  # godzina 12:00 (na górze)
            330: "10",
            30: "20",
            90: "30",  # godzina 6:00 (na dole)
            150: "40",
            210: "50"
        }

        font = painter.font()
        font.setPointSize(self.font_size)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor("yellow")))

        # Painting clock minutes
        for degree, mark in angle_and_marks.items():
            angle = math.radians(degree)
            text_box_width = 70
            text_box_height = 70
            # Wylicz pozycję X lewego górnego rogu pudełka, aby było na środku zegara

            if mark == "50":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "40":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle)
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "10":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "20":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height / 2

            elif mark == "60":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle)

            elif mark == "30":
                box_x = self.clock_x_center + self.arrow_length * math.cos(angle) - text_box_width / 2
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) - text_box_height

            text_rect = QRect(int(box_x), int(box_y), text_box_width, text_box_height)
            painter.drawText(text_rect, Qt.AlignCenter, mark)




        #Painting clock markers
        for i in range(60):
            angle = math.radians(i * 6)
            clk_marker_start_pos = self.available_width * 0.25
            clk_marker_end_pos = self.available_width * 0.27

            if (i * 6) % 90 == 0:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_1))
                clk_marker_start_pos = self.available_width * 0.242
            elif (i * 6) % 30 == 0:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_2))
                clk_marker_start_pos = self.available_width * 0.245
            else:
                painter.setPen(QPen(QColor("#edd711"), self.marker_thickness_2))
            x_start = int(self.clock_x_center + clk_marker_start_pos * math.cos(angle))
            y_start = int(self.clock_y_center + clk_marker_start_pos * math.sin(angle))

            x_end = int(self.clock_x_center + clk_marker_end_pos * math.cos(angle))
            y_end = int(self.clock_y_center + clk_marker_end_pos * math.sin(angle))
            painter.drawLine(x_start, y_start, x_end, y_end)


        # Small middle circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        circle_width = int(self.yellow_circle_radius * 2)
        circle_height = int(self.yellow_circle_radius * 2)
        painter.drawEllipse(int(self.clock_x_center) - self.yellow_circle_radius, int(self.clock_y_center) - self.yellow_circle_radius, circle_width, circle_height)

        # Laps left
        painter.setPen(QPen(QColor("white")))
        font = painter.font()
        font.setPointSize(self.font_size)
        font.setBold(True)
        painter.setFont(font)
        reps_left = "6 left"
        # 1. Zdefiniuj prostokątny obszar na tekst w dolnej części zegara.
        # Załóżmy, że promień tarczy zegara to 250px.
        text_box_width = 200
        text_box_height = 100
        # Wylicz pozycję X lewego górnego rogu pudełka, aby było na środku zegara
        box_x = self.clock_x_center - (text_box_width / 2)
        box_y = self.clock_y_center * 1.4
        text_rect = QRect(int(box_x), int(box_y), text_box_width, text_box_height)
        painter.drawText(text_rect, Qt.AlignCenter, reps_left)



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
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
