@echo off
set SDKCONFIG_BUILD=.pio\build\esp32-s3-devkitc-1-idf\sdkconfig
set SDKCONFIG_FALLBACK=sdkconfig
set SDKCONFIG=

if exist "%SDKCONFIG_BUILD%" (
    set SDKCONFIG=%SDKCONFIG_BUILD%
) else if exist "%SDKCONFIG_FALLBACK%" (
    set SDKCONFIG=%SDKCONFIG_FALLBACK%
)

if "%SDKCONFIG%"=="" (
    echo ERROR: sdkconfig not found. Run "pio run" first or ensure apps\iot\sdkconfig exists.
    exit /b 1
)

python esp-sr\model\movemodel.py -d1 "%SDKCONFIG%" -d2 esp-sr -d3 .
if exist srmodels\srmodels.bin (
    echo SUCCESS: srmodels\srmodels.bin created.
) else (
    echo FAILURE: srmodels\srmodels.bin not found.
)
