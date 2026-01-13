# get_parameters.py
import asyncio
import threading
from bleak import BleakClient, BleakScanner

# Identyfikatory BLE
CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
BLE_NAME = "ESP32_BLE_Device"

# Globalne dane
latest_values = {"bpm": None, "spo2": None}
ble_connected = False
stop_ble_event = threading.Event()


def ble_notification_handler(sender, data):
    """Obsługuje przychodzące dane z ESP32"""
    global latest_values
    try:
        text = data.decode("utf-8", errors="ignore").strip()
        parts = text.split(",")
        bpm = int(parts[0].split(":")[1])
        spo2 = int(parts[1].split(":")[1])
        latest_values["bpm"] = bpm
        latest_values["spo2"] = spo2
    except Exception as e:
        print(f"[BLE] Error parsing data: {e} | Raw: {data}")


async def _ble_task():
    """Asynchroniczne zadanie obsługujące połączenie BLE"""
    global ble_connected

    while not stop_ble_event.is_set():
        try:
            devices = await BleakScanner.discover(timeout=5.0)
            esp_device = next((d for d in devices if d.name and BLE_NAME in d.name), None)

            if not esp_device:
                print("[BLE] ESP32 not found. Retrying...")
                await asyncio.sleep(5)
                continue

            async with BleakClient(esp_device.address) as client:
                if client.is_connected:
                    ble_connected = True
                    print("[BLE] Connected to ESP32.")
                    await client.start_notify(CHAR_UUID, ble_notification_handler)

                    while not stop_ble_event.is_set() and client.is_connected:
                        await asyncio.sleep(1)

                    print("[BLE] Disconnecting...")
                    ble_connected = False
                else:
                    print("[BLE] Connection failed. Retrying...")
                    await asyncio.sleep(5)

        except Exception as e:
            print(f"[BLE] Error: {e}")
            ble_connected = False
            await asyncio.sleep(5)


def start_ble():
    """Uruchamia połączenie BLE w osobnym wątku"""
    global stop_ble_event
    if not is_connected():
        stop_ble_event.clear()
        threading.Thread(target=lambda: asyncio.run(_ble_task()), daemon=True).start()
        print("[BLE] Starting BLE connection...")


def stop_ble():
    """Zatrzymuje połączenie BLE"""
    global stop_ble_event, ble_connected
    stop_ble_event.set()
    ble_connected = False
    print("[BLE] Stopping BLE connection...")


def is_connected():
    """Zwraca True, jeśli BLE jest połączone"""
    return ble_connected


def reading_parameters():
    """Zwraca ostatnie wartości BPM i SpO₂ jako krotkę (bpm, spo2)"""
    if latest_values["bpm"] is not None:
        return latest_values["bpm"], latest_values["spo2"]
    return None
  