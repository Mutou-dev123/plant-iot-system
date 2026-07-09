//==================================================
// Wi-Fi管理
// Wi-Fiへの接続および接続状態を管理する処理を実装する
//==================================================

#include "wifi-manager.h"

#include <WiFi.h>

#include "../config/config.h"

//==============================
// Wi-Fi接続
//==============================

void connectWiFi()
{
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
    }
}