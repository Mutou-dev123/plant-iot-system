//==================================================
// Wi-Fi管理
// Wi-Fiへの接続および接続状態を管理する処理を実装する
//==================================================

#include "wifi-manager.h"

#include <WiFi.h>

#include "../config/config.h"

namespace
{
    // 再接続を試す間隔。毎ループ接続処理を実行しないようにする
    constexpr unsigned long WIFI_RECONNECT_INTERVAL_MS = 30000;

    unsigned long lastReconnectAttempt = 0;
}


//==============================
// Wi-Fi接続
//==============================

void connectWiFi()
{
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);

    for (int i = 0; i < WIFI_COUNT; i++)
    {
        Serial.println();
        Serial.print("Connecting to ");
        Serial.println(WIFI_LIST[i].ssid);

        WiFi.begin(
            WIFI_LIST[i].ssid,
            WIFI_LIST[i].password
        );

        int retry = 0;

        while (
            WiFi.status() != WL_CONNECTED &&
            retry < 20
        )
        {
            Serial.print(".");
            delay(500);
            retry++;
        }

        if (WiFi.status() == WL_CONNECTED)
        {
            Serial.println();
            Serial.println("Connected!");

            Serial.print("SSID: ");
            Serial.println(WiFi.SSID());

            Serial.print("IP Address: ");
            Serial.println(WiFi.localIP());

            return;
        }

        Serial.println();
        Serial.println("Connection failed.");
    }

    Serial.println();
    Serial.println("No available Wi-Fi found.");
}

bool ensureWiFiConnected(unsigned long currentMillis)
{
    // 接続中なら何もしない
    if (WiFi.status() == WL_CONNECTED)
    {
        return true;
    }

    // 再接続処理を短時間に繰り返さない
    if (
        currentMillis - lastReconnectAttempt <
        WIFI_RECONNECT_INTERVAL_MS
    )
    {
        return false;
    }

    lastReconnectAttempt = currentMillis;

    Serial.println("[WiFi] Connection lost. Reconnecting...");
    connectWiFi();

    return WiFi.status() == WL_CONNECTED;
}