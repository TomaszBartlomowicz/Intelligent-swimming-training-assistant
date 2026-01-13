"""
Hardware abstraction layer for the base station buzzer.
Provides asynchronous audio signaling for training events using RPi.GPIO.
"""

import RPi.GPIO as GPIO
import threading
import time

# --- GPIO Configuration ---
BUZZER_PIN = 17

# Initialize GPIO settings
GPIO.setmode(GPIO.BCM)
# Active-low configuration: HIGH = Off, LOW = On
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.HIGH)

def buzzer_on():
    """Activates the buzzer (active-low state)."""
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzzer_off():
    """Deactivates the buzzer."""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_beep(duration: float):
    """
    Generates a non-blocking audio signal for a specified duration.
    
    Args:
        duration (float): Beep duration in seconds.
    """
    buzzer_on()
    # Asynchronous timer to turn off the buzzer without blocking the main thread
    timer = threading.Timer(duration, buzzer_off)
    timer.start()

def buzzer_beep_short():
    """Triggers a short 100ms beep (e.g., for pacer intervals)."""
    buzzer_beep(0.1)

def buzzer_beep_long():
    """Triggers a 1.0s beep (e.g., for start/end signals)."""
    buzzer_beep(1.0)

