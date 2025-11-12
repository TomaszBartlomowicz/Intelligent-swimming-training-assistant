#ifndef __MAX30102_H__
#define __MAX30102_H__

#include "driver/i2c.h"
#include "esp_err.h"
#include <string.h>

#define MAX30102_I2C_ADDR 0x57

typedef struct {
    uint8_t spo2;        // Saturation (%)
    uint32_t bpm;        // Heart rate
    float temperature;   // Board temperature (°C)
} max30102_data_t;

/**
 * @brief Check sensor connection
 */
esp_err_t max30102_init(i2c_port_t i2c_port);

/**
 * @brief Start data collection (writes 0x01 to reg 0x20)
 */
esp_err_t max30102_start_measurement(i2c_port_t i2c_port);

/**
 * @brief Read SpO2, heart rate and temperature
 */
esp_err_t max30102_read_data(i2c_port_t i2c_port, max30102_data_t *data);

#endif // __MAX30102_H__
