// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "models/sensor_data.h"
#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"

void setup()
{
	//==============================
    // シリアル通信の初期化
    //==============================
	Serial.begin(115200);

	// センサー初期化
	initDHT();
	initSoilSensor();

	Serial.println("Plant Sensor Start");
}

void loop()
{
	//==============================
    // センサーデータ
    //==============================

	SensorData data;

	// 基本情報
	data.plantId = 1;
	data.timestamp = millis();

	//==============================
    // センサーデータ取得
    //==============================
	readDHT(data);
	readSoil(data);
	data.illuminance = 0;

	//==============================
    // データ表示
    //==============================
	if (!data.isValid)
	{
		Serial.println("Failed to read from DHT11");
	}
	else
	{
		Serial.printf("Plant ID	: %d\n", data.plantId);
		Serial.printf("Timestamp	: %lu ms\n", data.timestamp);

		Serial.printf("Temperature	: %.1f ℃\n", data.temperature);
		Serial.printf("Humidity	: %.1f %%\n", data.humidity);
		Serial.printf("Soil Raw	: %d\n", data.soilRaw);
		
		Serial.println("------------------------");
	}

	delay(2000);
}