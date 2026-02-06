#include <Arduino.h>
#include <driver/i2s.h>

#define I2S_BCLK 12
#define I2S_WS   11
#define I2S_SD   10
#define BTN_PIN  9

static const int SAMPLE_RATE = 16000;
static const int FRAMES = 256;

static int32_t i2s_buf[FRAMES * 2];
static int16_t pcm16_buf[FRAMES];

static bool recording = false;
static uint32_t lastBtnMs = 0;
static uint32_t lastRdyMs = 0;

static void send4(const char* s) { Serial0.write((const uint8_t*)s, 4); }
static void sendSTRT() { send4("STRT"); Serial0.flush(); }
static void sendSTOP() { send4("STOP"); Serial0.flush(); }
static void sendRDY()  { send4("RDY!"); Serial0.flush(); }

static void sendFrame(const uint8_t* payload, uint16_t len) {
  send4("AUD0");
  Serial0.write((uint8_t*)&len, 2);
  Serial0.write(payload, len);
}

static bool buttonPressedEdge() {
  if (digitalRead(BTN_PIN) == LOW && (millis() - lastBtnMs) > 250) {
    lastBtnMs = millis();
    return true;
  }
  return false;
}

void setup() {
  Serial0.begin(1000000);
  delay(300);

  pinMode(BTN_PIN, INPUT_PULLUP);

  i2s_config_t cfg = {};
  cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
  cfg.sample_rate = SAMPLE_RATE;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
  cfg.communication_format = I2S_COMM_FORMAT_I2S_MSB;
  cfg.dma_buf_count = 16;
  cfg.dma_buf_len = 256;

  i2s_pin_config_t pins = {};
  pins.bck_io_num = I2S_BCLK;
  pins.ws_io_num  = I2S_WS;
  pins.data_out_num = -1;
  pins.data_in_num  = I2S_SD;

  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pins);
  i2s_set_clk(I2S_NUM_0, SAMPLE_RATE, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_STEREO);

  i2s_zero_dma_buffer(I2S_NUM_0);
  i2s_start(I2S_NUM_0);
}

void loop() {
  if (buttonPressedEdge()) {
    recording = !recording;
    if (recording) {
      i2s_zero_dma_buffer(I2S_NUM_0);
      sendSTRT();
      delay(30);
    } else {
      sendSTOP();
      delay(30);
    }
  }

  if (!recording) {
    if (millis() - lastRdyMs > 500) {
      lastRdyMs = millis();
      sendRDY();
    }
    delay(5);
    return;
  }

  size_t bytes_read = 0;
  i2s_read(I2S_NUM_0, i2s_buf, sizeof(i2s_buf), &bytes_read, portMAX_DELAY);
  int frames = (bytes_read / 4) / 2;

  for (int i = 0; i < frames; i++) {
    int32_t L = i2s_buf[i * 2 + 0];
    pcm16_buf[i] = (int16_t)(L >> 13); // chống clipping
  }

  sendFrame((uint8_t*)pcm16_buf, (uint16_t)(frames * 2));
}
