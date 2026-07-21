//==================================================
// 温湿度センサー制御
// DHT11の初期化と温度・湿度の取得処理を実装する
//==================================================

#include "dht_sensor.h"

#include <Arduino.h>
#include <DHT.h>

#include "../config/pin_config.h"

//==============================
// DHT11設定
//==============================

constexpr uint8_t DHT_TYPE = DHT11;

// DHT11を扱うためのオブジェクトを作成
DHT dht(DHT_PIN, DHT_TYPE);

//==============================
// DHT11初期化
//==============================
void initDHT()
{
    dht.begin();
}

//==============================
// 温湿度取得
//==============================
void readDHT(SensorData &data)
{
    // 温度・湿度を取得
    data.temperature = dht.readTemperature();
    data.humidity = dht.readHumidity();

    // データ取得成功判定
    data.isValid = !(isnan(data.temperature) || isnan(data.humidity));
}