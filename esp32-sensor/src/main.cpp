// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "models/sensor_data.h"

#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"

#include "utils/logger.h"           // ログ表示の読込
#include "utils/led_indicator.h"    // LEDインジケーターの読込

// タイマー管理用の変数
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間
const unsigned long INTERVAL = 2000;	// センサー取得間隔

// 各センサーのエラー状態記憶フラグ
bool isDhtError = false;
bool isSoilError = false;
bool isLightError = false;

void setup()
{
	//==============================
    // シリアル通信の初期化
    //==============================

	Serial.begin(115200);

	// 各モジュールの初期化
    initLEDs();
	initDHT();
	initSoilSensor();
	initLightSensor();

	Serial.println("Plant Sensor Start");
}

void loop()
{
    unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得

    //==============================
    // センサーデータ取得
    //==============================
    if (currentMillis - lastReadTime >= INTERVAL)
    {
        lastReadTime = currentMillis; // 読み取り時間を更新

        SensorData data;
        data.plantId = 1;
        data.timestamp = currentMillis;

        readDHT(data);
        readSoil(data);
        readLight(data);

        // センサーエラー判定
        isDhtError = !data.isValid; 
		isSoilError  = (data.soilRaw <= 0 || data.soilRaw >= 4095);  
        isLightError = (data.lightRaw <= 0 || data.lightRaw >= 4095);

        // ログ表示（センサーエラー＆センサーデータ）
        printSensorLog(data, isDhtError, isSoilError, isLightError);
    } 


    //==============================
    // LEDの独立制御（常に実行）
    //==============================
    
    updateLEDs(currentMillis, lastReadTime, isDhtError, isSoilError, isLightError);
}