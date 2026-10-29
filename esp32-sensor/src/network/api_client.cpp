//==================================================
// API通信
//
// センサーデータをJSON変換とHTTP POST送信、
// Raspberry Piからのデバイス設定取得を行う。
//==================================================

#include "api_client.h"

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "../config/config.h"
#include "../utils/logger.h"

int sendSensorData(const SensorData& data)
{
    // Wi-Fi未接続時は通信を行わない
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("[HTTP] Wi-Fi is not connected.");
        return -1;
    }

    //========================
    // JSONデータ作成
    //========================

    JsonDocument doc;

    // デバイス識別情報
    doc["deviceName"] = DEVICE_NAME;
    doc["ipAddress"] = WiFi.localIP().toString();
    doc["macAddress"] = WiFi.macAddress();
    doc["firmwareVersion"] = FIRMWARE_VERSION;

    // 計測日時
    doc["timestamp"] = data.timestamp;

    // センサー有効設定
    doc["dhtEnabled"] = data.dhtEnabled;
    doc["soilEnabled"] = data.soilEnabled;
    doc["lightEnabled"] = data.lightEnabled;

    // DHTセンサー
    if (data.dhtEnabled && data.dhtValid)
    {
        doc["temperature"] = data.temperature;
        doc["humidity"] = data.humidity;
    }
    else
    {
        doc["temperature"] = nullptr;
        doc["humidity"] = nullptr;
    }

    // 土壌水分センサー
    if (data.soilEnabled && data.soilValid)
    {
        doc["soilRaw"] = data.soilRaw;
    }
    else
    {
        doc["soilRaw"] = nullptr;
    }

    // 光センサー
    if (data.lightEnabled && data.lightValid)
    {
        doc["lightRaw"] = data.lightRaw;
    }
    else
    {
        doc["lightRaw"] = nullptr;
    }

    // JSON文字列へ変換
    String json;
    serializeJson(doc, json);

    //========================
    // HTTP POST送信
    //========================

    HTTPClient http;
    int nextInterval = 300;

    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    Serial.println("====== HTTP REQUEST ======");
    Serial.print("API URL: ");
    Serial.println(API_URL);
    Serial.println("Request JSON:");
    Serial.println(json);
    Serial.println("==========================");

    int httpCode = http.POST(json);

    // HTTPレスポンスを取得
    String response = http.getString();

    //========================
    // HTTP結果・デバッグ情報
    //========================

    Serial.println("====== HTTP DEBUG ======");
    Serial.print("HTTP Code: ");
    Serial.println(httpCode);

    Serial.println("Response Body:");
    Serial.println(response);

    Serial.println("========================");

    //========================
    // レスポンス処理
    //========================

    if (httpCode >= 200 && httpCode < 300)
    {
        JsonDocument resDoc;

        DeserializationError error =
            deserializeJson(resDoc, response);

        if (!error)
        {
            JsonVariant value = resDoc["next_interval"];

            if (value.is<int>() && value.as<int>() > 0)
            {
                nextInterval = value.as<int>();
            }
            else
            {
                Serial.println(
                    "[HTTP] Invalid next_interval. Using default."
                );
            }
        }
        else
        {
            Serial.print("[HTTP] JSON parse error: ");
            Serial.println(error.c_str());
        }
    }
    else
    {
        nextInterval = -1; // 送信失敗
    }

    // 通信結果をログ出力
    printNetworkLog(httpCode, nextInterval);

    // HTTP通信終了
    http.end();

    return nextInterval;
}


bool fetchDeviceConfig(DeviceConfig& config)
{
    // Wi-Fi未接続時は設定を取得しない
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("[CONFIG] Wi-Fi is not connected.");
        return false;
    }

    // ESP32のMACアドレスをクエリに付けて設定APIを呼び出す
    String url = String(DEVICE_CONFIG_API_URL)
                + "?macAddress="
                + WiFi.macAddress();

    HTTPClient http;

    if (!http.begin(url))
    {
        Serial.println("[CONFIG] Failed to begin HTTP connection.");
        return false;
    }

    int httpCode = http.GET();

    if (httpCode != 200)
    {
        Serial.print("[CONFIG] HTTP error: ");
        Serial.println(httpCode);

        http.end();
        return false;
    }

    String response = http.getString();
    http.end();

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, response);

    if (error)
    {
        Serial.print("[CONFIG] JSON parse error: ");
        Serial.println(error.c_str());
        return false;
    }

    // 必要な項目がすべて存在し、型も正しいか確認する
    JsonVariant configVersion = doc["config_version"];
    JsonVariant intervalSeconds = doc["interval_seconds"];
    JsonVariant sensors = doc["sensors"];

    if (!configVersion.is<int>() ||
        !intervalSeconds.is<int>() ||
        !sensors.is<JsonObject>() ||
        !sensors["dht"].is<bool>() ||
        !sensors["soil"].is<bool>() ||
        !sensors["light"].is<bool>())
    {
        Serial.println("[CONFIG] Invalid response format.");
        return false;
    }

    // 正の値であることを確認する
    int newConfigVersion = configVersion.as<int>();
    int newIntervalSeconds = intervalSeconds.as<int>();

    if (newConfigVersion <= 0 || newIntervalSeconds <= 0)
    {
        Serial.println("[CONFIG] Invalid configuration value.");
        return false;
    }

    bool newDhtEnabled = sensors["dht"].as<bool>();
    bool newSoilEnabled = sensors["soil"].as<bool>();
    bool newLightEnabled = sensors["light"].as<bool>();

    // 全項目の検証後にまとめて反映
    config.configVersion = newConfigVersion;
    config.intervalSeconds = newIntervalSeconds;
    config.dhtEnabled = newDhtEnabled;
    config.soilEnabled = newSoilEnabled;
    config.lightEnabled = newLightEnabled;

    Serial.println("[CONFIG] Device configuration updated.");
    return true;
}