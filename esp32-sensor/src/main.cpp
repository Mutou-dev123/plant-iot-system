//==================================================
// メイン処理（システム全体の制御）
//==================================================

#include <Arduino.h>

#include "config/config.h"
#include "models/sensor_data.h"
#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"
#include "utils/logger.h"
#include "utils/led_indicator.h"
#include "utils/time_manager.h"
#include "network/wifi-manager.h"
#include "network/api_client.h"

// タイマー管理用の変数
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間

// 計測間隔
unsigned long currentInterval = 5000;	// センサー取得間隔

// センサーエラーフラグ
bool isDhtError = false;
bool isSoilError = false;
bool isLightError = false;

//==============================
// 初期準備
//==============================
void setup()
{

    // シリアル通信の初期化
    Serial.begin(115200);

    // 各モジュールの初期化
    initLEDs();

    // 有効なセンサーだけ初期化する
    if (SENSOR_DHT_ENABLED)
    {
        initDHT();
    }

    if (SENSOR_SOIL_ENABLED)
    {
        initSoilSensor();
    }

    if (SENSOR_LIGHT_ENABLED) {
        initLightSensor();
    }

    // ここでWi-Fi接続処理が入る
    connectWiFi();

    initTime();

    Serial.println("Plant Sensor Start");
}

//==============================
// メイン処理
//==============================
void loop()
{

    unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得

    // センサーデータ取得
    if (currentMillis - lastReadTime >= currentInterval)
    {
        lastReadTime = currentMillis; // 読み取り時間を更新

        // センサーデータを初期化
        SensorData data;

        data.timestamp = getCurrentTimestamp();

        // 有効設定を反映
        data.dhtEnabled = SENSOR_DHT_ENABLED;
        data.soilEnabled = SENSOR_SOIL_ENABLED;
        data.lightEnabled = SENSOR_LIGHT_ENABLED;

        // 計測結果の初期値
        data.temperature = NAN;
        data.humidity = NAN;
        data.soilRaw = -1;
        data.lightRaw = -1;

        data.dhtValid = false;
        data.soilValid = false;
        data.lightValid = false;

        // 有効なセンサーだけ計測
        if (data.dhtEnabled)
        {
            readDHT(data);
        }

        if (data.soilEnabled)
        {
            readSoil(data);
        }

        if (data.lightEnabled)
        {
            readLight(data);
        }

        // 無効なセンサーはエラーにしない
        isDhtError = data.dhtEnabled && !data.dhtValid;
        isSoilError = data.soilEnabled && !data.soilValid;
        isLightError = data.lightEnabled && !data.lightValid;

        // ログ表示
        printSystemAlert(
            data,
            isDhtError,
            isSoilError,
            isLightError
        );

        // 計測時刻
        printTimeLog(data.timestamp);

        // センサーデータ
        printSensorLog(
            data,
            isDhtError,
            isSoilError,
            isLightError
        );

        //==============================
        // データ送信
        //==============================

        Serial.println("Sending data to Django ...");
        int nextIntervalSec = sendSensorData(data);

        if (nextIntervalSec > 0)
        {
            // 送信成功時：Djangoから届いた秒数をミリ秒に変換して次のタイマーにセット
            currentInterval = (unsigned long)nextIntervalSec * 1000;
            Serial.print("Interval updated by Django ");
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

    //==============================
    // LEDの独立制御（常に実行）
    //==============================
    
    updateLEDs(currentMillis, lastReadTime, isDhtError, isSoilError, isLightError);

}