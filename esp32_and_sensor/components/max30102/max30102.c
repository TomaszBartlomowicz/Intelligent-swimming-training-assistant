// max30102.c
#include "max30102.h"
#include "esp_log.h"
#include <string.h>
#include "esp_log.h"

#define TAG "MAX30102"

static esp_err_t i2c_write(i2c_port_t port, uint8_t reg, const uint8_t *data, size_t len) {
    uint8_t buffer[16];
    buffer[0] = reg;
    if (len > 15) return ESP_ERR_INVALID_ARG;
    memcpy(&buffer[1], data, len);
    return i2c_master_write_to_device(port, MAX30102_I2C_ADDR, buffer, len + 1, pdMS_TO_TICKS(100));
}

static esp_err_t i2c_read(i2c_port_t port, uint8_t reg, uint8_t *data, size_t len) {
    return i2c_master_write_read_device(port, MAX30102_I2C_ADDR, &reg, 1, data, len, pdMS_TO_TICKS(100));
}

esp_err_t max30102_init(i2c_port_t i2c_port) {
    // Check device is connected
    uint8_t dummy;
    esp_err_t err = i2c_read(i2c_port, 0x04, &dummy, 1);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Sensor not responding");
        return err;
    }
    return ESP_OK;
}

esp_err_t max30102_start_measurement(i2c_port_t i2c_port) {
    uint8_t data[2] = {0x00, 0x01};
    return i2c_write(i2c_port, 0x20, data, 2); // 0x20 = start command
}

esp_err_t max30102_read_data(i2c_port_t i2c_port, max30102_data_t *out) {
    uint8_t buffer[8];
    esp_err_t err = i2c_read(i2c_port, 0x0C, buffer, 8);
    if (err != ESP_OK) return err;

    out->spo2 = buffer[0];
    out->bpm = ((uint32_t)buffer[2] << 24) | ((uint32_t)buffer[3] << 16) | ((uint32_t)buffer[4] << 8) | buffer[5];
    if (out->spo2 == 0) out->spo2 = 255; // mark invalid as 255
    if (out->bpm == 0) out->bpm = 0xFFFFFFFF; // mark invalid as max

    uint8_t temp_buf[2];
    err = i2c_read(i2c_port, 0x14, temp_buf, 2);
    if (err != ESP_OK) return err;
    out->temperature = temp_buf[0] + temp_buf[1] / 100.0f;

    return ESP_OK;
}
