cmake_minimum_required(VERSION 3.5)

list(APPEND EXTRA_COMPONENT_DIRS
    "esp-sr"
    "main/smart_home_mqtt"
)

set(EXCLUDE_COMPONENTS "esp_lcd")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(iot)
