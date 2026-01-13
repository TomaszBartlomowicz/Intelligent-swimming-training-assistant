/**
 * @file ble_app.h
 * @brief Configuration and function prototypes for the NimBLE application
 */

#ifndef BLE_APP_H_
#define BLE_APP_H_

#include <stdint.h>
#include <stdbool.h>

/* --- BLE Device Configuration --- */
#define BLE_DEVICE_NAME       "ESP32CE_BLE"    /**< Name of the device visible during scanning */
#define GATTS_SERVICE_UUID    0x00FF           /**< 16-bit Custom Service UUID */
#define GATTS_CHAR_UUID       0xFF01           /**< 16-bit Custom Characteristic UUID */

/**
 * @brief Initializes the NimBLE stack and starts advertising
 * This sets up the GATT server, GAP events, and FreeRTOS host task.
 */
void ble_app_start(void);

/**
 * @brief Formats and transmits sensor and battery data via BLE notification
 * * @param bpm Heart rate in beats per minute
 * @param spo2 Blood oxygen saturation level (0-100)
 * @param battery_percentage Battery capacity remaining (0-100)
 * @param batter_voltage Measured battery voltage in Volts
 */
void ble_app_send_data(uint32_t bpm, uint8_t spo2, uint32_t battery_percentage, float batter_voltage);

#endif /* BLE_APP_H_ */


