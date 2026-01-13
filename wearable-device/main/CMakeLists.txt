idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES SEN0344 nvs_flash BLE buzzer esp_adc
)