"""
Application entry point for the Intelligent Swimming Training Assistant.

"""

from splash_screen import LoadingScreen
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
import sys
import os

def main():
    """
    Coordinates the application startup and hardware-level UI configuration.
    """
    # Initialize the main GUI application instance
    app = QApplication(sys.argv)
    
    # Instantiate and display the splash screen in full-screen mode
    # Note: LoadingScreen handles the transition to MainWindow internally
    splash = LoadingScreen()
    splash.showFullScreen()
    
    # Embedded system optimization: Hide the hardware cursor after a brief delay
    # to ensure the UI renders without a mouse pointer on the touch display
    QTimer.singleShot(50, lambda: splash.setCursor(Qt.BlankCursor))
    
    # Execute the application's main event loop
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()