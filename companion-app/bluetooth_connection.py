"""
Bluetooth Low Energy (BLE) communication manager.
Handles background connection to the ESP32 wearable device, data parsing, 
and command transmission for the training assistant.
"""

import asyncio
import threading
from bleak import BleakClient, BleakScanner

# --- Global State Management ---
_ble_client = None
_ble_thread = None
_ble_loop = None
_stop_event = None
_ble_connected = False

# --- Hardware Configuration ---
BLE_NAME = "ESP32C3_BLE"
ESP_MAC = "94:A9:90:7C:B1:CE"
CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Shared telemetry data structure
latest_values = {
    "bpm": None,
    "spo2": None,
    "battery": None,
    "voltage": None
}

def ble_notification_handler(sender, data):
    """
    Asynchronous callback for processing incoming GATT notifications.
    Parses CSV-formatted string: 'BPM,SpO2,Battery,Voltage'.
    """
    try:
        text = data.decode("utf-8").strip()
        parts = text.split(",")
        
        if len(parts) >= 4:
            latest_values["bpm"] = int(parts[0])
            latest_values["spo2"] = int(parts[1])
            latest_values["battery"] = int(parts[2])
            latest_values["voltage"] = float(parts[3])
    except Exception as e:
        print(f"[BLE Handler Error] {e}")


async def _ble_task(stop_event):
    """
    Core asyncio task for maintaining the BLE connection lifecycle.
    Implements automatic reconnection and notification subscription.
    """
    global _ble_client, _ble_connected

    while not stop_event.is_set():
        try:
            print(f"Connecting to {ESP_MAC}...")
            client = BleakClient(ESP_MAC)
            await client.connect(timeout=10.0)

            if not client.is_connected:
                await asyncio.sleep(2)
                continue

            _ble_client = client
            _ble_connected = True
            print(f"Connected to {ESP_MAC}")

            # Subscribe to real-time telemetry updates
            await client.start_notify(CHAR_UUID, ble_notification_handler)

            # Keep task alive while connected and stop event not set
            while not stop_event.is_set() and client.is_connected:
                await asyncio.sleep(0.5)

            if client.is_connected:
                await client.disconnect()

            _ble_connected = False
            _ble_client = None
            print("BLE session closed.")

        except Exception as e:
            print(f"[BLE Error] {e}")
            _ble_connected = False
            await asyncio.sleep(2)


def start_ble_in_thread():
    """Spawns a dedicated background thread for the asyncio event loop."""
    global _ble_thread, _ble_loop, _stop_event

    if _ble_thread and _ble_thread.is_alive():
        return

    _stop_event = threading.Event()

    def runner():
        global _ble_loop
        _ble_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_ble_loop)
        try:
            _ble_loop.run_until_complete(_ble_task(_stop_event))
        finally:
            _ble_loop.close()

    _ble_thread = threading.Thread(target=runner, daemon=True)
    _ble_thread.start()
    print("BLE service thread started.")


def disconnect_ble():
    """Signals the BLE thread to terminate and closes active connections safely."""
    global _stop_event, _ble_client, _ble_connected

    if _stop_event:
        _stop_event.set()

    if _ble_client and _ble_client.is_connected:
        try:
            # Safely schedule disconnect in the background event loop
            fut = asyncio.run_coroutine_threadsafe(_ble_client.disconnect(), _ble_loop)
            fut.result(timeout=3)
        except Exception as e:
            print(f"[BLE Disconnect Error] {e}")

    _ble_connected = False
    _ble_client = None


def is_connected():
    """Thread-safe check for current BLE link status."""
    return _ble_connected


def reading_parameters():
    """Returns the latest telemetry dictionary or None if no data received."""
    if latest_values["bpm"] is not None:
        return latest_values
    return None


def send_timer_seconds(seconds: int):
    """
    Transmits an integer value to the ESP32 to set the buzzer interval.
    Utilizes GATT write with response.
    """
    global _ble_client, _ble_loop, _ble_connected

    if not _ble_connected or _ble_client is None:
        print("[BLE Write Error] No active connection.")
        return

    # Convert to UTF-8 string as expected by the ESP32 GATT callback
    data_to_send = str(seconds).encode("utf-8")

    try:
        # Cross-thread communication: injecting coroutine into the BLE thread loop
        future = asyncio.run_coroutine_threadsafe(
            _ble_client.write_gatt_char(CHAR_UUID, data_to_send, response=True), 
            _ble_loop
        )
        future.result(timeout=2) 
        print(f"Buzzer interval set to: {seconds}s")
    except Exception as e:
        print(f"[BLE Write Error] {e}")

if __name__ == "__main__":
    # Test script for standalone verification
    import time
    start_ble_in_thread()
    
    try:
        while True:
            data = reading_parameters()
            if data:
                print(f"Data stream: {data}")
            time.sleep(1)
    except KeyboardInterrupt:
        disconnect_ble()