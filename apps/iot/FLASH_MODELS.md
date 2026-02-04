# Hướng dẫn build/flash Wake Word cho ESP32-S3

Tài liệu này tạo quy trình chuẩn để build firmware và nạp model Wake Word ("Hi ESP").

## 1. Cấu hình model (đã bật sẵn trong repo)
Repo đã bật WakeNet9 (Hi ESP) và VADNET1 medium trong:
- sdkconfig
- sdkconfig.esp32-s3-devkitc-1-idf

Nếu bạn dùng `pio run -t menuconfig`, các tuỳ chọn nằm ở:
ESP Speech Recognition -> Load Multiple Wake Words (WakeNet9) -> Hi,ESP (wn9_hiesp)
ESP Speech Recognition -> Select voice activity detection -> vadnet1 medium

## 2. Build firmware (tạo config cho PlatformIO)
```bash
pio run
```
Lưu ý: PlatformIO có thể không tạo file `.pio/build/.../sdkconfig`. Script `gen_models.bat` sẽ tự dùng file `apps/iot/sdkconfig` khi không có file này.

## 3. Tạo srmodels.bin
Chạy script đã chuẩn hoá:
```bat
gen_models.bat
```
File được tạo tại `apps/iot/srmodels/srmodels.bin`.

## 4. Kiểm tra partition `model`
Xem offset và size:
```bash
pio run --target partition-table
```
Nếu lệnh trên không hỗ trợ, dùng cách thủ công để đọc `partitions.bin`:
```bat
%USERPROFILE%\.platformio\penv\.espidf-5.5.0\Scripts\python.exe ^
  %USERPROFILE%\.platformio\packages\framework-espidf\components\partition_table\gen_esp32part.py ^
  .pio\build\esp32-s3-devkitc-1-idf\partitions.bin
```
Tìm dòng `model` để lấy offset. Kiểm tra dung lượng `srmodels/srmodels.bin` nhỏ hơn size của partition.
Gợi ý: script movemodel sẽ in ra "Recommended model partition size" sau khi chạy.
Ví dụ offset thực tế của dự án hiện tại là `0x6f0000` (có thể thay đổi nếu bạn chỉnh `partitions.csv`).

## 5. Flash model vào thiết bị
Thay COMx và 0xOFFSET cho đúng:
```bat
%USERPROFILE%\.platformio\packages\tool-esptoolpy\esptool.py --chip esp32s3 --port COMx write_flash 0xOFFSET srmodels\srmodels.bin
```
Ví dụ (offset `0x6f0000`):
```bat
%USERPROFILE%\.platformio\packages\tool-esptoolpy\esptool.py --chip esp32s3 --port COMx write_flash 0x6f0000 srmodels\srmodels.bin
```

## 6. Flash firmware
```bash
pio run --target flash
```

## 7. Monitor (tuỳ chọn)
```bash
pio device monitor -b 115200
```

## Lưu ý
- Nếu đổi Wake Word hoặc VAD, hãy chạy lại `gen_models.bat` và flash lại srmodels.bin.
- Nếu srmodels.bin vượt quá size của partition `model`, cần tăng size partition (và giảm app/spiffs nếu cần).
- Bạn có thể test đường truyền UDP audio bằng script: `apps/iot/scripts/udp-audio-test.mjs` (chỉ gửi tone 440Hz để kiểm tra pipeline, không kích hoạt wake word).
