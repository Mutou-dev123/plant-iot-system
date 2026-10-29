//==================================================
// メイン処理（システム全体の制御）
//==================================================

#include <Arduino.h>

#include "config/config.h"

#include "models/sensor_data.h"

#include "sensors/dht_sensor.h"
#include "sensors/soil_sensor.h"
#include "sensors/light_sensor.h"

#include "utils/config_manager.h"
#include "utils/led_indicator.h"
#include "utils/logger.h"
#include "utils/time_manager.h"

#include "network/wifi-manager.h"
#include "network/api_client.h"

// センサー計測の管理
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間
unsigned long currentInterval = 5000;	// センサー取得間隔

// センサーエラーフラグ
bool isDhtError = false;
bool isSoilError = false;
bool isLightError = false;

// 現在の設定に従ってセンサーを取得し、サーバーへ送信する
void collectAndSendSensorData()
{
    const DeviceConfig& config = getCurrentDeviceConfig();

    SensorData data;

    // 現在の時刻を計測データへ設定する
    data.timestamp = getCurrentTimestamp();

    // 現在適用されているセンサー設定を反映する
    data.dhtEnabled = config.dhtEnabled;
    data.soilEnabled = config.soilEnabled;
    data.lightEnabled = config.lightEnabled;

    // センサー値を初期化する
    data.temperature = NAN;
    data.humidity = NAN;
    data.soilRaw = -1;
    data.lightRaw = -1;

    // センサーの有効状態を初期化する
    data.dhtValid = false;
    data.soilValid = false;
    data.lightValid = false;

    // 有効なセンサーだけ読み取る
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

    // センサーの読み取り結果を確認する
    isDhtError = data.dhtEnabled && !data.dhtValid;
    isSoilError = data.soilEnabled && !data.soilValid;
    isLightError = data.lightEnabled && !data.lightValid;

    // センサー状態と計測時刻をログに表示する
    printSystemAlert(
        data,
        isDhtError,
        isSoilError,
        isLightError
    );

    printTimeLog(data.timestamp);

    printSensorLog(
        data,
        isDhtError,
        isSoilError,
        isLightError
    );

    // センサーデータをRaspberry Piへ送信する
    Serial.println("Sending data to Django ...");

    int sendResult = sendSensorData(data);

    if (sendResult <= 0)
    {
        Serial.println("Failed to send sensor data.");
    }
}

//==============================
// 初期準備
//==============================
void setup()
{

    // シリアル通信の初期化
    Serial.begin(115200);

    // 各モジュールの初期化
    initLEDs();

    // 設定管理を初期化する
    initConfigManager();

    // 後からセンサーを有効化できるよう、すべてのセンサーを初期化する
    initDHT();
    initSoilSensor();
    initLightSensor();

    // ここでWi-Fi接続処理が入る
    connectWiFi();
    initTime();

    // 起動時に最新設定を取得する
    if (updateDeviceConfig())
    {
        const DeviceConfig& config = getCurrentDeviceConfig();

        currentInterval = static_cast<unsigned long>(config.intervalSeconds) * 1000UL;
    }

    Serial.println("Plant Sensor Start");

    // 起動時にセンサーデータを1回取得・送信する
    collectAndSendSensorData();

    lastReadTime = millis();
}

//==============================
// メイン処理
//==============================
void loop()
{

    unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得
    
    // 10秒ごとにRaspberry Piの設定変更を確認する
    if (shouldCheckDeviceConfig(currentMillis))
    {
        // 設定が変更された場合だけ反映する
        if (updateDeviceConfig())
        {
            const DeviceConfig& config = getCurrentDeviceConfig();

            // 新しい計測間隔をミリ秒へ変換する
            currentInterval = static_cast<unsigned long>(config.intervalSeconds) * 1000UL;

            // 設定変更後にセンサーデータを1回取得・送信する
            collectAndSendSensorData();

            // 次回の通常計測までの基準時刻を更新する
            lastReadTime = millis();

            // 設定取得・送信にかかった時間を反映する
            currentMillis = millis();
        }
    }

    // 通常の計測間隔になったらセンサーを取得する
    if (currentMillis - lastReadTime >= currentInterval)
    {
        lastReadTime = currentMillis; // 読み取り時間を更新
        collectAndSendSensorData();
    }

    //==============================
    // LEDの独立制御（常に実行）
    //==============================
    
    updateLEDs(currentMillis, lastReadTime, isDhtError, isSoilError, isLightError);

}