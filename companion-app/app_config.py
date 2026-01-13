
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap

PROJECT_PATH = "/home/tomraspberry/Inteligent_training_asistant/aplikacja_python"

###----------------------------FONT SIZES ----------------------------###

FONT_1 = "29"
FONT_2 = "23" 
FONT_3 = "20"
FONT_4 = "17" 
FONT_5 = "25"
# FONT_6 = 


### ---------------------COMMON APPLICATION ATRIBUTES-------------------- ###

MAIN_BUTTON_STYLE = """ 
            QPushButton {
                                 background-color: rgba(0, 0, 0, 0.7);
                                 color: white;
                                 font: 615 30pt 'Segoe UI';
                                 border-radius: 15px;
                                 border: 2px solid #2b2b2a;
                                 }
                                 
            QPushButton:pressed {
                                background-color: rgba(25, 25, 25, 0.8);
                                padding-top: 3px;
                                padding-left: 3px;
            }
            """

RETURN_BUTTON_STYLE = """ 
                    QPushButton {
                                         background-color: rgba(0, 0, 0, 0.8);
                                         color: white;
                                         font: 30px 'Segoe UI';
                                         font-weight: bold;
                                         border-radius: 15px;
                                         }

                    QPushButton:pressed {
                                        background-color: rgba(25, 25, 25, 0.8);
                                        padding-top: 3px;
                                        padding-left: 3px;
            }
                    """

SCROLL_AREA_STYLE = "background-color: transparent; border: none;"


SAVE_BUTTON_STYLE = f"""
        QPushButton {{
                        background-color: rgba(0, 0, 0, 0.8);
                        font: bold {FONT_1}pt 'Segoe UI';
                        border-radius: 10px;
                        color: white;
                        
                        }}
                        
        QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.6);
                        padding-top: 3px;
                        padding-left: 3px;
                        }}
        """



## --------------------- MAIN WINDOW -------------------- ###

BACKGROUND = PROJECT_PATH + "/icons/basen3.jpg"



MAIN_WINDOW_MAIN_BUTTON_ICONS = [f"{PROJECT_PATH}/icons/plan.png", f"{PROJECT_PATH}/icons/swimmer.png", f"{PROJECT_PATH}/icons/training_history.png", f"{PROJECT_PATH}/icons/heartt.png"]


MAIN_WINDOW_LOWER_BUTTONS_STYLE = """ 
                QPushButton {
                                     background-color: rgba(0, 0, 0, 0.8);
                                     border-radius: 10px;
                                     padding: 5px;
                                     }
                                     
                QPushButton:pressed {
                                    background-color: rgba(25, 25, 25, 0.8);
                                    padding-top: 3px;
                                    padding-left: 3px;
        }
                """

MAIN_WINDOW_LOWER_BUTTONS_ICONS = [f"{PROJECT_PATH}/icons/info.png", f"{PROJECT_PATH}/icons/power_off.png"]

SENSOR_BUTTON_STYLE = """      QPushButton {
                                    font: bold 20pt 'Segoe UI';
                                    background-color: transparent;
                                    border: solid;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """

CLOCK_BUTTON_STYLE = """      QPushButton {
                                    background-color: rgba(255, 255, 255, 180);
                                    border-radius: 50px;
                                    border: 2px solid;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """


                
TIME_DATE_STYLE = f"""color: white;
                    font: 650 {FONT_1}pt 'Segoe UI';"""


## --------------------- PLAN TRAINING WINDOW  -------------------- ###

PLAN_WINDOW_PLUS_BUTTON_STYLE = f"""
        QPushButton {{
                        background-color: rgba(255, 255, 255, 0.6);
                        border-radius: 60px;
                        border: 1px solid blue;
                        }}
                        
        QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.6);
                        padding-top: 3px;
                        padding-left: 3px;
                        }}
        """


TRAINING_NAME_STYLE = f"""background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font: {FONT_2}pt 'Segoe UI';
                        font-weight: bold;"""


MSG_STYLE = f"""
QLabel {{
    color: white;
    font: {FONT_3}pt 'Segoe UI';
    font-weight: bold;
}}

QPushButton {{
    color: white;
    background-color: rgba(0, 0, 0, 0.7);
    font: 15pt 'Segoe UI';
    font-weight: bold;
    border-radius: 10px;
    padding: 8px 16px;
}}
"""



## --------------------- TRAINING WINDOW  -------------------- ###

PARAMETERS_STYLE = """
                background-color: rgba(0, 0, 0, 0);
                border: None;
                color: white;
                font: 35pt 'Segoe UI';
                font-weight: bold;
            """


LABELS_STYLE = f"""
            background-color: none;
            color: yellow;
            font: 700 35pt 'Segoe UI'
        """


TEXT_EDIT_STYLE = f"""
                background-color: rgba(0, 0, 0, 0.4);
                color: white;
                font: 650 24pt 'Segoe UI';
                border: 3px solid black;
                border-radius: 20px;
                padding: 10px;
            """


START_BUTTON_STYLE = f"""
            background-color: #096301;
            color: white;
            font: 650 24pt 'Segoe UI';
            border-radius: 10px;
            padding: 10px;
        """


SKIP_BUTTON_STYLE = f"""
            background-color: #3c5b73;
            color: white;
            font: 650 24pt 'Segoe UI';
            border-radius: 10px;
            padding: 10px;
        """


END_BUTTON_STYLE = f"""
            background-color: #a3170d;
            color: white;
            font: 650 24pt 'Segoe UI';
            border-radius: 10px;
            padding: 10px;
        """


## --------------------- INFO / POWER OFF  WINDOWS  -------------------- ###

INFO_LABEL_STYLE = f"""color: black;
                    font: {FONT_4}pt 'Segoe UI';
                    font-weight: bold;"""

OK_BUTTON_STYLE = f"""
            QPushButton {{
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
                font: {FONT_4}pt 'Segoe UI';
                font-weight: bold;;
            }}
            QPushButton:hover {{
                background-color: #357abd;
            }}
        """




POWER_OFF_BUTTON_STYLE = """
                                QPushButton {
                                    font: bold 25pt 'Segoe UI';
                                    border-radius: 90px;
                                    color: #8f0b0b;
                                    border: 7px solid #8f0b0b;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """


CANCEL_BUTTON_STYLE = """
                                QPushButton {
                                    font: bold 25pt 'Segoe UI';
                                    border-radius: 90px;
                                    color: #135e09;
                                    border: 7px solid #135e09;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """


QUIT_LABEL_STYLE = f"""color: black;
                    font: {FONT_3}pt 'Segoe UI';
                    font-weight: bold;"""





HR_MAX_LABEL_STYLE = f"""color: white;
                    font: {FONT_1}pt 'Segoe UI';
                    font-weight: bold;"""

RECOVERY_LAVBEL_STYLE = f"""color: #E0E0E0;
                    font: {FONT_5}pt 'Segoe UI';
                    font-weight: bold;"""

AEROBIC_ENDURANCE_STYLE = f"""color: #00E676;
                    font: {FONT_5}pt 'Segoe UI';
                    font-weight: bold;"""

AEROBIC_CAPACITY_STYLE = f"""color: #FFEA00;
                    font: {FONT_5}pt 'Segoe UI';
                    font-weight: bold;"""

ANAEROBIC_STYLE = f"""color: #FF6D00;
                    font: {FONT_5}pt 'Segoe UI';
                    font-weight: bold;"""


VO2_MAX_STYLE = f"""color: #e00202;
                    font: {FONT_5}pt 'Segoe UI';
                    font-weight: bold;"""


GET_HR_MAX_STYLE = """
    QPushButton {
        background-color: #2E2E2E;
        color: #FFD740;
        font: bold 20pt 'Segoe UI';
        border-radius: 15px;
        padding: 12px 25px;
        border: 2px solid rgba(255,255,255,0.1);
    }
    QPushButton:hover {
        background-color: #454545;
    }
    QPushButton:pressed {
        background-color: #5A5A5A;
        padding-top: 3px;
        padding-left: 3px;
    }
"""




## --------------------- DO YOU WANT TO DELETE ? WINDOW  -------------------- ###


DELETE_BUTTON_STYLE = """
                                QPushButton {
                                    font: bold 25pt 'Segoe UI';
                                    border-radius: 60px;
                                    color: #8f0b0b;
                                    border: 5px solid #8f0b0b;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """



CANCEL_BUTTON_STYLE2 = """
                                QPushButton {
                                    font: bold 25pt 'Segoe UI';
                                    border-radius: 60px;
                                    color: #135e09;
                                    border: 5px solid #135e09;
                                }
                                QPushButton:pressed {
                                    padding-top: 3px;
                                    padding-left: 3px;
                                }
                                """


DELETE_LABEL_STYLE = f"""color: white;
                    font: 18pt 'Segoe UI';
                    font-weight: bold;"""




BATTERY_STYLE = """     color: white;
                        font: 23pt 'Segoe UI';
                        font-weight: bold;"""
