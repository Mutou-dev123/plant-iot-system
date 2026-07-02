//==================================================
// 温湿度センサー制御
// DHT11の初期化と温度・湿度の取得処理を実装する
//==================================================

#include "dht_sensor.h"

#include <Arduino.h>
#include <DHT.h>

//==============================
// DHT11設定
//==============================

#define DHTPIN 4
#define DHTTYPE DHT11

// DHT11を扱うためのオブジェクトを作成
DHT dht(DHTPIN, DHTTYPE);

//==============================
// DHT11初期化
//==============================
void readDHT(SensorData &data)
{
    // 温度・湿度を取得
    data.temperature = dht.readTemperature();
    data.humidity = dht.readHumidity();

    // データ取得成功判定
    data.isValid = !(isnan(data.temperature) || isnan(data.humidity));
}