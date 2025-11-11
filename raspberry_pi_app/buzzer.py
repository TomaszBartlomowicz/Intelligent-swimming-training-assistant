import RPi.GPIO as GPIO
import threading
import time

# Ustawienia GPIO
BUZZER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.HIGH)  # HIGH = wyłączony

def buzzer_on():
    """Włącza buzzer (aktywny stan niski)."""
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzzer_off():
    """Wyłącza buzzer."""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_beep(duration: float):
    """Generuje sygnał o określonym czasie trwania (sekundy)."""
    buzzer_on()
    timer = threading.Timer(duration, buzzer_off)
    timer.start()

def buzzer_beep_short():
    """Krótki sygnał buzzera (100 ms)."""
    buzzer_beep(0.1)

def buzzer_beep_long():
    """Długi sygnał buzzera (900 ms)."""
    buzzer_beep(1)

# Przykład użycia
if __name__ == "__main__":
    try:
        buzzer_beep_short()
        time.sleep(1)
        buzzer_beep_long()
        input("Naciśnij Enter, aby zakończyć...\n")
    finally:
        GPIO.cleanup()
