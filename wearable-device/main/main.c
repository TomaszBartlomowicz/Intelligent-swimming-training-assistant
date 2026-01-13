#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h" 
#include "nvs_flash.h"
#include "driver/i2c.h"
#include "driver/ledc.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h" 
#include "ble_app.h"
#include "SEN0344.h"
#include "buzzer.h"
#include "esp_timer.h" 

#define TAG "MAIN"

/* --- I2C Configuration --- */
#define I2C_MASTER_NUM      I2C_NUM_0
#define I2C_MASTER_SDA_IO   6
#define I2C_MASTER_SCL_IO   7
#define I2C_MASTER_FREQ_HZ  100000

/* --- ADC Configuration --- */
#define BATTERY_ADC_UNIT    ADC_UNIT_1
#define BATTERY_ADC_CHAN    ADC_CHANNEL_3 
#define VOLTAGE_DIVIDER     5.966f

/* Global ADC handle */
adc_oneshot_unit_handle_t adc1_handle;

/** * @brief Structure for storing processed battery data 
 */
typedef struct {
    uint32_t percentage;
    float voltage;
} Battery_level_t;

Battery_level_t battery;

/* Global handle for the pace marking timer */
TimerHandle_t xPaceTimer = NULL;           

/**
 * @brief System timer callback for pace marking
 * @param xTimer Handle to the timer that triggered the callback
 */
void vPaceTimerCallback(TimerHandle_t xTimer) {
    play_pace_mark_sound(); 
}

/**
 * @brief Sets the interval and starts the periodic pace timer
 * @param seconds Interval in seconds. If 0, the timer is stopped.
 */
void start_pace_timer(int seconds) {
    if (xPaceTimer == NULL) return;
    
    if (seconds <= 0) {
        /* Stop the timer if interval is non-positive */
        xTimerStop(xPaceTimer, 0);
        ESP_LOGI(TAG, "Timer stopped (time=0)");
        return;
    }

    /* Convert input seconds to FreeRTOS ticks */
    TickType_t ticks = pdMS_TO_TICKS(seconds * 1000);
    
    /* Changing the period automatically starts the timer */
    if (xTimerChangePeriod(xPaceTimer, ticks, 0) == pdPASS) {
        ESP_LOGI(TAG, "Timer set to %d s and started.", seconds);
    }
}

/**
 * @brief Stops the pace timer manually
 */
void stop_pace_timer() {
    if (xPaceTimer != NULL) {
        xTimerStop(xPaceTimer, 0);
        ESP_LOGI(TAG, "Timer stopped manually.");
    }
}

/* --- BLE State Management --- */
static volatile bool ble_ready = false;
static uint64_t disconnect_time = 0;

/**
 * @brief BLE connection status callback
 * @param connected Current connection state
 */
void ble_connection_status(bool connected)
{
    ble_ready = connected;
    
    if (connected) {
        /* RECONNECTED STATE */
        if (disconnect_time > 0) {
            /* esp_timer_get_time() returns time in microseconds (us) */
            uint64_t current_time = esp_timer_get_time();
            uint64_t duration_ms = (current_time - disconnect_time) / 1000;
            
            ESP_LOGW(TAG, "!!! RECONNECTED !!! Disconnection duration: %llu ms", duration_ms);
            
            /* Reset disconnection timestamp */
            disconnect_time = 0;
        } else {
            ESP_LOGI(TAG, "BLE Connected (initial or after reset)");
        }
        
        play_bluetooth_connected_sound();
    } 
    else {
        /* DISCONNECTED STATE */
        disconnect_time = esp_timer_get_time(); 
        
        ESP_LOGE(TAG, "BLE Disconnected! Measuring downtime...");
        play_bluetooth_disconnected_sound();
        stop_pace_timer(); 
    }
}

/**
 * @brief Initializes the I2C Master peripheral
 */
static void i2c_master_init(void)
{
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ
    };
    i2c_param_config(I2C_MASTER_NUM, &conf);
    i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

/**
 * @brief Initializes the ADC for battery voltage measurement
 */
static void battery_adc_init(void)
{
    adc_oneshot_unit_init_cfg_t init_config = { .unit_id = BATTERY_ADC_UNIT };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config, &adc1_handle));

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten    = ADC_ATTEN_DB_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, BATTERY_ADC_CHAN, &config));
}

/**
 * @brief Main Application Entry Point
 */
void app_main(void)
{
    /* Initialize Non-Volatile Storage */
    ESP_ERROR_CHECK(nvs_flash_init());

    /* Initialize Peripherals */
    i2c_master_init();
    buzzer_init();
    battery_adc_init(); 

    /* Initialize SEN0344 Pulse Oximeter Sensor */
    if (SEN0344_init(I2C_MASTER_NUM) != ESP_OK) {
        ESP_LOGE(TAG, "SEN0344 initialization error");
    } else {
        SEN0344_start_measurement(I2C_MASTER_NUM);
    }
    
    /* Create the software timer for pace marking */
    xPaceTimer = xTimerCreate("PaceTimer", pdMS_TO_TICKS(1000), pdTRUE, (void *)0, vPaceTimerCallback);

    /* Start system services */
    play_power_on_sound();
    ble_app_start();
    
    /* --- Main Execution Loop --- */
    while (1) {
        /* 1. Read and Process Battery Level */
        int adc_raw = 0;
        if (adc_oneshot_read(adc1_handle, BATTERY_ADC_CHAN, &adc_raw) == ESP_OK) {
            float voltage = (adc_raw / 4095.0f) * VOLTAGE_DIVIDER;
            int percentage = (int)((voltage - 3.3f) / (4.2f - 3.3f) * 100);
            
            /* Bound checking for percentage */
            if (percentage > 100) percentage = 100;
            if (percentage < 0)   percentage = 0;

            battery.voltage = voltage;
            battery.percentage = percentage;
        }

        /* 2. Read Sensor Data and Transmit via BLE */
        SEN0344_data_t sensor_data;
        if (SEN0344_read_data(I2C_MASTER_NUM, &sensor_data) == ESP_OK) {
            if (ble_ready) {
                ble_app_send_data(sensor_data.bpm, 
                                  sensor_data.spo2, 
                                  battery.percentage, 
                                  battery.voltage);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}