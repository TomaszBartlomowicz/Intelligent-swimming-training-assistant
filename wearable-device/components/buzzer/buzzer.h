/**
 * @file buzzer.h
 * @brief Configuration and function prototypes for the buzzer driver
 */

#ifndef BUZZER_H
#define BUZZER_H

#include "driver/ledc.h"

/* --- Buzzer Hardware Configuration --- */
#define BUZZER_PIN          2                   /**< GPIO pin connected to the buzzer */
#define BUZZER_TIMER        LEDC_TIMER_0        /**< LEDC timer peripheral */
#define BUZZER_MODE         LEDC_LOW_SPEED_MODE /**< LEDC speed mode */
#define BUZZER_CHANNEL      LEDC_CHANNEL_0      /**< LEDC channel */
#define BUZZER_RES          LEDC_TIMER_13_BIT   /**< PWM duty resolution (13-bit = 8192 levels) */
#define BUZZER_FREQ         4000                /**< Default PWM frequency in Hz */

/**
 * @brief Initializes the buzzer peripheral (LEDC)
 */
void buzzer_init(void);

/**
 * @brief Plays a tone with a specific frequency and duration
 * * @param freq_hz Frequency in Hertz
 * @param volume Volume level (0-100)
 * @param duration_ms Duration in milliseconds
 */
void buzzer_play_tone(int freq_hz, int volume, int duration_ms);

/**
 * @brief Plays an ascending melody for successful BLE connection
 */
void play_bluetooth_connected_sound(void);

/**
 * @brief Plays a descending melody for BLE disconnection
 */
void play_bluetooth_disconnected_sound(void);

/**
 * @brief Plays a power-on greeting melody
 */
void play_power_on_sound(void);

/**
 * @brief Plays a high-pitched double-beep for pace marking
 */
void play_pace_mark_sound(void);

#endif /* BUZZER_H */