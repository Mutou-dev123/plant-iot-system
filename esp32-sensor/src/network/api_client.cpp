//==================================================
// API通信
// センサーデータをJSON形式へ変換し、
// HTTP通信で送信する処理を実装する
//==================================================

#include "api_client.h"

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "../config/config.h"
#include "../utils/logger.h"

int sendSensorData(const SensorData& data)
{
    // Wi-Fi未接続なら送信しない
    if (WiFi.status() != WL_CONNECTED)
    {
        return -1;
    }

    //========================
    // JSONデータ作成
    //========================

    JsonDocument doc;

    doc["deviceName"] = DEVICE_NAME;
    doc["timestamp"] = data.timestamp;

    doc["temperature"] = data.temperature;
    doc["humidity"] = data.humidity;
    doc["soilRaw"] = data.soilRaw;
    doc["lightRaw"] = data.lightRaw;

    String json;

    serializeJson(doc, json);

    //========================
    // HTTP POST送信
    //========================

    HTTPClient http;
    int nextInterval = 300;

    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(json);

    if (httpCode >= 200 && httpCode < 300)
    {
        String response = http.getString();

        JsonDocument resDoc;
        deserializeJson(resDoc, response);

        JsonVariant value = resDoc["next_interval"];

        if (value.is<int>())
        {
            nextInterval = value.as<int>();
        }

    }
    else
    {
        nextInterval = -1;  // 送信失敗フラグ
    }

    printNetworkLog(httpCode, nextInterval);

    http.end();

    return nextInterval;
}