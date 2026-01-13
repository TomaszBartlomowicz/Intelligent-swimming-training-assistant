/**
 * @file SEN0344.c
 * @brief Driver implementation for DFRobot SEN0344 (MAX30102) Heart Rate and SpO2 sensor
 */

#include "SEN0344.h"
#include "esp_log.h"
#include <string.h>

#define TAG "SEN0344"

/**
 * @brief Internal helper to write data to a specific sensor register over I2C
 * @param port I2C port number
 * @param reg Register address to write to
 * @param data Pointer to the data buffer
 * @param len Number of bytes to write
 * @return esp_err_t ESP_OK on success
 */
static esp_err_t i2c_write(i2c_port_t port, uint8_t reg, const uint8_t *data, size_t len) {
    uint8_t buffer[16];
    buffer[0] = reg;
    
    if (len > 15) return ESP_ERR_INVALID_ARG;
    
    memcpy(&buffer[1], data, len);
    return i2c_master_write_to_device(port, SEN0344_I2C_ADDR, buffer, len + 1, pdMS_TO_TICKS(100));
}

/**
 * @brief Internal helper to read data from a specific sensor register over I2C
 * @param port I2C port number
 * @param reg Register address to read from
 * @param data Pointer to the destination buffer
 * @param len Number of bytes to read
 * @return esp_err_t ESP_OK on success
 */
static esp_err_t i2c_read(i2c_port_t port, uint8_t reg, uint8_t *data, size_t len) {
    return i2c_master_write_read_device(port, SEN0344_I2C_ADDR, &reg, 1, data, len, pdMS_TO_TICKS(100));
}

/**
 * @brief Initializes the SEN0344 sensor and checks connection
 * @param i2c_port I2C port number
 * @return esp_err_t ESP_OK if sensor is detected
 */
esp_err_t SEN0344_init(i2c_port_t i2c_port) {
    /* Connectivity check: Read a dummy register to verify device presence */
    uint8_t dummy;
    esp_err_t err = i2c_read(i2c_port, 0x04, &dummy, 1);
    
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Sensor not responding - check wiring and I2C address");
        return err;
    }
    
    return ESP_OK;
}

/**
 * @brief Sends the start command to the sensor to begin sampling
 * @param i2c_port I2C port number
 * @return esp_err_t ESP_OK on success
 */
esp_err_t SEN0344_start_measurement(i2c_port_t i2c_port) {
    /* 0x20 is the command register to trigger measurement start */
    uint8_t data[2] = {0x00, 0x01};
    return i2c_write(i2c_port, 0x20, data, 2);
}

/**
 * @brief Reads the latest Heart Rate, SpO2 and Temperature data from the sensor
 * @param i2c_port I2C port number
 * @param out Pointer to the data structure where results will be stored
 * @return esp_err_t ESP_OK on success
 */
esp_err_t SEN0344_read_data(i2c_port_t i2c_port, SEN0344_data_t *out) {
    uint8_t buffer[8];
    
    /* Read primary data buffer starting from register 0x0C */
    esp_err_t err = i2c_read(i2c_port, 0x0C, buffer, 8);
    if (err != ESP_OK) return err;

    /* Parse SpO2 and BPM (BPM is sent as a 32-bit big-endian value) */
    out->spo2 = buffer[0];
    out->bpm = ((uint32_t)buffer[2] << 24) | 
               ((uint32_t)buffer[3] << 16) | 
               ((uint32_t)buffer[4] << 8)  | 
               buffer[5];

    /* Validation: mark invalid or zero readings with error codes */
    if (out->spo2 == 0) out->spo2 = 255;          // 255 indicates invalid SpO2
    if (out->bpm == 0)  out->bpm = 0xFFFFFFFF;    // Max uint32 indicates invalid BPM

    /* Read temperature data from register 0x14 */
    uint8_t temp_buf[2];
    err = i2c_read(i2c_port, 0x14, temp_buf, 2);
    if (err != ESP_OK) return err;
    
    /* Calculate temperature (Integer part + fractional part) */
    out->temperature = temp_buf[0] + (temp_buf[1] / 100.0f);

    return ESP_OK;
}