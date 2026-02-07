# WAKE_WORD

Tài liệu này tổng hợp **toàn bộ bước liên quan đến Wake Word** trong dự án ESP32-S3 (ESP-SR + INMP411), bao gồm luồng **TCP audio** về API server.

## 1) Chuẩn bị phần cứng
- Mic INMP411, nguồn 3.3V, GND chung.
- Dây I2S theo cấu hình bạn đang dùng trong code.
  - Ví dụ hiện tại trong `apps/iot/main/smart_home_mqtt/smart_home_mqtt.cpp`:
    - `BCLK/SCK` -> GPIO12
    - `WS` -> GPIO11
    - `SD` -> GPIO10
    - `LR` -> GND (mono)
- (Tuỳ chọn) LCD I2C để hiển thị trạng thái:
  - `SCL` -> GPIO4
  - `SDA` -> GPIO5

## 2) Chọn Wake Word + VAD trong menuconfig
Chạy:
```bash
cd apps/iot
pio run -t menuconfig
```
Chọn:
- `ESP Speech Recognition -> Load Multiple Wake Words (WakeNet9)`
  - Bật câu bạn muốn, ví dụ **Hi, Jason** (`wn9_hijason_tts2`)
- `ESP Speech Recognition -> Select voice activity detection`
  - Chọn **vadnet1 medium**

Lưu cấu hình rồi thoát.

## 3) Build để tạo cấu hình
```bash
pio run
```

## 4) Đảm bảo sdkconfig đúng
Nếu `.pio/build/.../config/sdkconfig.h` không tồn tại, script `gen_models.bat` sẽ dùng `apps/iot/sdkconfig`.
Kiểm tra nhanh:
```powershell
Select-String -Path ".pio\build\esp32-s3-devkitc-1-idf\config\sdkconfig.h","sdkconfig" -Pattern "CONFIG_SR_WN_|CONFIG_SR_VADN"
```
Bạn phải thấy:
- WakeNet đã bật (vd `CONFIG_SR_WN_WN9_HIJASON_TTS2=y`)
- VADNET1 medium (`CONFIG_SR_VADN_VADNET1_MEDIUM=y`)

## 5) Tạo srmodels.bin
```bat
gen_models.bat
```
Kết quả nằm ở `apps/iot/srmodels/srmodels.bin`.

## 6) Kiểm tra srmodels có đúng model (tuỳ chọn)
Windows PowerShell:
```powershell
%USERPROFILE%\.platformio\penv\.espidf-5.5.0\Scripts\python.exe check_models.py
```
Kỳ vọng có `wn9_hijason_tts2` và `vadnet1_medium`.

## 7) Lấy offset partition model
```bat
%USERPROFILE%\.platformio\penv\.espidf-5.5.0\Scripts\python.exe ^
  %USERPROFILE%\.platformio\packages\framework-espidf\components\partition_table\gen_esp32part.py ^
  .pio\build\esp32-s3-devkitc-1-idf\partitions.bin
```
Tìm dòng `model` để lấy **Offset**.
Bạn cũng có thể lấy từ boot log, ví dụ: `model  ...  005f0000` -> offset là `0x005f0000`.

## 8) Flash srmodels.bin
```bat
%USERPROFILE%\.platformio\penv\.espidf-5.5.0\Scripts\python.exe ^
  %USERPROFILE%\.platformio\packages\tool-esptoolpy\esptool.py ^
  --chip esp32s3 --port COMx write_flash 0xOFFSET srmodels\srmodels.bin
```
Nếu gặp lỗi `ModuleNotFoundError: No module named 'serial'`, cài pyserial:
```bat
%USERPROFILE%\.platformio\penv\.espidf-5.5.0\Scripts\python.exe -m pip install pyserial
```

## 9) Flash firmware
```bash
pio run -t upload --upload-port COMx
```

## 10) Monitor và test
```bash
pio device monitor -b 115200 --port COMx
```
Bạn nên thấy:
- `MODEL_LOADER: Successfully load srmodels`
- **Không còn** `wakenet model not found`
- Khi nói câu đã chọn (ví dụ “Hi, Jason”) => log `Wake word detected!`
- Nếu có LCD I2C: hiện `WAKE WORD / DETECTED` trong ~2s rồi về `SMART HOME / LISTENING...`

## 11) Kết nối TCP audio tới API
- Trên API server, đảm bảo `AUDIO_TCP_ENABLED=1` và lắng nghe port `AUDIO_TCP_PORT` (mặc định 3334).
- Trên ESP32, cấu hình:
  - `CONFIG_SMART_HOME_AUDIO_UDP_HOST` = IP máy chạy API
  - `CONFIG_SMART_HOME_AUDIO_UDP_PORT` = 3334 (TCP port)

Lưu ý: biến config còn chữ "UDP" nhưng luồng hiện tại dùng **TCP**.

## 12) MQTT (tuỳ chọn)
Nếu bạn muốn dùng MQTT (telemetry/trigger), làm nhanh như sau:

1. Khởi động broker:
```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "#" -v
```

2. Cấu hình API trong `apps/api/.env`:
```
MQTT_BROKER_URL=mqtt://<IP_MAY_CHAY_BROKER>:1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_SUB_TOPICS=sensor/temp_humid_msa_assign1,smart-home/+/+/+/+
```

3. Cấu hình ESP32 (nếu cần) trong sdkconfig:
- `CONFIG_SMART_HOME_MQTT_BROKER_URI`
- `CONFIG_SMART_HOME_MQTT_USERNAME`
- `CONFIG_SMART_HOME_MQTT_PASSWORD`

## 13) Lỗi thường gặp
- **`wakenet model not found`**: srmodels.bin không chứa WakeNet hoặc flash sai offset.
- **AFE pipeline vẫn WebRTC**: VADNET1 chưa bật trong sdkconfig đang dùng.
- **Không có `.pio/build/.../config/sdkconfig.h`**: chạy `pio run` để tạo config, hoặc `gen_models.bat` sẽ dùng `apps/iot/sdkconfig`.
- **`ModuleNotFoundError: No module named 'serial'`**: cài pyserial theo bước 8.
- **`TCP send failed`**: API server không chạy, sai IP/port, hoặc kết nối bị ngắt.

## 14) Ghi nhớ
- Mỗi lần đổi wake word / VAD: **build -> gen_models.bat -> flash srmodels.bin**.
- Nếu tăng size model: phải chỉnh `apps/iot/partitions.csv` rồi build lại.
