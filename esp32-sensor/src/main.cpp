// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"

void setup()
{
	//==============================
    // シリアル通信の初期化
    //==============================
	Serial.begin(115200);

	// DHT11を初期化
	initDHT();
	// V1.2を初期化
	initSoilSensor();

	Serial.println("Plant Sensor Start");
}

void loop()
{
	float temperature = getTemperature();
	float humidity = getHumidity();
	int soil = getSoilMoisture();

	if (isnan(temperature) || isnan(humidity))
	{
		Serial.println("Failed to read from DHT11");
	}
	else
	{
		Serial.printf("Temperature	: %.1f ℃\n", temperature);
		Serial.printf("Humidity	: %.1f %%\n", humidity);
	}

	Serial.printf("Soil Raw	: %d\n", soil);

	Serial.println("------------------------");

	delay(2000);
}