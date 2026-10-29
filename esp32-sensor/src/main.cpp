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

// センサー計測の管理
unsigned long lastReadTime = 0;			// 最後にセンサーを読み取った時間
unsigned long currentInterval = 5000;	// センサー取得間隔

// デバイス設定取得の管理
constexpr unsigned long CONFIG_CHECK_INTERVAL = 10000;   // 設定の確認間隔（10秒）
unsigned long lastConfigCheckTime = 0;                  // 設定の最終確認時間

// Raspberry Piから取得した実行時設定
bool dhtEnabled = SENSOR_DHT_ENABLED;
bool soilEnabled = SENSOR_SOIL_ENABLED;
bool lightEnabled = SENSOR_LIGHT_ENABLED;

int currentConfigVersion = 0;           // 現在の設定バージョン

// センサーエラーフラグ
bool isDhtError = false;
bool isSoilError = false;
bool isLightError = false;

// 取得した設定をESP32の実行時設定へ反映する
void applyDeviceConfig(const DeviceConfig& config)
{
    dhtEnabled = config.dhtEnabled;
    soilEnabled = config.soilEnabled;
    lightEnabled = config.lightEnabled;

    // 秒単位の設定値をミリ秒へ変換する
    currentInterval =
        static_cast<unsigned long>(config.intervalSeconds) * 1000UL;

    currentConfigVersion = config.configVersion;

    Serial.println("[CONFIG] Runtime configuration applied.");
    Serial.print("[CONFIG] Version: ");
    Serial.println(currentConfigVersion);
    Serial.print("[CONFIG] Interval: ");
    Serial.print(config.intervalSeconds);
    Serial.println(" seconds");
}

// Raspberry Piから設定を取得し、成功した場合だけ反映する
void checkDeviceConfig()
{
    DeviceConfig newConfig;

    if (fetchDeviceConfig(newConfig))
    {
        // 初回取得時、または設定バージョンが変わった場合だけ反映する
        if (newConfig.configVersion != currentConfigVersion)
        {
            applyDeviceConfig(newConfig);
        }
        else
        {
            Serial.println("[CONFIG] No configuration change.");
        }
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

    // 後からセンサーを有効かできるよう、すべてのセンサーを初期化する
    initDHT();
    initSoilSensor();
    initLightSensor();

    // ここでWi-Fi接続処理が入る
    connectWiFi();
    initTime();

    // 起動時に最新設定を1回取得する
    checkDeviceConfig();
    lastConfigCheckTime = millis();

    Serial.println("Plant Sensor Start");
}

//==============================
// メイン処理
//==============================
void loop()
{

    unsigned long currentMillis = millis(); // 現在のストップウォッチの時間を取得
    
    // センサー計測とは別に、10秒ごとに設定を確認する
    if (currentMillis - lastConfigCheckTime >= CONFIG_CHECK_INTERVAL)
    {
        lastConfigCheckTime = currentMillis;
        checkDeviceConfig();
    }

    // センサーデータ取得
    if (currentMillis - lastReadTime >= currentInterval)
    {
        lastReadTime = currentMillis; // 読み取り時間を更新

        // センサーデータを初期化
        SensorData data;

        data.timestamp = getCurrentTimestamp();

        // 現在の実行時設定を送信データへ反映する
        data.dhtEnabled = dhtEnabled;
        data.soilEnabled = soilEnabled;
        data.lightEnabled = lightEnabled;

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

        // 計測間隔は設定取得APIの値を正とする
        int sendResult = sendSensorData(data);

        if (sendResult <= 0)
        {
            Serial.println("Failed to send sensor data.");
        }

    }

    //==============================
    // LEDの独立制御（常に実行）
    //==============================
    
    updateLEDs(currentMillis, lastReadTime, isDhtError, isSoilError, isLightError);

}