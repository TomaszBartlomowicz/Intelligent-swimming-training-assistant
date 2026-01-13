import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSizePolicy, QTextEdit, QPlainTextEdit, QLayout, QSpacerItem, QScrollArea, QLineEdit, QComboBox
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint


from virtual_keyboard import VirtualKeyboard
import math
import time
import json

class AddTask(QWidget):
    def __init__(self, training_name, task_name):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.default_task_name = task_name
        self.training_name = training_name

        # Declaring Labels
        self.meters_label = QLabel("meters", self)
        self.x_label = QLabel("x", self)
        self.time_limit_label = QLabel("Time limit:", self)
        self.hear_rate_label = QLabel("Target heart rate zone:", self)
        self.block_rep_label = QLabel("Repeat everything", self)
        self.times_label = QLabel("times", self)
        self.labels = [self.x_label, self.meters_label,
                       self.time_limit_label, self.hear_rate_label,
                       self.block_rep_label, self.times_label]


        # Declaring user inputs
        self.hear_rate = QComboBox(self)
        self.task_name = QLineEdit(self)
        self.meters_input = QLineEdit(self)
        self.time_limit = QComboBox(self)
        self.reps_input = QLineEdit(self)
        self.block_rep = QLineEdit(self)
        self.detailed_description = QPlainTextEdit(self)

        self.editables = [self.task_name, self.meters_input, self.reps_input, self.detailed_description,
                           self.hear_rate, self.time_limit, self.block_rep]

        self.editable_line_edits = [self.meters_input, self.reps_input, self.detailed_description,
                            self.block_rep]

        # Save button
        self.save_button = QPushButton(self)
        self.save_button.clicked.connect(self.save_button_clicked)

        # Declaring spacer items
        self.spacer_item = QSpacerItem(1024, 100, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.spacer_item2 = QSpacerItem(1024, 50, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Available font sizes
        self.font_size = int(self.available_height * 0.04)
        self.font_size_2 = int(self.available_height * 0.03)
        self.font_size_3 = int(self.available_height * 0.05)

        # Declaring layouts
        self.upper_layout = QVBoxLayout()
        self.repetitions_layout = QHBoxLayout()
        self.description_layout = QVBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.save_layout = QHBoxLayout()
        self.main_layout = QHBoxLayout()

        # Initializing keyboard
        self.keyboard = VirtualKeyboard()
        self.keyboard.hide()  # na start ukryta


        # Calling necessary functions
        self.init_ui()
        self.layout_setting()
        self.time_limit_managment()
        self.hear_rate_zones_managment()
        self.connect_line_edits()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient Seeting
        gradient = QLinearGradient(0, 0, 1920, 1080)
        gradient.setColorAt(0, QColor("#0f0f0f"))
        gradient.setColorAt(0.3, QColor("#1a1919"))
        gradient.setColorAt(0.6, QColor("#242323"))
        gradient.setColorAt(1, QColor("#333333"))
        painter.fillRect(self.rect(), gradient)

    def init_ui(self):
        for label in self.labels:
            label.setStyleSheet("color: white;"
                                 f"font: {self.font_size}px 'Segoe UI';"
                                 "font-weight: bold;")

        for editable in self.editables:
            editable.setStyleSheet("background-color: rgba(0, 0, 0, 0.6);"
                                         "color: white;"
                                         "border-radius: 10px;"
                                         "padding: 10px;"
                                         "font: 25px 'Segoe UI';"
                                         "font-weight: bold;")

        self.save_button.setStyleSheet(f"""
                QPushButton {{
                                background-color: rgb(255, 255, 255, 0.8);
                                font: {self.font_size_3}px 'Segoe UI';
                                font-weight: bold;
                                border-radius: 10px;
                                color: black;
                                align: center;
                                }}

                QPushButton:pressed {{
                                background-color: rgba(0, 0, 0, 0.6);
                                padding-top: 3px;
                                padding-left: 3px;
                                }}
                """)

        self.save_button.setText("Save")
        self.save_button.setMinimumSize(self.available_width // 4, self.available_height // 20)

        
        self.reps_input.setAlignment(Qt.AlignCenter)
        self.meters_input.setAlignment(Qt.AlignCenter)
        self.block_rep.setAlignment(Qt.AlignCenter)

        self.task_name.setReadOnly(True)

        self.detailed_description.setFixedSize(self.available_width // 2,
                                               self.available_height // 2)

        self.time_limit.setFixedSize(self.available_width // 10,
                                               self.available_height // 14)


        self.hear_rate.setFixedSize(self.available_width // 7,
                                               self.available_height // 14)

        self.block_rep.setFixedSize(self.available_width // 15,
                                               self.available_height // 15)
        self.reps_input.setFixedSize(self.available_width // 15,
                                               self.available_height // 15)
        self.meters_input.setFixedSize(self.available_width // 13,
                                               self.available_height // 15)

        self.detailed_description.setPlaceholderText("Enter detailed description here...")
        self.task_name.setPlaceholderText(self.default_task_name)
        #self.detailed_description.setAlignment(Qt.AlignTop)

    def layout_setting(self):

        
        self.repetitions_layout.addWidget(self.reps_input)
        self.repetitions_layout.addWidget(self.x_label)
        self.repetitions_layout.addWidget(self.meters_input)
        self.repetitions_layout.addWidget(self.meters_label)
        self.repetitions_layout.addStretch(5)

        self.upper_layout.addStretch(2)
        #self.upper_layout.addLayout(self.repetitions_layout)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.time_limit_label)
        self.upper_layout.addWidget(self.time_limit)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.hear_rate_label)
        self.upper_layout.addWidget(self.hear_rate)
        self.upper_layout.addStretch(2)
        self.upper_layout.addLayout(self.lower_layout)
        self.upper_layout.addStretch(3)


        self.description_layout.addStretch(1)
        self.description_layout.addWidget(self.task_name)
        self.description_layout.addStretch(4)
        self.description_layout.addLayout(self.repetitions_layout)
        self.description_layout.addStretch(1)
        self.description_layout.addWidget(self.detailed_description, stretch=10)
        self.description_layout.addStretch(1)
        
        self.description_layout.addStretch(3)
        self.description_layout.addLayout(self.save_layout)
        self.description_layout.addStretch(1)

        self.save_layout.addStretch(20)
        self.save_layout.addWidget(self.save_button)
        self.save_layout.addStretch(1)



        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.block_rep_label)
        self.lower_layout.addWidget(self.block_rep)
        self.lower_layout.addWidget(self.times_label)
        self.lower_layout.addStretch(10)


        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.description_layout)
        self.main_layout.addStretch(2)
        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addStretch(1)
        #self.main_layout.addWidget(self.save_button)
        self.setLayout(self.main_layout)

    def save_button_clicked(self):
        # task_number = 0
        task_description = self.detailed_description.toPlainText()
        amount = self.reps_input.text()
        heart_rate = self.hear_rate.currentText()
        time_limit = self.time_limit.currentText()
        meters = self.meters_input.text()
        block_reps = self.block_rep.text()
        task_data = {
            "task_name": self.task_name.text(),
            "ammount_reps": amount,
            "meters": meters,
            "detailed_description": task_description,
            "target_heart_rate": heart_rate,
            "time_limit": time_limit,
            "block_reps": block_reps
        }
        with open(f"planned_trainings/{self.training_name}/{self.default_task_name}.json", 'w') as task_file:
            json.dump(task_data, task_file, indent=4)

        self.close()

    def time_limit_managment(self):
        self.time_limit.addItem("None")
        for minutes in range(0, 6):
            for seconds in range(0, 60, 5):
                if minutes == 0 and seconds <= 20:
                    pass
                else:
                    self.time_limit.addItem(f"{str(minutes)}'{str(seconds).zfill(2)}")

    def hear_rate_zones_managment(self):
        self.hear_rate.addItem("None")
        for i in range(60, 200, 20):
            self.hear_rate.addItem(str(i) + "-" + str(i + 20))

    def connect_line_edits(self):
        for line_edit in self.editable_line_edits:
            line_edit.mousePressEvent = lambda event, e=line_edit: self.show_keyboard(event, e)

    def show_keyboard(self, event, editable):
        self.keyboard.set_target(editable)  # powiedz klawiaturze, do którego pola ma wpisywać
        self.keyboard.show()
        if isinstance(editable, QPlainTextEdit):
             return QPlainTextEdit.mousePressEvent(editable, event)
        else:
            return QLineEdit.mousePressEvent(editable, event)  # zachowaj standardowe zachowanie (kursor itp.)

    def mousePressEvent(self, event):
        for window in QApplication.topLevelWidgets():
            if window.windowTitle() == "Virtual Keyboard":
                window.close()
    
def main():
    app = QApplication(sys.argv)
    window = AddTask(training_name="Trening 1", task_name= "dupa")
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()