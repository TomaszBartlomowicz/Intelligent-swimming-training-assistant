/**
 * @file ble_app.c
 * @brief Bluetooth Low Energy (BLE) application logic using NimBLE stack
 */

#include "ble_app.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_gap.h"
#include "host/ble_gatt.h"
#include "esp_nimble_hci.h"
#include <string.h>
#include <stdlib.h>

#define TAG "BLE_APP"

/* Forward declaration for advertising function */
static void ble_advertise(void);

/* --- BLE State Variables --- */
static uint8_t gatt_char_val[64];               /**< Buffer for characteristic value */
static uint16_t gatt_char_handle;               /**< Handle for the GATTS characteristic */
static uint16_t conn_handle = BLE_HS_CONN_HANDLE_NONE; /**< Active connection handle */

/* --- External Linkage (Main Application Functions) --- */
extern void ble_connection_status(bool connected);
extern void start_pace_timer(int seconds);

/**
 * @brief GATT access callback for write operations
 * Triggered when a client (e.g., Raspberry Pi) writes a value to the characteristic.
 */
static int gatt_write_cb(uint16_t conn_handle, uint16_t attr_handle,
                         struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    char buffer[16];
    uint16_t len = ctxt->om->om_len;
    
    /* Clamp length to prevent buffer overflow */
    if (len >= sizeof(buffer)) len = sizeof(buffer) - 1;

    /* Copy data from mbuf to flat buffer */
    ble_hs_mbuf_to_flat(ctxt->om, buffer, len, NULL);
    buffer[len] = '\0';

    /* Convert received string to integer */
    int seconds = atoi(buffer);
    ESP_LOGI(TAG, "Timer value received: %d s", seconds);

    /* Update the system pace timer */
    start_pace_timer(seconds);

    return 0;
}

/* --- GATT Service Definition --- */
static const struct ble_gatt_svc_def gatt_svcs[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = BLE_UUID16_DECLARE(GATTS_SERVICE_UUID),
        .characteristics = (struct ble_gatt_chr_def[]) {
            {
                .uuid = BLE_UUID16_DECLARE(GATTS_CHAR_UUID),
                .access_cb = gatt_write_cb,
                .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_NOTIFY,
                .val_handle = &gatt_char_handle,
            },
            {0} /* Mark end of characteristics */
        }
    },
    {0} /* Mark end of services */
};

/**
 * @brief GAP Event Callback
 * Handles connection, disconnection, and advertising events.
 */
static int ble_gap_event_cb(struct ble_gap_event *event, void *arg)
{
    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status == 0) {
            conn_handle = event->connect.conn_handle;
            ESP_LOGI(TAG, "Connection established!");
            ble_connection_status(true);
        } else {
            /* If connection failed, resume advertising */
            ble_advertise();
        }
        break;

    case BLE_GAP_EVENT_DISCONNECT:
        ESP_LOGI(TAG, "Disconnected! Reason: %d", event->disconnect.reason);
        conn_handle = BLE_HS_CONN_HANDLE_NONE;
        ble_connection_status(false);
        
        /* Resume advertising to allow reconnection */
        ble_advertise();
        break;

    case BLE_GAP_EVENT_ADV_COMPLETE:
        ble_advertise();
        break;
    }
    return 0;
}

/**
 * @brief Configures and starts BLE advertising
 */
static void ble_advertise(void)
{
    struct ble_gap_adv_params adv_params = {0};
    adv_params.conn_mode = BLE_GAP_CONN_MODE_UND; /* Undirected connectable */
    adv_params.disc_mode = BLE_GAP_DISC_MODE_GEN; /* General discoverable */

    /* Set stable advertising interval (~100ms) */
    adv_params.itvl_min = 0x00A0; 
    adv_params.itvl_max = 0x00A0;

    struct ble_hs_adv_fields fields = {0};
    
    /* Set advertising flags (Required for compatibility with most BLE scanners) */
    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    
    /* Set device name in advertising packet */
    fields.name = (uint8_t *)BLE_DEVICE_NAME;
    fields.name_len = strlen(BLE_DEVICE_NAME);
    fields.name_is_complete = 1;

    int rc;
    rc = ble_gap_adv_set_fields(&fields);
    if (rc != 0) {
        ESP_LOGE(TAG, "Error setting adv fields; rc=%d", rc);
        return;
    }

    /* Start advertising indefinitely */
    rc = ble_gap_adv_start(BLE_OWN_ADDR_PUBLIC, NULL, BLE_HS_FOREVER,
                           &adv_params, ble_gap_event_cb, NULL);
    if (rc != 0) {
        ESP_LOGE(TAG, "Error starting advertising; rc=%d", rc);
    }
}

/**
 * @brief Callback triggered when NimBLE stack is synchronized
 */
static void ble_on_sync(void)
{
    uint8_t addr_type;
    ble_hs_id_infer_auto(0, &addr_type);
    ble_advertise();
}

/**
 * @brief FreeRTOS task for NimBLE host stack
 */
static void ble_app_host_task(void *param)
{
    nimble_port_run();
    nimble_port_freertos_deinit();
}

/**
 * @brief Initializes and starts the BLE application
 */
void ble_app_start(void)
{
    nimble_port_init();
    
    /* Configure NimBLE stack */
    ble_hs_cfg.sync_cb = ble_on_sync;
    
    /* Register GATT services */
    ble_gatts_count_cfg(gatt_svcs);
    ble_gatts_add_svcs(gatt_svcs);
    
    /* Start the host task in FreeRTOS */
    nimble_port_freertos_init(ble_app_host_task);
}

/**
 * @brief Formats and sends sensor data via BLE Notification
 * @param bpm Heart Rate in Beats Per Minute
 * @param spo2 Oxygen Saturation percentage
 * @param battery_percentage Battery level (0-100)
 * @param batter_voltage Battery voltage in Volts
 */
void ble_app_send_data(uint32_t bpm, uint8_t spo2, uint32_t battery_percentage, float batter_voltage)
{
    if (conn_handle == BLE_HS_CONN_HANDLE_NONE) return;

    /* Format data as a comma-separated string */
    snprintf((char *)gatt_char_val, sizeof(gatt_char_val), "%lu,%u,%lu,%.2f",
             bpm, spo2, battery_percentage, batter_voltage);

    /* Allocate mbuf for GATT notification */
    struct os_mbuf *om = ble_hs_mbuf_from_flat(gatt_char_val, strlen((char *)gatt_char_val));
    
    /* Push notification to the connected client */
    ble_gattc_notify_custom(conn_handle, gatt_char_handle, om);
}