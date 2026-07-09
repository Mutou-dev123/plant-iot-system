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


bool sendSensorData(const SensorData& data)
{
    // Wi-Fi未接続なら送信しない
    if (WiFi.status() != WL_CONNECTED)
    {
        return false;
    }

    //========================
    // JSONデータ作成
    //========================

    JsonDocument doc;

    doc["plantId"] = data.plantId;
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

    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(json);

    http.end();

    return (httpCode >= 200 && httpCode < 300);
}