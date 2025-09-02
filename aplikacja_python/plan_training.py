import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit, QLayout, QSpacerItem, QScrollArea
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint

import math
import time

import add_task


class PlanTraining(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.background = QPixmap("icons/basen3.jpg")
        self.plus_button = QPushButton(self)
        self.save_button = QPushButton(self)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.plus_button.setIcon(QIcon("icons/plus.png"))
        self.plus_button.clicked.connect(self.add_task)
        self.training_name_label = QLabel("Training name:", self)
        self.training_name = QTextEdit(self)
        self.task_counter = 1
        self.spacer_item = QSpacerItem(1024, 100, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer_item2 = QSpacerItem(1024, 50, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.font_size = int(self.available_height * 0.04)
        self.font_size_2 = int(self.available_height * 0.03)


        self.labels = [self.training_name_label]


        self.button_size = int(self.available_height * 0.1)
        self.plus_button.setIconSize(QSize(self.button_size, self.button_size))

        self.upper_layout = QHBoxLayout()
        self.training_name_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.plus_layout = QHBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.adding_tasks_layout = QVBoxLayout(self.scroll_widget)
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()


        self.init_ui()
        self.layout_setting()
        self.save_button_clicked()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.drawPixmap(self.rect(), self.background)

        painter.setPen(QPen(400))
        painter.drawLine(0, 170, 1024, 170)






    def init_ui(self):
        radius = self.button_size // 2
        self.plus_button.setStyleSheet(f"""
        QPushButton {{
                        background-color: rgba(255, 255, 255, 0.6);
                        font: bold {self.font_size_2 * 3}px 'Segoe UI';
                        border-radius: {radius}px;
                        color: white;
                        align: center;
                        }}
                        
        QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.6);
                        padding-top: 3px;
                        padding-left: 3px;
                        }}
        """)
        self.plus_button.setIconSize(QSize(int(self.button_size*0.8), int(self.button_size*0.8)))

        self.save_button.setText("Save")
        self.save_button.setStyleSheet(f"""
        QPushButton {{
                        background-color: rgba(0, 0, 0, 0.8);
                        font: bold {self.font_size}px 'Segoe UI';
                        border-radius: {radius/2}px;
                        color: white;
                        align: center;
                        }}
                        
        QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.6);
                        padding-top: 3px;
                        padding-left: 3px;
                        }}
        """)
        self.save_button.setMaximumWidth(self.available_width // 4)


        self.training_name.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 25px 'Segoe UI';"
                                         "font-weight: bold;")
        self.training_name.setAlignment(Qt.AlignCenter)



        for label in self.labels:
            label.setStyleSheet("color: white;"
                                f"font: {self.font_size}px 'Segoe UI';"
                                "font-weight: bold;")


        self.training_name.setMaximumHeight(self.available_height // 16)
        self.training_name.setMinimumWidth(self.available_width // 4)


        self.plus_button.setFixedSize(self.button_size, self.button_size)

        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")


    def layout_setting(self):
        self.training_name_layout.addStretch(1)
        self.training_name_layout.addWidget(self.training_name_label)
        self.training_name_layout.addStretch(6)
        self.training_name_layout.addWidget(self.training_name)
        self.training_name_layout.addStretch(12)


        self.plus_layout.addStretch(1)
        self.plus_layout.addWidget(self.plus_button)
        self.plus_layout.addStretch(12)

        self.adding_tasks_layout.addLayout(self.plus_layout)
        self.adding_tasks_layout.addStretch(5)

        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.save_button, stretch = 5)
        self.lower_layout.addStretch(1)

        self.main_layout.addItem(self.spacer_item2)
        self.main_layout.addLayout(self.training_name_layout)
        self.main_layout.addItem(self.spacer_item)
        self.main_layout.addWidget(self.scroll_area, stretch=6)
        self.main_layout.addItem(self.spacer_item)
        self.main_layout.addLayout(self.lower_layout)


        self.setLayout(self.main_layout)



    def add_task(self):


        new_layout = QHBoxLayout()
        task_label = QLabel(self)
        task_label.setText("Task " + str(self.task_counter))
        task_name = task_label.text()

        self.task_window = add_task.AddTask(task_name)
        self.task_window.showFullScreen()

        new_layout.addStretch(1)
        new_layout.addWidget(task_label)
        new_layout.addStretch(6)


        index = self.adding_tasks_layout.indexOf(self.plus_layout)

        self.adding_tasks_layout.insertLayout(index, new_layout)
        self.adding_tasks_layout.insertStretch(index, 1)


        task_label.setStyleSheet("color: white;"
                                f"font: {self.font_size_2}px 'Segoe UI';"
                                "font-weight: bold;")


        self.task_counter += 1

    def save_button_clicked(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    window = PlanTraining()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()