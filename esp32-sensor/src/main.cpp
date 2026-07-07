// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "models/sensor_data.h"
#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"

const int LED_PIN = 13;

void setup()
{

	//==============================
    // シリアル通信の初期化
    //==============================

	Serial.begin(115200);

	// LED初期化
	pinMode(LED_PIN, OUTPUT);
	digitalWrite(LED_PIN, LOW);

	// センサー初期化
	initDHT();
	initSoilSensor();
	initLightSensor();

	Serial.println("Plant Sensor Start");
}

void loop()
{

	// LED点灯
	digitalWrite(LED_PIN, HIGH);

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
	readLight(data);

	//==============================
    // データ表示
    //==============================

	if (!data.isValid)
	{
		Serial.println("Failed to read from DHT11");

		digitalWrite(LED_PIN, LOW);
	}
	else
	{
		Serial.printf("Plant ID	: %d\n", data.plantId);
		Serial.printf("Timestamp	: %lu ms\n", data.timestamp);

		Serial.printf("Temperature	: %.1f ℃\n", data.temperature);
		Serial.printf("Humidity	: %.1f %%\n", data.humidity);
		Serial.printf("Soil Raw	: %d\n", data.soilRaw);
		Serial.printf("Light Raw	: %d\n", data.lightRaw);
		
		Serial.println("------------------------");

		digitalWrite(LED_PIN, LOW);
	}

	delay(2000);
}