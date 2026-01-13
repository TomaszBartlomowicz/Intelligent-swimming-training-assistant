idf_component_register(
    SRCS "ble_app.c"
    INCLUDE_DIRS "."
    REQUIRES nvs_flash bt 
)
