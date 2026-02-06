#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "sdkconfig.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_rom_sys.h"
#include "esp_netif_ip_addr.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "nvs_flash.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"
#include "lwip/tcp.h"

extern "C" {
#include "esp_afe_sr_iface.h"
#include "esp_afe_sr_models.h"
#include "esp_mn_iface.h"
#include "esp_mn_models.h"
}

static const char *TAG = "i2s_mic";

static const char *WIFI_SSID = CONFIG_SMART_HOME_WIFI_SSID;
static const char *WIFI_PASS = CONFIG_SMART_HOME_WIFI_PASSWORD;
static const char *AUDIO_UDP_HOST = CONFIG_SMART_HOME_AUDIO_UDP_HOST;
static const int AUDIO_UDP_PORT = CONFIG_SMART_HOME_AUDIO_UDP_PORT;

// INMP411 wiring (from INMP411.c)
static const gpio_num_t I2S_SCK = GPIO_NUM_12; // BCLK
static const gpio_num_t I2S_WS = GPIO_NUM_11;
static const gpio_num_t I2S_SD = GPIO_NUM_10;
#define I2S_PORT I2S_NUM_0

// I2C LCD wiring
static const i2c_port_num_t I2C_PORT = I2C_NUM_0;
static const gpio_num_t I2C_SCL = GPIO_NUM_4;
static const gpio_num_t I2C_SDA = GPIO_NUM_5;
static const uint32_t I2C_CLK_HZ = 100000;
static const gpio_num_t LED_PIN = GPIO_NUM_6;

static const int SAMPLE_RATE = 16000;
static const int SILENCE_TIMEOUT_MS = 2000;
static const int MAX_RECORD_MS = 20000;
static const int LISTENING_ANIM_MS = 500;
static const int ENERGY_THRESHOLD = 250;
static const uint32_t UDP_AUDIO_HEADER = 10;
static const int AUDIO_GAIN_SHIFT = 2; // +12dB (x4)
static const int UDP_AGG_FRAMES = 3;   // aggregate frames to reduce UDP packet rate

static i2s_chan_handle_t rx_handle = NULL;
static int audio_sock = -1;
static struct sockaddr_in audio_target = {};

static EventGroupHandle_t wifi_event_group;
static const int WIFI_CONNECTED_BIT = BIT0;

static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t *afe_data = NULL;

static SemaphoreHandle_t lcd_mutex = NULL;
static bool lcd_ready = false;
static uint8_t lcd_addr = 0x27;
static bool lcd_backlight = true;
static i2c_master_bus_handle_t i2c_bus = NULL;
static i2c_master_dev_handle_t lcd_dev = NULL;

#define LCD_RS 0x01
#define LCD_EN 0x04
#define LCD_BL 0x08

static bool wifi_config_valid(void) {
    return WIFI_SSID && WIFI_PASS && strlen(WIFI_SSID) > 0 && strlen(WIFI_PASS) > 0;
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

static bool wifi_init_sta(void) {
    if (!wifi_config_valid()) {
        ESP_LOGE(TAG, "WiFi credentials not set. Configure SMART_HOME_WIFI_SSID/PASSWORD.");
        return false;
    }

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
    strncpy((char *)wifi_config.sta.ssid, WIFI_SSID, sizeof(wifi_config.sta.ssid) - 1);
    wifi_config.sta.ssid[sizeof(wifi_config.sta.ssid) - 1] = '\0';
    strncpy((char *)wifi_config.sta.password, WIFI_PASS, sizeof(wifi_config.sta.password) - 1);
    wifi_config.sta.password[sizeof(wifi_config.sta.password) - 1] = '\0';
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    esp_wifi_start();

    xEventGroupWaitBits(wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdFALSE, portMAX_DELAY);

    esp_netif_ip_info_t ip_info;
    esp_netif_t *netif = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
    if (netif && esp_netif_get_ip_info(netif, &ip_info) == ESP_OK) {
        ESP_LOGI(TAG, "WiFi IP: " IPSTR, IP2STR(&ip_info.ip));
    }
    return true;
}

static void audio_close_socket(void) {
    if (audio_sock >= 0) {
        shutdown(audio_sock, SHUT_RDWR);
        close(audio_sock);
        audio_sock = -1;
    }
}

static void audio_init(void) {
    if (!AUDIO_UDP_HOST || strlen(AUDIO_UDP_HOST) == 0) {
        ESP_LOGW(TAG, "AUDIO_UDP_HOST not set, TCP audio disabled");
        return;
    }

    audio_target.sin_family = AF_INET;
    audio_target.sin_port = htons(AUDIO_UDP_PORT);
    audio_target.sin_addr.s_addr = inet_addr(AUDIO_UDP_HOST);

    ESP_LOGI(TAG, "TCP audio target: %s:%d", AUDIO_UDP_HOST, AUDIO_UDP_PORT);
}

static bool audio_connect(void) {
    if (audio_sock >= 0) {
        return true;
    }
    audio_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (audio_sock < 0) {
        ESP_LOGE(TAG, "Unable to create TCP socket");
        return false;
    }
    int one = 1;
    setsockopt(audio_sock, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    struct timeval tv = {};
    tv.tv_sec = 2;
    tv.tv_usec = 0;
    setsockopt(audio_sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
    setsockopt(audio_sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    if (connect(audio_sock, (struct sockaddr *)&audio_target, sizeof(audio_target)) != 0) {
        ESP_LOGW(TAG, "TCP connect failed");
        audio_close_socket();
        return false;
    }
    return true;
}

static bool audio_send_packet(const uint8_t *data, size_t len) {
    if (!audio_connect()) {
        return false;
    }
    size_t sent = 0;
    while (sent < len) {
        int r = send(audio_sock, data + sent, len - sent, 0);
        if (r <= 0) {
            ESP_LOGW(TAG, "TCP send failed");
            audio_close_socket();
            return false;
        }
        sent += r;
    }
    return true;
}

static void tcp_send_start(void) {
    static const uint8_t msg[] = {'S', 'T', 'R', 'T'};
    audio_send_packet(msg, sizeof(msg));
}

static void tcp_send_stop(void) {
    static const uint8_t msg[] = {'S', 'T', 'O', 'P'};
    audio_send_packet(msg, sizeof(msg));
}

static bool tcp_send_audio(const int16_t *pcm, uint16_t bytes, uint32_t seq, uint8_t *scratch, size_t scratch_size) {
    if (bytes == 0 || !pcm) {
        return true;
    }
    const size_t packet_size = (size_t)bytes + UDP_AUDIO_HEADER;
    if (!scratch || scratch_size < packet_size) {
        return false;
    }
    scratch[0] = 'A';
    scratch[1] = 'U';
    scratch[2] = 'D';
    scratch[3] = '0';
    scratch[4] = (uint8_t)(seq & 0xff);
    scratch[5] = (uint8_t)((seq >> 8) & 0xff);
    scratch[6] = (uint8_t)((seq >> 16) & 0xff);
    scratch[7] = (uint8_t)((seq >> 24) & 0xff);
    scratch[8] = (uint8_t)(bytes & 0xff);
    scratch[9] = (uint8_t)((bytes >> 8) & 0xff);
    memcpy(&scratch[10], pcm, bytes);
    return audio_send_packet(scratch, packet_size);
}

static esp_err_t i2c_master_init(void) {
    if (i2c_bus) {
        return ESP_OK;
    }

    i2c_master_bus_config_t bus_cfg = {};
    bus_cfg.i2c_port = I2C_PORT;
    bus_cfg.sda_io_num = I2C_SDA;
    bus_cfg.scl_io_num = I2C_SCL;
    bus_cfg.clk_source = I2C_CLK_SRC_DEFAULT;
    bus_cfg.glitch_ignore_cnt = 7;
    bus_cfg.intr_priority = 0;
    bus_cfg.trans_queue_depth = 0;
    bus_cfg.flags.enable_internal_pullup = 1;
    bus_cfg.flags.allow_pd = 0;

    return i2c_new_master_bus(&bus_cfg, &i2c_bus);
}

static bool i2c_probe(uint8_t addr) {
    if (!i2c_bus) {
        return false;
    }
    return i2c_master_probe(i2c_bus, addr, 50) == ESP_OK;
}

static uint8_t lcd_detect_addr(void) {
    for (uint8_t addr = 0x20; addr <= 0x27; addr++) {
        if (i2c_probe(addr)) return addr;
    }
    for (uint8_t addr = 0x38; addr <= 0x3F; addr++) {
        if (i2c_probe(addr)) return addr;
    }
    return 0;
}

static esp_err_t lcd_write_raw(uint8_t data) {
    if (!lcd_dev) {
        return ESP_ERR_INVALID_STATE;
    }
    return i2c_master_transmit(lcd_dev, &data, 1, 50);
}

static void lcd_pulse_enable(uint8_t data) {
    lcd_write_raw(data | LCD_EN);
    esp_rom_delay_us(1);
    lcd_write_raw(data & ~LCD_EN);
    esp_rom_delay_us(50);
}

static void lcd_write4bits(uint8_t value, bool rs) {
    uint8_t data = value & 0xF0;
    if (rs) data |= LCD_RS;
    if (lcd_backlight) data |= LCD_BL;
    lcd_pulse_enable(data);
}

static void lcd_send(uint8_t value, bool rs) {
    lcd_write4bits(value & 0xF0, rs);
    lcd_write4bits((value << 4) & 0xF0, rs);
}

static void lcd_command(uint8_t cmd) {
    lcd_send(cmd, false);
    if (cmd == 0x01 || cmd == 0x02) {
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}

static void lcd_write_char(char c) {
    lcd_send((uint8_t)c, true);
}

static void lcd_set_cursor(uint8_t col, uint8_t row) {
    static const uint8_t row_offsets[] = {0x00, 0x40, 0x14, 0x54};
    if (row > 1) row = 1;
    lcd_command(0x80 | (col + row_offsets[row]));
}

static void lcd_write_line(uint8_t row, const char *text) {
    char buf[17];
    memset(buf, ' ', 16);
    if (text) {
        size_t len = strlen(text);
        if (len > 16) len = 16;
        memcpy(buf, text, len);
    }
    buf[16] = '\0';

    lcd_set_cursor(0, row);
    for (int i = 0; i < 16; i++) {
        lcd_write_char(buf[i]);
    }
}

static void lcd_lock(void) {
    if (lcd_mutex) {
        xSemaphoreTake(lcd_mutex, portMAX_DELAY);
    }
}

static void lcd_unlock(void) {
    if (lcd_mutex) {
        xSemaphoreGive(lcd_mutex);
    }
}

static void lcd_show_status(const char *line1, const char *line2) {
    if (!lcd_ready) return;
    lcd_lock();
    lcd_write_line(0, line1);
    lcd_write_line(1, line2);
    lcd_unlock();
}

static void lcd_show_idle(void) {
    lcd_show_status("WELCOME,", "SAY HI JASON");
}

static void lcd_show_listening(int dots) {
    char buf[17];
    const char *suffix = "...";
    if (dots == 1) suffix = ".";
    if (dots == 2) suffix = "..";
    snprintf(buf, sizeof(buf), "LISTENING%s", suffix);
    lcd_show_status("SAY COMMAND", buf);
}

static void lcd_init(void) {
    lcd_mutex = xSemaphoreCreateMutex();
    if (!lcd_mutex) {
        ESP_LOGW(TAG, "LCD mutex alloc failed");
        return;
    }

    uint8_t addr = lcd_detect_addr();
    if (addr == 0) {
        ESP_LOGW(TAG, "LCD I2C device not found");
        return;
    }
    lcd_addr = addr;

    i2c_device_config_t dev_cfg = {};
    dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
    dev_cfg.device_address = lcd_addr;
    dev_cfg.scl_speed_hz = I2C_CLK_HZ;
    dev_cfg.scl_wait_us = 0;
    dev_cfg.flags.disable_ack_check = 0;
    esp_err_t err = i2c_master_bus_add_device(i2c_bus, &dev_cfg, &lcd_dev);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "LCD device add failed: %d", (int)err);
        return;
    }
    lcd_ready = true;

    vTaskDelay(pdMS_TO_TICKS(50));
    lcd_write4bits(0x30, false);
    vTaskDelay(pdMS_TO_TICKS(5));
    lcd_write4bits(0x30, false);
    esp_rom_delay_us(150);
    lcd_write4bits(0x30, false);
    esp_rom_delay_us(150);
    lcd_write4bits(0x20, false);
    esp_rom_delay_us(150);

    lcd_command(0x28); // 4-bit, 2-line, 5x8
    lcd_command(0x0C); // display on, cursor off
    lcd_command(0x06); // entry mode
    lcd_command(0x01); // clear
}

static void esp_sr_init(void) {
    srmodel_list_t *models = esp_srmodel_init("model");
    if (!models) {
        ESP_LOGE(TAG, "ESP-SR models not found (flash srmodels.bin)");
        return;
    }

    afe_config_t *afe_config = afe_config_init("M", models, AFE_TYPE_SR, AFE_MODE_LOW_COST);
    if (!afe_config) {
        ESP_LOGE(TAG, "Failed to init AFE config");
        return;
    }
    afe_config->vad_init = true;
    afe_config->wakenet_init = true;

    afe_handle = (esp_afe_sr_iface_t *)esp_afe_handle_from_config(afe_config);
    if (!afe_handle) {
        ESP_LOGE(TAG, "Failed to create AFE handle");
        return;
    }
    afe_data = afe_handle->create_from_config(afe_config);
    if (!afe_data) {
        ESP_LOGE(TAG, "Failed to create AFE data");
        return;
    }
    ESP_LOGI(TAG, "ESP-SR initialized");
}

static void setup_i2s(void) {
    i2s_chan_config_t chan_cfg = {};
    chan_cfg.id = I2S_PORT;
    chan_cfg.role = I2S_ROLE_MASTER;
    chan_cfg.dma_desc_num = 16;
    chan_cfg.dma_frame_num = 256;
    chan_cfg.auto_clear = true;
    chan_cfg.auto_clear_before_cb = false;
    chan_cfg.allow_pd = false;
    chan_cfg.intr_priority = 0;

    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, &rx_handle));

    i2s_std_config_t std_cfg;
    memset(&std_cfg, 0, sizeof(std_cfg));
    std_cfg.clk_cfg.sample_rate_hz = SAMPLE_RATE;
    std_cfg.clk_cfg.clk_src = I2S_CLK_SRC_DEFAULT;
#if SOC_I2S_HW_VERSION_2
    std_cfg.clk_cfg.ext_clk_freq_hz = 0;
#endif
    std_cfg.clk_cfg.mclk_multiple = I2S_MCLK_MULTIPLE_256;
    std_cfg.clk_cfg.bclk_div = 8;

    std_cfg.slot_cfg.data_bit_width = I2S_DATA_BIT_WIDTH_32BIT;
    std_cfg.slot_cfg.slot_bit_width = I2S_SLOT_BIT_WIDTH_AUTO;
    std_cfg.slot_cfg.slot_mode = I2S_SLOT_MODE_MONO;
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
    std_cfg.slot_cfg.ws_width = I2S_DATA_BIT_WIDTH_32BIT;
    std_cfg.slot_cfg.ws_pol = false;
    std_cfg.slot_cfg.bit_shift = true;
#if SOC_I2S_HW_VERSION_1
    std_cfg.slot_cfg.msb_right = false;
#else
    std_cfg.slot_cfg.left_align = true;
    std_cfg.slot_cfg.big_endian = false;
    std_cfg.slot_cfg.bit_order_lsb = false;
#endif
    std_cfg.gpio_cfg.mclk = I2S_GPIO_UNUSED;
    std_cfg.gpio_cfg.bclk = I2S_SCK;
    std_cfg.gpio_cfg.ws = I2S_WS;
    std_cfg.gpio_cfg.dout = I2S_GPIO_UNUSED;
    std_cfg.gpio_cfg.din = I2S_SD;
    std_cfg.gpio_cfg.invert_flags.mclk_inv = false;
    std_cfg.gpio_cfg.invert_flags.bclk_inv = false;
    std_cfg.gpio_cfg.invert_flags.ws_inv = false;

    ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(rx_handle));
}

static void audio_task(void *pvParameters) {
    while (!afe_handle || !afe_data) {
        vTaskDelay(pdMS_TO_TICKS(200));
    }

    int feed_chunk = afe_handle->get_feed_chunksize(afe_data);
    int32_t *i2s_buf = (int32_t *)malloc(feed_chunk * sizeof(int32_t));
    int16_t *feed_buf = (int16_t *)malloc(feed_chunk * sizeof(int16_t));
    int agg_capacity_samples = feed_chunk * UDP_AGG_FRAMES;
    int16_t *agg_buf = (int16_t *)malloc(agg_capacity_samples * sizeof(int16_t));
    uint8_t *udp_buf = (uint8_t *)malloc(agg_capacity_samples * sizeof(int16_t) + UDP_AUDIO_HEADER);
    if (!i2s_buf || !feed_buf || !agg_buf || !udp_buf) {
        ESP_LOGE(TAG, "Audio buffer alloc failed");
        vTaskDelete(NULL);
        return;
    }

    uint32_t log_tick = 0;
    uint32_t timeout_tick = 0;
    static bool showing_wake = false;
    static TickType_t wake_tick = 0;
    static bool recording = false;
    static TickType_t record_start_tick = 0;
    static TickType_t last_lcd_tick = 0;
    static bool pending_idle = false;
    static TickType_t pending_idle_tick = 0;
    static int listening_dots = 0;
    static uint32_t audio_seq = 0;
    int agg_samples = 0;
    int frame_ms = (feed_chunk * 1000) / SAMPLE_RATE;
    if (frame_ms <= 0) frame_ms = 30;
    int silence_frames = 0;

    while (true) {
        size_t bytes_read = 0;
        esp_err_t r = i2s_channel_read(rx_handle, i2s_buf, feed_chunk * sizeof(int32_t),
                                       &bytes_read, pdMS_TO_TICKS(100));
        if (r != ESP_OK && r != ESP_ERR_TIMEOUT) {
            ESP_LOGW(TAG, "I2S read error: %d bytes=%d", (int)r, (int)bytes_read);
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        if (r == ESP_ERR_TIMEOUT && (timeout_tick++ % 50) == 0) {
            ESP_LOGW(TAG, "I2S read timeout (bytes=%d)", (int)bytes_read);
        }
        if (bytes_read == 0) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        int samples = bytes_read / (int)sizeof(int32_t);
        for (int i = 0; i < samples; i++) {
            int32_t v = i2s_buf[i] >> 8; // 24-bit in 32-bit
            int32_t s = v >> 8;          // 24-bit -> 16-bit
            s <<= AUDIO_GAIN_SHIFT;
            if (s > 32767) s = 32767;
            if (s < -32768) s = -32768;
            feed_buf[i] = (int16_t)s;
        }
        if (samples < feed_chunk) {
            memset(&feed_buf[samples], 0, (feed_chunk - samples) * sizeof(int16_t));
        }

        afe_handle->feed(afe_data, feed_buf);
        afe_fetch_result_t *res = afe_handle->fetch(afe_data);
        TickType_t now = xTaskGetTickCount();
        if (res && res->wakeup_state == WAKENET_DETECTED) {
            ESP_LOGI(TAG, "Wake word detected!");
            lcd_show_status("WAKE WORD,", "DETECTED");
            showing_wake = true;
            wake_tick = now;
            if (!recording) {
                if (!audio_connect()) {
                    lcd_show_status("NET ERROR", "TCP CONNECT");
                    pending_idle = true;
                    pending_idle_tick = now;
                    gpio_set_level(LED_PIN, 0);
                    continue;
                }
                recording = true;
                record_start_tick = now;
                silence_frames = 0;
                pending_idle = false;
                tcp_send_start();
                gpio_set_level(LED_PIN, 1);
            } else {
            }
        }

        if (showing_wake && (now - wake_tick) > pdMS_TO_TICKS(800)) {
            showing_wake = false;
            last_lcd_tick = 0;
        }

        if (res) {
            bool energy_speech = false;
            const int16_t *energy_src = res->data ? res->data : feed_buf;
            int energy_samples = res->data ? (res->data_size / (int)sizeof(int16_t)) : feed_chunk;
            if (energy_samples > 0) {
                int64_t acc = 0;
                int step = 4;
                int count = energy_samples / step;
                if (count <= 0) {
                    step = 1;
                    count = energy_samples;
                }
                for (int i = 0; i < energy_samples; i += step) {
                    int32_t s = energy_src[i];
                    if (s < 0) s = -s;
                    acc += s;
                }
                int avg = (int)(acc / count);
                energy_speech = avg > ENERGY_THRESHOLD;
            }
            if (res->vad_state == VAD_SPEECH || energy_speech) {
                silence_frames = 0;
            } else {
                silence_frames++;
            }
        }

        if (recording) {
            int silence_ms = silence_frames * frame_ms;
            if (silence_ms > SILENCE_TIMEOUT_MS ||
                (now - record_start_tick) > pdMS_TO_TICKS(MAX_RECORD_MS)) {
                recording = false;
                if (agg_samples > 0) {
                    tcp_send_audio(agg_buf, (uint16_t)(agg_samples * sizeof(int16_t)),
                                   audio_seq++, udp_buf, agg_capacity_samples * sizeof(int16_t) + UDP_AUDIO_HEADER);
                    agg_samples = 0;
                }
                tcp_send_stop();
                audio_close_socket();
                gpio_set_level(LED_PIN, 0);
                lcd_show_status("JASON", "PROCESSING...");
                pending_idle = true;
                pending_idle_tick = now;
            }
        }

        if (pending_idle && (now - pending_idle_tick) > pdMS_TO_TICKS(800)) {
            lcd_show_idle();
            pending_idle = false;
        }

        if (recording && !showing_wake) {
            if (last_lcd_tick == 0 || (now - last_lcd_tick) > pdMS_TO_TICKS(LISTENING_ANIM_MS)) {
                listening_dots = (listening_dots % 3) + 1;
                lcd_show_listening(listening_dots);
                last_lcd_tick = now;
            }
        }

        if ((log_tick++ % 50) == 0) {
            ESP_LOGI(TAG, "Streaming audio chunks (samples=%d)", feed_chunk);
        }

        if (recording && audio_sock >= 0 && res) {
            const int16_t *payload = feed_buf;
            int payload_bytes = feed_chunk * (int)sizeof(int16_t);
            if (res->data && res->data_size > 0 && res->data_size <= payload_bytes) {
                payload = res->data;
                payload_bytes = res->data_size;
            }
            int payload_samples = payload_bytes / (int)sizeof(int16_t);
            int copied = 0;
            while (copied < payload_samples) {
                int space = agg_capacity_samples - agg_samples;
                int to_copy = payload_samples - copied;
                if (to_copy > space) {
                    to_copy = space;
                }
                memcpy(&agg_buf[agg_samples], &payload[copied], to_copy * sizeof(int16_t));
                agg_samples += to_copy;
                copied += to_copy;
                if (agg_samples == agg_capacity_samples) {
                    if (!tcp_send_audio(agg_buf, (uint16_t)(agg_samples * sizeof(int16_t)),
                                        audio_seq++, udp_buf, agg_capacity_samples * sizeof(int16_t) + UDP_AUDIO_HEADER)) {
                        recording = false;
                        audio_close_socket();
                        gpio_set_level(LED_PIN, 0);
                        lcd_show_status("NET ERROR", "TCP SEND");
                        pending_idle = true;
                        pending_idle_tick = now;
                        agg_samples = 0;
                        break;
                    }
                    agg_samples = 0;
                }
            }
        }
    }
}

extern "C" void app_main(void) {
    nvs_flash_init();
    gpio_reset_pin(LED_PIN);
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(LED_PIN, 0);
    if (i2c_master_init() == ESP_OK) {
        lcd_init();
        lcd_show_status("SMART HOME", "BOOTING...");
    } else {
        ESP_LOGW(TAG, "I2C init failed");
    }

    if (!wifi_init_sta()) {
        ESP_LOGE(TAG, "WiFi init failed. Aborting.");
        lcd_show_status("WIFI", "FAILED");
        return;
    }
    audio_init();
    setup_i2s();
    esp_sr_init();
    ESP_LOGI(TAG, "INMP411 analysis ready");
    lcd_show_idle();
    xTaskCreate(audio_task, "audio_task", 8192, NULL, 5, NULL);
}
