idf_component_register(SRCS "smart_home_mqtt.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES esp-sr esp_wifi esp_event nvs_flash mqtt driver)
