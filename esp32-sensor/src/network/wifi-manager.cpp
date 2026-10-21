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