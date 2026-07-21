//==================================================
// ピン設定（ヘッダファイル）
// センサー接続におけるピンのGPIO設定などを一括で管理する
//==================================================

#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

#include <Arduino.h>

// ==========================
// DHT11
// ==========================
constexpr uint8_t DHT_PIN = 4;

// ==========================
// Soil Moisture Sensor
// ==========================
constexpr uint8_t SOIL_PIN = 34;

// ==========================
// Light Sensor
// ==========================
constexpr uint8_t LIGHT_PIN = 35;

// ==========================
// LEDs
// ==========================
constexpr uint8_t LED_DHT = 13;		// 温湿度（緑色）
constexpr uint8_t LED_SOIL = 14;	// 土壌水分（青色）
constexpr uint8_t LED_LIGHT = 16;	// 光量（黄色）

#endif