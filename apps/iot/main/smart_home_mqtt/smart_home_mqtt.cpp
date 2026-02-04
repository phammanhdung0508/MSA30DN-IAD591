#include <string.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/ringbuf.h"
#include "freertos/task.h"

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "mqtt_client.h"
#include "nvs_flash.h"

#include "driver/gpio.h"
#include "driver/i2s.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"

extern "C" {
#include "esp_afe_sr_iface.h"
#include "esp_afe_sr_models.h"
#include "esp_mn_iface.h"
#include "esp_mn_models.h"
}

static const char *TAG = "smart_home_mqtt";

static const char *WIFI_SSID = "FSB-202";
static const char *WIFI_PASS = "123@123a";

static const char *MQTT_BROKER = "mqtt://broker.hivemq.com";
static const char *MQTT_TOPIC = "sensor/temp_humid_msa_assign1";
static const char *MQTT_CONTROL_TOPIC = "sensor/control_msa_assign1";
static const char *MQTT_WAKE_TOPIC = "sensor/wake_trigger_msa_assign1";

#define AUDIO_SOURCE_UDP 1
#define AUDIO_SOURCE_I2S 0
#define UDP_AUDIO_PORT 3333
#define UDP_RINGBUF_SIZE (32 * 1024)

#define DHTPIN 4
#define MQ_PIN 16
#define SDA_PIN 8
#define SCL_PIN 9
#define LED_PIN 2
#define BUZZER_PIN 18
#define MICROPHONE_SD_PIN 15
#define MICROPHONE_SCK_PIN 7
#define MICROPHONE_WS_PIN 6
#define I2S_PORT I2S_NUM_0

#define TEMP_THRESHOLD 20

static EventGroupHandle_t wifi_event_group;
static const int WIFI_CONNECTED_BIT = BIT0;

static esp_mqtt_client_handle_t mqtt_client = NULL;
static bool alarmEnabled = true;

static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t *afe_data = NULL;
static RingbufHandle_t audio_ringbuf = NULL;
static volatile int64_t last_udp_us = 0;
static volatile bool remote_wake_pending = false;

static void setup_i2s(void) {
    const i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    const i2s_pin_config_t pin_config = {
        .bck_io_num = MICROPHONE_SCK_PIN,
        .ws_io_num = MICROPHONE_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = MICROPHONE_SD_PIN
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
}

static void trigger_wake_event(const char *source) {
    if (mqtt_client) {
        char payload[96];
        snprintf(payload, sizeof(payload), "{\"event\":\"wake_word_detected\",\"source\":\"%s\"}", source);
        esp_mqtt_client_publish(mqtt_client, MQTT_TOPIC, payload, 0, 0, 0);
    }
    gpio_set_level((gpio_num_t)LED_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(200));
    gpio_set_level((gpio_num_t)LED_PIN, 0);
}

static void wifi_event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        esp_wifi_connect();
        xEventGroupClearBits(wifi_event_group, WIFI_CONNECTED_BIT);
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        xEventGroupSetBits(wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

static void wifi_init_sta(void) {
    wifi_event_group = xEventGroupCreate();
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, &instance_any_id);
    esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL, &instance_got_ip);

    wifi_config_t wifi_config = {};
    strncpy((char *)wifi_config.sta.ssid, WIFI_SSID, sizeof(wifi_config.sta.ssid));
    strncpy((char *)wifi_config.sta.password, WIFI_PASS, sizeof(wifi_config.sta.password));
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    esp_wifi_start();

    xEventGroupWaitBits(wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdFALSE, portMAX_DELAY);
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data) {
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;
    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            esp_mqtt_client_subscribe(mqtt_client, MQTT_CONTROL_TOPIC, 0);
            esp_mqtt_client_subscribe(mqtt_client, MQTT_WAKE_TOPIC, 0);
            break;
        case MQTT_EVENT_DATA:
            if (event->topic_len && event->data_len) {
                if (strncmp(event->topic, MQTT_CONTROL_TOPIC, event->topic_len) == 0) {
                    if (strncmp(event->data, "ALARM_ON", event->data_len) == 0) {
                        alarmEnabled = true;
                    } else if (strncmp(event->data, "ALARM_OFF", event->data_len) == 0) {
                        alarmEnabled = false;
                        gpio_set_level((gpio_num_t)LED_PIN, 0);
                        gpio_set_level((gpio_num_t)BUZZER_PIN, 0);
                    }
                } else if (strncmp(event->topic, MQTT_WAKE_TOPIC, event->topic_len) == 0) {
                    remote_wake_pending = true;
                }
            }
            break;
        default:
            break;
    }
}

static void mqtt_start(void) {
    esp_mqtt_client_config_t mqtt_cfg = {};
    mqtt_cfg.broker.address.uri = MQTT_BROKER;

    mqtt_client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(mqtt_client, MQTT_EVENT_ANY, mqtt_event_handler, NULL);
    esp_mqtt_client_start(mqtt_client);
}

static void esp_sr_init(void) {
    srmodel_list_t *models = esp_srmodel_init("model");
    if (models) {
        afe_config_t *afe_config = afe_config_init("M", models, AFE_TYPE_SR, AFE_MODE_LOW_COST);
        if (afe_config) {
            afe_config->vad_init = true;
            afe_config->wakenet_init = true;
            afe_handle = (esp_afe_sr_iface_t *)esp_afe_handle_from_config(afe_config);
            afe_data = afe_handle->create_from_config(afe_config);
            ESP_LOGI(TAG, "ESP-SR initialized");
        }
    } else {
        ESP_LOGW(TAG, "ESP-SR models not found (flash srmodels.bin)");
    }
}

static void udp_audio_task(void *pvParameters) {
#if AUDIO_SOURCE_UDP
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "UDP socket create failed");
        vTaskDelete(NULL);
        return;
    }

    struct sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(UDP_AUDIO_PORT);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        ESP_LOGE(TAG, "UDP bind failed");
        close(sock);
        vTaskDelete(NULL);
        return;
    }

    uint8_t rx_buf[1024];
    while (true) {
        int len = recvfrom(sock, rx_buf, sizeof(rx_buf), 0, NULL, NULL);
        if (len > 0 && audio_ringbuf) {
            last_udp_us = esp_timer_get_time();
            if (xRingbufferSend(audio_ringbuf, rx_buf, len, 0) != pdTRUE) {
                size_t old_size = 0;
                void *old_item = xRingbufferReceive(audio_ringbuf, &old_size, 0);
                if (old_item) {
                    vRingbufferReturnItem(audio_ringbuf, old_item);
                }
                xRingbufferSend(audio_ringbuf, rx_buf, len, 0);
            }
        }
    }
#else
    vTaskDelete(NULL);
#endif
}

static void audio_feed_task(void *pvParameters) {
    while (!afe_handle || !afe_data) {
        vTaskDelay(pdMS_TO_TICKS(200));
    }

    int feed_chunksize = afe_handle->get_feed_chunksize(afe_data);
    int16_t *feed_buff = (int16_t *)malloc(feed_chunksize * sizeof(int16_t));
    if (!feed_buff) {
        ESP_LOGE(TAG, "Audio buffer alloc failed");
        vTaskDelete(NULL);
        return;
    }

    const int64_t udp_timeout_us = 500000;
    while (true) {
        bool use_udp = false;
#if AUDIO_SOURCE_UDP
        int64_t now_us = esp_timer_get_time();
        use_udp = (now_us - last_udp_us) < udp_timeout_us;
#endif

        size_t bytesRead = 0;
#if AUDIO_SOURCE_I2S
        if (!use_udp) {
            i2s_read(I2S_PORT, feed_buff, feed_chunksize * sizeof(int16_t), &bytesRead, portMAX_DELAY);
        }
#endif

#if AUDIO_SOURCE_UDP
        if (use_udp && audio_ringbuf) {
            size_t item_size = 0;
            void *item = xRingbufferReceiveUpTo(audio_ringbuf, &item_size,
                                                pdMS_TO_TICKS(50),
                                                feed_chunksize * sizeof(int16_t));
            if (item && item_size > 0) {
                size_t copy_size = item_size > (size_t)(feed_chunksize * sizeof(int16_t))
                                       ? (size_t)(feed_chunksize * sizeof(int16_t))
                                       : item_size;
                memcpy(feed_buff, item, copy_size);
                if (copy_size < (size_t)(feed_chunksize * sizeof(int16_t))) {
                    memset(((uint8_t *)feed_buff) + copy_size, 0,
                           feed_chunksize * sizeof(int16_t) - copy_size);
                }
                bytesRead = feed_chunksize * sizeof(int16_t);
                vRingbufferReturnItem(audio_ringbuf, item);
            } else {
                memset(feed_buff, 0, feed_chunksize * sizeof(int16_t));
                bytesRead = feed_chunksize * sizeof(int16_t);
            }
        }
#endif

        if (bytesRead > 0) {
            afe_handle->feed(afe_data, feed_buff);
            afe_fetch_result_t *res = afe_handle->fetch(afe_data);
            if (res && res->wakeup_state == WAKENET_DETECTED) {
                trigger_wake_event("ondevice");
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(10));
        }
    }
}

static void app_task(void *pvParameters) {
    gpio_set_direction((gpio_num_t)LED_PIN, GPIO_MODE_OUTPUT);
    gpio_set_direction((gpio_num_t)BUZZER_PIN, GPIO_MODE_OUTPUT);
    gpio_set_direction((gpio_num_t)MQ_PIN, GPIO_MODE_INPUT);

#if AUDIO_SOURCE_I2S
    setup_i2s();
#endif

    esp_sr_init();
    mqtt_start();

#if AUDIO_SOURCE_UDP
    audio_ringbuf = xRingbufferCreate(UDP_RINGBUF_SIZE, RINGBUF_TYPE_BYTEBUF);
    xTaskCreate(udp_audio_task, "udp_audio_task", 4096, NULL, 5, NULL);
#endif
    xTaskCreate(audio_feed_task, "audio_feed_task", 4096, NULL, 5, NULL);

    while (true) {
        float humidity = 0.0f;
        float temperature = 0.0f;
        int gasValue = 0;
        float noiseLevel = 0;

        if (remote_wake_pending) {
            remote_wake_pending = false;
            trigger_wake_event("remote");
        }

        if (temperature > TEMP_THRESHOLD && alarmEnabled) {
            gpio_set_level((gpio_num_t)LED_PIN, 1);
            gpio_set_level((gpio_num_t)BUZZER_PIN, 1);
        } else {
            gpio_set_level((gpio_num_t)LED_PIN, 0);
            gpio_set_level((gpio_num_t)BUZZER_PIN, 0);
        }

        char payload[128];
        snprintf(payload, sizeof(payload),
                 "{\"temperature\":%.2f,\"humidity\":%.2f,\"gas\":%d,\"noise\":%.2f}",
                 temperature, humidity, gasValue, noiseLevel);
        esp_mqtt_client_publish(mqtt_client, MQTT_TOPIC, payload, 0, 0, 0);

        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}

extern "C" void app_main(void) {
    nvs_flash_init();
    wifi_init_sta();
    xTaskCreate(app_task, "app_task", 8192, NULL, 5, NULL);
}
