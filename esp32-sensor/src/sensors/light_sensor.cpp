//==================================================
// 光量センサー制御
// フォトレジスタモジュールの初期化と光量取得処理を実装する
//==================================================

#include "light_sensor.h"

#include <Arduino.h>

#include "../config/pin_config.h"

//==============================
// 光量センサー初期化
//==============================

void initLightSensor()
{
    pinMode(LIGHT_PIN, INPUT);
}

//==============================
// 光量取得
//==============================

void readLight(SensorData &data)
{
    // ADC値を取得
    data.lightRaw = analogRead(LIGHT_PIN);
}