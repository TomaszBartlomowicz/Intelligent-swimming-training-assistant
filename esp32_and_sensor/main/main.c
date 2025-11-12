#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "driver/i2c.h"
#include "esp_log.h"

#include "ble_app.h"
#include "max30102.h"

#define TAG "MAIN"
#define I2C_MASTER_NUM I2C_NUM_0
#define I2C_MASTER_SDA_IO 21
#define I2C_MASTER_SCL_IO 22
#define I2C_MASTER_FREQ_HZ 100000

static void i2c_master_init(void)
{
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    i2c_param_config(I2C_MASTER_NUM, &conf);

    esp_err_t del_err = i2c_driver_delete(I2C_MASTER_NUM);
    if (del_err != ESP_ERR_INVALID_STATE && del_err != ESP_OK) {
        ESP_LOGW(TAG, "i2c_driver_delete returned %d", del_err);
    }

    esp_err_t inst_err = i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
    if (inst_err != ESP_OK) {
        ESP_LOGE(TAG, "i2c_driver_install failed: %d", inst_err);
    }
}

void app_main(void)
{
    // NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    ESP_LOGI(TAG, "Starting application");

    // Start BLE
    ble_app_start();

    // Init I2C i MAX30102
    i2c_master_init();
    if (max30102_init(I2C_MASTER_NUM) != ESP_OK) {
        ESP_LOGE(TAG, "MAX30102 not found!");
        return;
    }
    max30102_start_measurement(I2C_MASTER_NUM);

    while (1) {
        max30102_data_t data;
        if (max30102_read_data(I2C_MASTER_NUM, &data) == ESP_OK) {
            ESP_LOGI(TAG, "Sensor read -> BPM: %lu, SpO2: %d%%", data.bpm, data.spo2);

            // Send data over BLE
            ble_app_send_data(data.bpm, data.spo2);
        } else {
            ESP_LOGW(TAG, "Failed to read data from MAX30102");
        }

        vTaskDelay(pdMS_TO_TICKS(1000)); // delay 1s
    } 
} 
