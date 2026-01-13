from app_config import (BACKGROUND, PLAN_WINDOW_PLUS_BUTTON_STYLE, SAVE_BUTTON_STYLE,
                        RETURN_BUTTON_STYLE, SCROLL_AREA_STYLE, TRAINING_NAME_STYLE, MSG_STYLE)
import os
from PyQt5.QtWidgets import (QWidget, QMessageBox, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
    QSizePolicy, QLineEdit, QScrollArea)
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
import math, time, shutil 

import virtual_keyboard, add_task


class PlanTraining(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.screen = QApplication.primaryScreen()
        self.available_height = self.screen.geometry().height()
        self.available_width = self.screen.geometry().width()

        self.background = QPixmap(BACKGROUND)

        # Initializing buttons
        self.plus_button = QPushButton(self)
        self.save_button = QPushButton(self)
        self.return_button = QPushButton(self)
        self.save_button.hide()

        # Flags
        self.training_name_accepted = False
        self.is_training_created = False
        

        # Initializing virtual keyboard
        self.keyboard = virtual_keyboard.VirtualKeyboard()

        self.training_name = QLineEdit(self)
        self.task_counter = 1

        # Msg box
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setWindowFlags(Qt.Popup)
        self.msg.setAttribute(Qt.WA_TranslucentBackground)

    
        # Declaring layouts and scroll area
        self.upper_layout = QHBoxLayout()
        self.training_name_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.tasks_layout = QHBoxLayout()
        self.plus_layout = QHBoxLayout()
        self.return_button_layout = QHBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.adding_tasks_layout = QVBoxLayout(self.scroll_widget)
        self.lower_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()


        # Calling necessary functions
        self.init_ui()
        self.layout_setting()
        self.connect_buttons()
        self.connect_line_edit_to_keyboard()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.drawPixmap(self.rect(), self.background)


    def init_ui(self):
        # Plus button style
        self.plus_button.setFixedSize(120, 120)
        self.plus_button.setStyleSheet(PLAN_WINDOW_PLUS_BUTTON_STYLE)
        self.plus_button.setIcon(QIcon("icons/plus.png"))
        self.plus_button.setIconSize(QSize(80, 80))
        
        # Save button style
        self.save_button.setText("Save")
        self.save_button.setStyleSheet(SAVE_BUTTON_STYLE)
        self.save_button.setMaximumWidth(self.available_width // 4)

        # Return button style
        self.return_button.setIcon(QIcon("icons/return.png"))
        self.return_button.setStyleSheet(RETURN_BUTTON_STYLE)
        self.return_button.setIconSize(QSize(80, 80))
        self.return_button.setFixedSize(90, 80)

        # Training name style
        self.training_name.setStyleSheet(TRAINING_NAME_STYLE)
        self.training_name.setAlignment(Qt.AlignCenter)
        self.training_name.setPlaceholderText("Enter training name!")
        self.training_name.setMaximumHeight(self.available_height // 8)
        self.training_name.setMinimumWidth(self.available_width // 3)

        # Scroll area
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

        # MSG Box
        self.msg.setStyleSheet(MSG_STYLE)


    def layout_setting(self):
        self.training_name_layout.addStretch(12)
        self.training_name_layout.addWidget(self.training_name)
        self.training_name_layout.addStretch(12)

        self.lower_layout.addStretch(1)
        self.lower_layout.addWidget(self.save_button, stretch = 5)
        self.lower_layout.addStretch(1)

        self.return_button_layout.addStretch(2)
        self.return_button_layout.addWidget(self.return_button)
        self.return_button_layout.addStretch(20)
        self.return_button_layout.addWidget(self.plus_button)
        self.return_button_layout.addStretch(2)

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.training_name_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.scroll_area, stretch=8)
        self.main_layout.addLayout(self.return_button_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.lower_layout)
        self.main_layout.addStretch(1)
        
        self.setLayout(self.main_layout)



    def plus_clicked(self):
        # Check if training name was given
        training_name = self.training_name.text()
        if not training_name:
            self.msg.setText("Enter training name first!")
            self.msg.setWindowTitle("No trainign name chosen")
            self.msg.show() # tu czeka aż użytkownik kliknie OK
            return

        # Check if training name is free to use
        if not self.is_training_created:
            if training_name in os.listdir("planned_trainings"):
                self.msg.setText("Choose a different training name!")
                self.msg.setWindowTitle("Training name already exists!")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.show()
                return



        new_layout = QHBoxLayout()
        task_label = QLabel()
        task_label.setText("Task " + str(self.task_counter))
        task_name = task_label.text()

        new_layout.addStretch(21)
        new_layout.addWidget(task_label)
        new_layout.addStretch(20)


        index = self.adding_tasks_layout.indexOf(self.plus_layout)

        self.adding_tasks_layout.insertLayout(index, new_layout)
        self.adding_tasks_layout.insertStretch(index, 1)


        task_label.setStyleSheet("color: white;"
                                f"font: 30px 'Segoe UI';"
                                "font-weight: bold;")
        
        self.save_button.show()
        
        if not self.is_training_created:
            os.mkdir(f"planned_trainings/{training_name}")
            with open(f"planned_trainings/{training_name}/training_data.txt", 'w') as file:
                file.write(f"Training Name: {training_name}\n")

                
        self.is_training_created = True
        self.task_counter += 1

        self.task_window = add_task.AddTask(training_name, task_name)
        self.task_window.showFullScreen()


    def connect_buttons(self):
        self.save_button.clicked.connect(self.save_button_clicked)
        self.plus_button.clicked.connect(self.plus_clicked)
        self.return_button.clicked.connect(self.return_button_clicked)

    def save_button_clicked(self):
        self.close()

    def return_button_clicked(self): 
        training_name = self.training_name.text().strip()  # usuń spacje
        if training_name:  # zabezpieczenie przed pustym stringiem
            shutil.rmtree(f"planned_trainings/{training_name}")
        self.close()

    def connect_line_edit_to_keyboard(self):
        self.training_name.mousePressEvent = lambda event: self.show_keyboard(event)

    def show_keyboard(self, event):
        self.keyboard.set_target(self.training_name)  # powiedz klawiaturze, do którego pola ma wpisywać
        self.keyboard.show()
        return QLineEdit.mousePressEvent(self.training_name, event)  # zachowaj standardowe zachowanie (kursor itp.)

    def mousePressEvent(self, event):
        for window in QApplication.topLevelWidgets():
            if window.windowTitle() == "Virtual Keyboard":
                window.close()






