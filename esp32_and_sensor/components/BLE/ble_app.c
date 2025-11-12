#include "ble_app.h"
#include "esp_log.h"
#include <stdio.h>
#include <string.h>

#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_gatt_common_api.h"
#include "esp_bt_defs.h"

static const char *TAG = "BLE_APP";

// GATT variables
static uint16_t gatt_service_handle = 0;
static uint16_t char_handle = 0;
static esp_gatt_if_t gatts_if_global = 0;
static uint16_t conn_id_global = 0;
static bool device_connected = false;

// Advertising parameters
static esp_ble_adv_params_t adv_params = {
    .adv_int_min        = 0x20,
    .adv_int_max        = 0x40,
    .adv_type           = ADV_TYPE_IND,
    .own_addr_type      = BLE_ADDR_TYPE_PUBLIC,
    .channel_map        = ADV_CHNL_ALL,
    .adv_filter_policy  = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

// Forward declarations
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param);
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if,
                                esp_ble_gatts_cb_param_t *param);

void ble_app_start(void)
{
    ESP_LOGI(TAG, "Initializing Bluetooth...");

    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    ESP_ERROR_CHECK(esp_bluedroid_init());
    ESP_ERROR_CHECK(esp_bluedroid_enable());

    ESP_ERROR_CHECK(esp_ble_gap_register_callback(gap_event_handler));
    ESP_ERROR_CHECK(esp_ble_gatts_register_callback(gatts_event_handler));
    ESP_ERROR_CHECK(esp_ble_gatts_app_register(0));

    ESP_LOGI(TAG, "BLE initialized");
}

void ble_app_send_data(uint32_t bpm, uint8_t spo2)
{
    if (!device_connected) return;

    char buf[50];
    int len = snprintf(buf, sizeof(buf), "BPM:%lu,SpO2:%d", bpm, spo2);

    esp_ble_gatts_send_indicate(
        gatts_if_global,
        conn_id_global,
        char_handle,
        len,
        (uint8_t*)buf,
        false
    );
}

// GAP event handler
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param)
{
    switch (event) {
        case ESP_GAP_BLE_ADV_DATA_SET_COMPLETE_EVT:
            esp_ble_gap_start_advertising(&adv_params);
            break;
        case ESP_GAP_BLE_ADV_START_COMPLETE_EVT:
            if (param->adv_start_cmpl.status == ESP_BT_STATUS_SUCCESS)
                ESP_LOGI(TAG, "Advertising started");
            else
                ESP_LOGE(TAG, "Advertising start failed");
            break;
        default:
            break;
    }
}

// GATTS event handler
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if,
                                esp_ble_gatts_cb_param_t *param)
{
    switch (event) {
        case ESP_GATTS_REG_EVT:
        {
            gatts_if_global = gatts_if;

            esp_ble_gap_set_device_name(BLE_DEVICE_NAME);

            esp_ble_adv_data_t adv_data = {
                .set_scan_rsp = false,
                .include_name = true,
                .include_txpower = true,
                .appearance = 0x00,
                .manufacturer_len = 0,
                .p_manufacturer_data = NULL,
                .service_uuid_len = 0,
                .p_service_uuid = NULL,
                .flag = (ESP_BLE_ADV_FLAG_GEN_DISC | ESP_BLE_ADV_FLAG_BREDR_NOT_SPT),
            };
            esp_ble_gap_config_adv_data(&adv_data);

            esp_gatt_srvc_id_t service_id = {
                .is_primary = true,
                .id.inst_id = 0x00,
                .id.uuid.len = ESP_UUID_LEN_16,
                .id.uuid.uuid.uuid16 = GATTS_SERVICE_UUID
            };
            esp_ble_gatts_create_service(gatts_if, &service_id, GATTS_NUM_HANDLE);
            break;
        }

        case ESP_GATTS_CREATE_EVT:
        {
            gatt_service_handle = param->create.service_handle;

            esp_ble_gatts_start_service(gatt_service_handle);

            esp_gatt_char_prop_t property = ESP_GATT_CHAR_PROP_BIT_READ |
                                            ESP_GATT_CHAR_PROP_BIT_WRITE |
                                            ESP_GATT_CHAR_PROP_BIT_NOTIFY;

            esp_attr_value_t char_val = {
                .attr_max_len = 50,
                .attr_len = 0,
                .attr_value = NULL,
            };

            esp_bt_uuid_t char_uuid = {
                .len = ESP_UUID_LEN_16,
                .uuid.uuid16 = GATTS_CHAR_UUID
            };

            esp_ble_gatts_add_char(gatt_service_handle,
                                   &char_uuid,
                                   ESP_GATT_PERM_READ | ESP_GATT_PERM_WRITE,
                                   property,
                                   &char_val,
                                   NULL);
            break;
        }

        case ESP_GATTS_ADD_CHAR_EVT:
        {
            char_handle = param->add_char.attr_handle;
            ESP_LOGI(TAG, "Characteristic handle saved: %d", char_handle);

            // Dodanie Client Characteristic Configuration Descriptor (CCCD)
            esp_bt_uuid_t descr_uuid = {
                .len = ESP_UUID_LEN_16,
                .uuid.uuid16 = ESP_GATT_UUID_CHAR_CLIENT_CONFIG,
            };

            esp_attr_value_t descr_val = {
                .attr_max_len = 2,
                .attr_len = 2,
                .attr_value = (uint8_t[]){0x00, 0x00},
            };

            esp_ble_gatts_add_char_descr(gatt_service_handle,
                                         &descr_uuid,
                                         ESP_GATT_PERM_READ | ESP_GATT_PERM_WRITE,
                                         &descr_val,
                                         NULL);
            break;
        }

        case ESP_GATTS_CONNECT_EVT:
            conn_id_global = param->connect.conn_id;
            device_connected = true;
            ESP_LOGI(TAG, "Device connected");
            break;

        case ESP_GATTS_DISCONNECT_EVT:
            device_connected = false;
            ESP_LOGI(TAG, "Device disconnected, restarting advertising");
            esp_ble_gap_start_advertising(&adv_params);
            break;

        default:
            break;
    }
}
 