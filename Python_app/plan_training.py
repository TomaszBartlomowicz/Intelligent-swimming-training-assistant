import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit, QLayout, QSpacerItem
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint

import math
import time


class PlanTraining(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(0,0, 1024, 600)
        self.background = QPixmap("icons/basen1.jpg")
        self.plan_training_label = QLabel("Plan your training session here", self)
        self.plan_training_label.hide()
        self.warmup_label = QLabel("Task 1", self)
        self.plus_button = QPushButton("+", self)
        self.plus_button.clicked.connect(self.add_task)
        self.x_label = QLabel("x", self)
        self.training_name_label = QLabel("Training name", self)
        self.date_label = QLabel("Date", self)
        self.date = QPlainTextEdit(self)
        self.training_name = QPlainTextEdit(self)
        self.m_label = QLabel('m', self)
        self.task_counter = 2
        self.ammount = QPlainTextEdit(self)
        self.meters = QPlainTextEdit(self)
        self.spacer_item = QSpacerItem(1024, 100, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.details = QPlainTextEdit(self)


        self.labels = [self.plan_training_label, self.warmup_label, self.m_label,
                       self.date_label, self.training_name_label, self.x_label]




        self.upper_layout = QHBoxLayout()
        self.training_name_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.plus_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        self.init_ui()
        self.layout_setting()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.drawPixmap(self.rect(), self.background)

        painter.setPen(QPen(100))
        painter.drawLine(0, 170, 1024, 170)






    def init_ui(self):
        self.plus_button.setStyleSheet("background-color: gray;"
                                       "border-radius: 20px;"
                                       "color: white;"
                                       "padding: 10px;"
                                       "font-size: 50px;")


        self.training_name.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 20px 'Segoe UI';")

        self.date.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 20px 'Segoe UI';")


        for label in self.labels:
            label.setStyleSheet("color: yellow;"
                                "font: 25px 'Segoe UI';"
                                "font-weight: bold;")

        self.ammount.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 20px 'Segoe UI';")

        self.meters.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 20px 'Segoe UI';")

        self.details.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                  "color: white;"
                                  "border-radius: 10px;"
                                  "padding: 10px;"
                                  "font: 20px 'Segoe UI';")


        self.training_name.setMaximumSize(400, 60)
        self.date.setMaximumSize(400, 60)
        self.plus_button.setMaximumSize(60, 60)

        self.ammount.setMaximumSize(80, 60)
        self.meters.setMaximumSize(70, 60)
        self.details.setMaximumSize(800, 60)



    def layout_setting(self):

        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.plan_training_label)
        self.upper_layout.addStretch(1)

        self.training_name_layout.addStretch(1)
        self.training_name_layout.addWidget(self.training_name_label)
        self.training_name_layout.addStretch(1)
        self.training_name_layout.addWidget(self.training_name)
        self.training_name_layout.addStretch(1)
        self.training_name_layout.addWidget(self.date_label)
        self.training_name_layout.addStretch(1)
        self.training_name_layout.addWidget(self.date)
        self.training_name_layout.addStretch(1)

        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.warmup_label)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.ammount)
        self.middle_layout.addWidget(self.x_label)
        self.middle_layout.addWidget(self.meters)
        self.middle_layout.addWidget(self.m_label)
        self.middle_layout.addStretch(1)
        self.middle_layout.addWidget(self.details, stretch = 20)
        self.middle_layout.addStretch(2)

        self.plus_layout.addStretch(1)
        self.plus_layout.addWidget(self.plus_button)
        self.plus_layout.addStretch(10)


        self.main_layout.addLayout(self.upper_layout)

        self.main_layout.addLayout(self.training_name_layout)
        self.main_layout.addItem(self.spacer_item)
        self.main_layout.addLayout(self.middle_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.plus_layout)
        self.main_layout.addStretch(12)

        self.setLayout(self.main_layout)



    def add_task(self):
        new_layout = QHBoxLayout()
        x_label = QLabel("x", self)
        m_label = QLabel('m', self)
        ammount = QPlainTextEdit(self)
        meters = QPlainTextEdit(self)
        details = QPlainTextEdit(self)
        task_label = QLabel(self)
        task_label.setText("Task " + str(self.task_counter))
        labels = [m_label, x_label, task_label]

        new_layout.addStretch(1)
        new_layout.addWidget(task_label)
        new_layout.addStretch(1)
        new_layout.addWidget(ammount)
        new_layout.addWidget(x_label)
        new_layout.addWidget(meters)
        new_layout.addWidget(m_label)
        new_layout.addStretch(1)
        new_layout.addWidget(details, stretch = 10)
        new_layout.addStretch(2)

        index = self.main_layout.indexOf(self.plus_layout)

        self.main_layout.insertLayout(index, new_layout)
        self.main_layout.insertStretch(index, 1)

        ammount.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                   "color: white;"
                                   "border-radius: 10px;"
                                   "padding: 10px;"
                                   "font: 20px 'Segoe UI';")

        meters.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                  "color: white;"
                                  "border-radius: 10px;"
                                  "padding: 10px;"
                                  "font: 20px 'Segoe UI';")

        details.setStyleSheet("background-color: rgba(0, 0, 0, 0.4);"
                                   "color: white;"
                                   "border-radius: 10px;"
                                   "padding: 10px;"
                                   "font: 20px 'Segoe UI';")

        for label in labels:
            label.setStyleSheet("color: #d7f705;"
                                "font: 25px 'Segoe UI';"
                                "font-weight: bold;")

        ammount.setMaximumSize(80, 60)
        meters.setMaximumSize(70, 60)
        details.setMaximumSize(800, 60)
        self.task_counter += 1

def main():
    app = QApplication(sys.argv)
    window = PlanTraining()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()