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
    Serial.print("Connecting to Wi-Fi");

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED)
    {
        Serial.print(".");
        delay(500);
    }

    Serial.println();
    Serial.println("Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}