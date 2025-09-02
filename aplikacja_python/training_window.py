import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
import training_window2

import math
import time


class TrainingWindow1(QWidget):
    def __init__(self):
        super().__init__()

        # Get used screen parameters
        self.app = QApplication.instance()
        self.screen = self.app.primaryScreen()
        self.available_height = self.screen.availableGeometry().height()
        self.available_width = self.screen.availableGeometry().width()


        self.background = QPixmap("icons/basen3.jpg")


        # Declaring buttons and labels
        self.heart_rate_button = QPushButton(self, text=" 74")
        self.saturation_button = QPushButton(self, text=" 98%")
        self.parameters_buttons = [self.heart_rate_button, self.saturation_button]
        #self.time_label = QLabel("00:00", self)
        self.heart_rate_button.setIcon(QIcon("icons/heart_rate.png"))
        self.saturation_button.setIcon(QIcon("icons/saturation.png"))

        self.current_set_label = QLabel(self)
        self.current_set_label.setText(" Next set:")
        self.task_label = QLabel(self)
        self.task_label.setText(" 10 x 100m ")
        self.start_button = QPushButton(self, text="START")
        self.end_button = QPushButton(self, text="END TRAINING")



        self.details = "kraul co druga huj wie czym cos tam cos tam cos tam cos tam raz dwa trzy joł"
        self.limit = "1:30"
        self.desired_heart_rate = "120 - 130"
        self.details_text_window = QPlainTextEdit()

        self.details_text_window.appendPlainText(self.details)
        self.details_text_window.appendPlainText("\n")
        self.details_text_window.appendPlainText(f"Limit: {self.limit}\nZakres tętna: {self.desired_heart_rate}")
        self.details_text_window.setReadOnly(True)


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
        self.wall_clock_timer.start(10)

        # Thickness and other
        self.font_size = int(self.available_height * 0.04)
        self.clock_x_center = self.available_width * 0.72
        self.clock_y_center = self.available_height * 0.5
        self.arrow_length = self.available_height * 0.4
        self.arrows_thickness = self.available_height * 0.035
        self.yellow_circle_radius = int(self.available_height * 0.033)
        self.marker_thickness_1 = self.available_height * 0.035
        self.marker_thickness_2 = self.available_height * 0.025

        self.emoji_timer = QTimer(self)
        self.emoji_timer.start(1000)
        self.emoji_timer.timeout.connect(lambda: self.toggle_emoji_size())

        # Functions calling
        self.layout_settings()
        self.init_ui()
        self.connecting_buttons()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self.rect(), self.background)

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
            text_box_width = 85
            text_box_height = 85
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
                box_y = self.clock_y_center + self.arrow_length * math.sin(angle) + text_box_height / 2

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


        # Clock arrows settings
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


        # Timer
        self.clock_time = "00:00"
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



        self.start_button.setStyleSheet("background-color: #096301;"
                                             "color: white;"
                                             "font: bold;"
                                             "font-size: 30px;"
                                             "border-radius: 10px;"
                                             "padding: 10px;")


        self.end_button.setStyleSheet("background-color: #080808;"
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


        self.heart_rate_button.setIconSize(QSize(90, 90))
        self.saturation_button.setIconSize(QSize(90, 90))

        self.heart_rate_button.setFixedSize(220, 100)
        self.saturation_button.setFixedSize(220, 100)

        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def layout_settings(self):

        #self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.heart_rate_button)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.saturation_button)
        self.upper_layout.addStretch(400)

        self.current_set_layout.addWidget(self.current_set_label)
        self.current_set_layout.addWidget(self.task_label)
        self.current_set_layout.addStretch(100)
        self.current_set_layout.addStretch(73)

        self.middle_layout.addWidget(self.details_text_window, stretch=7)
        self.middle_layout.addStretch(10)

        self.lower_layout.addStretch(1)


        self.lower_layout.addWidget(self.start_button)
        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.end_button)
        self.lower_layout.addStretch(2)
        self.lower_layout.addStretch(20)

        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(2)
        self.main_layout.addLayout(self.current_set_layout)
        #self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.middle_layout, stretch=20)
        self.main_layout.addStretch(3)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(3)
        self.setLayout(self.main_layout)


    def toggle_emoji_size(self):
        if self.heart_rate_button.iconSize() == QSize(70, 70):
            self.heart_rate_button.setIconSize(QSize(60, 60))
            self.saturation_button.setIconSize(QSize(60, 60))
        else:
            self.heart_rate_button.setIconSize(QSize(70, 70))
            self.saturation_button.setIconSize(QSize(70, 70))

    def connecting_buttons(self):
        self.start_button.clicked.connect(self.start_button_clicked)


    def start_button_clicked(self):
        self.training_window = training_window2.TrainingWindow()
        self.training_window.showFullScreen()
        self.close()





def main():
    app = QApplication(sys.argv)
    window = TrainingWindow1()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
