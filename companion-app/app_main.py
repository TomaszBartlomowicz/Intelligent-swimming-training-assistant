from splash_screen import LoadingScreen
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QIcon, QPixmap




def main():
    app = QApplication(sys.argv)
    splash = LoadingScreen()
    splash.showFullScreen()
    sys.exit(app.exec_())





if __name__ == "__main__":
    main()