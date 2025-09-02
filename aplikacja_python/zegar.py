import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPixmap


class PaceClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basenowy Zegar Kolorowy")
        self.resize(1024, 600)

        ## Arrow angles
        self.angle_0 = math.radians(90)
        self.angle_1 = math.radians(180)
        self.angle_2 = math.radians(270)
        self.angle_3 = math.radians(360)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(100)
        self.x_center = 1024 / 2
        self.y_center = 600 / 2
        self.arrow_length = 230
        self.clock_widget = QPixmap(self.size())
        self.draw_clock(self.clock_widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(0, 0, self.clock_widget)
        # Draw lines

        painter.setPen(QPen(QColor("black"), 25))
        x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_0))
        y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_0))

        # Zegar lines
        for i in range(4):
            if i == 1:
                painter.setPen(QPen(QColor("#1025e0"), 25))
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_1))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_1))
            elif i == 2:
                painter.setPen(QPen(QColor("green"), 25))
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_2))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_2))
            elif i == 3:
                painter.setPen(QPen(QColor("red"), 25))
                x_end = int(self.x_center + self.arrow_length * math.cos(self.angle_3))
                y_end = int(self.y_center + self.arrow_length * math.sin(self.angle_3))


            painter.drawLine(int(self.x_center), int(self.y_center), x_end, y_end)

        # Small middle circle
        painter.setPen(QPen(QColor("#d9ce04")))
        painter.setBrush(QColor("#d9ce04"))
        radius = 20
        painter.drawEllipse(512 - radius, 300 - radius, 2* radius, 2* radius)

    def draw_clock(self, clock_widget):
        painter = QPainter(clock_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient Seeting
        gradient = QLinearGradient(0, 0, 1024, 600)
        gradient.setColorAt(0, QColor("white"))
        gradient.setColorAt(1, QColor("white"))
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

        painter.setPen(QPen(QColor("#d9ce04"), 5))
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
        self.angle_0 = (self.angle_0 + math.radians(0.6)) % (2 * math.pi)
        self.angle_1 = (self.angle_1 + math.radians(0.6)) % (2 * math.pi)
        self.angle_2 = (self.angle_2 + math.radians(0.6)) % (2 * math.pi)
        self.angle_3 = (self.angle_3 + math.radians(0.6)) % (2 * math.pi)
        self.update()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    clock = PaceClock()
    clock.show()
    sys.exit(app.exec_())
