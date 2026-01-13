#ifndef __SEN0344_H__
#define __SEN0344_H__

#include "driver/i2c.h"
#include "esp_err.h"
#include <string.h>

#define SEN0344_I2C_ADDR 0x57

typedef struct {
    uint8_t spo2;        // Saturation (%)
    uint32_t bpm;        // Heart rate
    float temperature;   // Board temperature (°C)
} SEN0344_data_t;

/**
 * @brief Check sensor connection
 */
esp_err_t SEN0344_init(i2c_port_t i2c_port);

/**
 * @brief Start data collection (writes 0x01 to reg 0x20)
 */
esp_err_t SEN0344_start_measurement(i2c_port_t i2c_port);

/**
 * @brief Read SpO2, heart rate and temperature
 */
esp_err_t SEN0344_read_data(i2c_port_t i2c_port, SEN0344_data_t *data);

#endif  __SEN0344_H__
