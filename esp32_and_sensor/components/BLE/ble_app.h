#ifndef BLE_APP_H_
#define BLE_APP_H_

#include "esp_err.h"
#include "stdint.h"
#include "stdbool.h"

#define BLE_DEVICE_NAME         "ESP32_BLE_Device"
#define GATTS_SERVICE_UUID      0x00FF
#define GATTS_CHAR_UUID         0xFF01
#define GATTS_NUM_HANDLE        4

void ble_app_start(void);
void ble_app_send_data(uint32_t bpm, uint8_t spo2);

#endif
