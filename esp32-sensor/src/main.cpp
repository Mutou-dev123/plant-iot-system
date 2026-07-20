// メイン処理（システム全体の制御）

#include <Arduino.h>

#include "models/sensor_data.h"

#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"

#include "network/api_client.h"
#include "utils/logger.h"           // ログ表示の読込
#include "utils/led_indicator.h"    // LEDインジケーターの読込

#include "network/wifi-manager.h"
#include "network/api_client.h"

// タイマー管理用の変数
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間

// Djangoからの指示で変動。初期値を5分（300,000ms）に設定
unsigned long currentInterval = 300000;	// センサー取得間隔

// 各センサーのエラー状態記憶フラグ
bool isDhtError = false;
bool isSoilError = false;
bool isLightError = false;

// HTTP通信テスト用
#define HTTP_TEST


//==============================
// 初期準備
//==============================
void setup()
{

    #ifdef HTTP_TEST

        // 通信テスト

        Serial.begin(115200);

        connectWiFi();

        SensorData data;

        data.timestamp = millis();
        data.temperature = 25.5;
        data.humidity = 60.2;
        data.soilRaw = 2000;
        data.lightRaw = 1500;
        data.isValid = true;

        sendSensorData(data);

    #else

        // シリアル通信の初期化
        Serial.begin(115200);

        // 各モジュールの初期化
        initLEDs();
        initDHT();
        initSoilSensor();
        initLightSensor();

        // ここでWi-Fi接続処理が入る

        Serial.println("Plant Sensor Start");

    #endif
}

//==============================
// メイン処理
//==============================
void loop()
{

    #ifdef HTTP_TEST


    #else
        unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得

        // センサーデータ取得
        if (currentMillis - lastReadTime >= currentInterval)
        {
            lastReadTime = currentMillis; // 読み取り時間を更新

            SensorData data;
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

            // すべてのセンサーが正常ならDjangoへ送信
            if (!isDhtError && !isSoilError && !isLightError)
            {
                Serial.println("Sending data to Django ...");
                int nextIntervalSec = sendSensorData(data);

                if (nextIntervalSec > 0)
                {
                    // 送信成功時：Djangoから届いた秒数をミリ秒に変換して次のタイマーにセット
                    currentInterval = (unsigned long)nextIntervalSec * 1000;
                    Serial.print("Interval updated by Django");
                    Serial.print(nextIntervalSec);
                    Serial.println(" sec");
                }
                else
                {
                    // 送信失敗時：一時的に10秒後にトライ
                    Serial.println("Failed to send data. Retry after 30 seconds.");
                    currentInterval = 30000;
                }
            }
        }

        //==============================
        // LEDの独立制御（常に実行）
        //==============================
        
        updateLEDs(currentMillis, lastReadTime, isDhtError, isSoilError, isLightError);

    #endif
}