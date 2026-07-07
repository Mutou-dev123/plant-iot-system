// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "models/sensor_data.h"
#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"

// LEDピンの設定
const int LED_DHT = 13;		// 温湿度（緑色）
const int LED_SOIL = 14;	// 土壌水分（青色）
const int LED_LIGHT = 16;	// 光量（黄色）

// タイマー管理用の変数
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間
const unsigned long INTERVAL = 2000;	// センサー取得間隔
const unsigned long FLASH_TIME = 100;	// 点滅間隔

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

	//==============================
    // LED初期化と「起動・初期化中」の高速点滅演出
    //==============================
	pinMode(LED_DHT, OUTPUT);
	pinMode(LED_SOIL, OUTPUT);
	pinMode(LED_LIGHT, OUTPUT);

	// 起動完了サインとして3回素早く同時点滅させる
	for (int i = 0; i < 3; i++) {
		digitalWrite(LED_DHT, HIGH);
		digitalWrite(LED_SOIL, HIGH);
		digitalWrite(LED_LIGHT, HIGH);
		delay(100);
		digitalWrite(LED_DHT, LOW);
		digitalWrite(LED_SOIL, LOW);
		digitalWrite(LED_LIGHT, LOW);
		delay(100);
	}

	// センサー初期化
	initDHT();
	initSoilSensor();
	initLightSensor();

	Serial.println("Plant Sensor Start");
}

void loop()
{
    unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得

    //==============================
    // 1. センサーデータ取得（2秒に1回だけ実行）
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

        // 状態判定（ここで各センサーが正常かエラーかをチェック）
        isDhtError = !data.isValid; 
		isSoilError  = (data.soilRaw <= 0 || data.soilRaw >= 4095);  
        isLightError = (data.lightRaw <= 0 || data.lightRaw >= 4095);

        //==============================
        // データ表示
        //==============================
        if (isDhtError) {
            Serial.println("Failed to read from DHT11");
        } else {
            Serial.printf("Plant ID     : %d\n", data.plantId);
            Serial.printf("Timestamp    : %lu ms\n", data.timestamp);
            Serial.printf("Temperature  : %.1f ℃\n", data.temperature);
            Serial.printf("Humidity     : %.1f %%\n", data.humidity);
            Serial.printf("Soil Raw     : %d\n", data.soilRaw);
            Serial.printf("Light Raw    : %d\n", data.lightRaw);
            Serial.println("------------------------");
        }
    }

    //==============================
    // 2. LEDの独立制御（常に超高速で実行され続ける）
    //==============================
    
    // データ取得直後の 100ms だけ true になるフラグ（ハートビート用）
    bool isHeartbeat = (currentMillis - lastReadTime < FLASH_TIME);

    // --- 温湿度（緑）の制御 ---
    if (isDhtError) {
        digitalWrite(LED_DHT, HIGH); // エラー時は常時点灯（SOS）
    } else {
        digitalWrite(LED_DHT, isHeartbeat ? HIGH : LOW); // 正常時は一瞬だけ光る
    }

    // --- 土壌水分（青）の制御 ---
    if (isSoilError) {
        digitalWrite(LED_SOIL, HIGH);
    } else {
        digitalWrite(LED_SOIL, isHeartbeat ? HIGH : LOW);
    }

    // --- 光量（黄色）の制御 ---
    if (isLightError) {
        digitalWrite(LED_LIGHT, HIGH);
    } else {
        digitalWrite(LED_LIGHT, isHeartbeat ? HIGH : LOW);
    }
}