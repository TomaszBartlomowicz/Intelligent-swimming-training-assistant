/**
 * @file buzzer.c
 * @brief Buzzer driver implementation using ESP32 LEDC (PWM) peripheral
 */

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h" 
#include "buzzer.h"

/**
 * @brief Initializes the LEDC peripheral for buzzer control
 * Configures the timer and the specific PWM channel.
 */
void buzzer_init(void)
{
    /* Configure the LEDC PWM timer */
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = BUZZER_MODE,
        .timer_num        = BUZZER_TIMER,
        .duty_resolution  = BUZZER_RES,
        .freq_hz          = BUZZER_FREQ,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&ledc_timer);

    /* Configure the LEDC PWM channel */
    ledc_channel_config_t ledc_channel = {
        .speed_mode     = BUZZER_MODE,
        .channel        = BUZZER_CHANNEL,
        .timer_sel      = BUZZER_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = BUZZER_PIN,
        .duty           = 0,
        .hpoint         = 0
    };
    ledc_channel_config(&ledc_channel);
}

/**
 * @brief Plays a single tone with specified frequency, volume and duration
 * @param freq_hz Frequency in Hertz
 * @param volume Volume percentage (0-100)
 * @param duration_ms Duration of the tone in milliseconds
 */
void buzzer_play_tone(int freq_hz, int volume, int duration_ms)
{
    /* Set the PWM frequency for the desired pitch */
    ledc_set_freq(BUZZER_MODE, BUZZER_TIMER, freq_hz);
    
    /* Calculate duty cycle: Scaling 100% volume to 4096 (mid-point for 13-bit resolution) */
    uint32_t duty = (volume * 4096) / 100;

    /* Start the sound */
    ledc_set_duty(BUZZER_MODE, BUZZER_CHANNEL, duty);
    ledc_update_duty(BUZZER_MODE, BUZZER_CHANNEL);

    /* Hold the tone for the specified duration */
    vTaskDelay(pdMS_TO_TICKS(duration_ms));

    /* Stop the sound (set duty to 0) */
    ledc_set_duty(BUZZER_MODE, BUZZER_CHANNEL, 0);
    ledc_update_duty(BUZZER_MODE, BUZZER_CHANNEL);
}

/**
 * @brief Plays a startup sound sequence (C5-E5-G5 melody)
 */
void play_power_on_sound(void) {
    buzzer_play_tone(523, 100, 60); 
    buzzer_play_tone(659, 100, 60);
    buzzer_play_tone(784, 100, 150); 
}

/**
 * @brief Plays an ascending melody indicating successful BLE connection
 */
void play_bluetooth_connected_sound() {
    buzzer_play_tone(1047, 100, 80);
    vTaskDelay(pdMS_TO_TICKS(20));
    buzzer_play_tone(1319, 100, 80);
    vTaskDelay(pdMS_TO_TICKS(20));
    buzzer_play_tone(1568, 100, 200);
}

/**
 * @brief Plays a descending melody indicating BLE disconnection
 */
void play_bluetooth_disconnected_sound() {
    buzzer_play_tone(784, 100, 80);
    buzzer_play_tone(392, 100, 250); 
}

/**
 * @brief Plays a high-pitched double-beep sound for pace marking
 */
void play_pace_mark_sound() {
    int freq = 2730; 
    
    /* Double beep sequence */
    buzzer_play_tone(freq, 100, 70);
    vTaskDelay(pdMS_TO_TICKS(80));
    buzzer_play_tone(freq, 100, 70);
}