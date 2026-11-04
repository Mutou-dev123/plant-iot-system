//==================================================
// デバイス設定管理
//
// Raspberry Piの設定APIを定期的に確認し、
// 設定バージョンが変わった場合だけ新しい設定を反映する。
//==================================================

#include "config_manager.h"

#include <Arduino.h>

#include "../config/config.h"

// 設定APIを確認する間隔（10秒）
constexpr unsigned long CONFIG_CHECK_INTERVAL_MS = 10000;

// 前回設定を確認した時刻
static unsigned long lastConfigCheckTime = 0;

// 現在ESP32に適用されている設定
static DeviceConfig currentConfig = {
    0,
    5,
    SENSOR_DHT_ENABLED,
    SENSOR_SOIL_ENABLED,
    SENSOR_LIGHT_ENABLED
};

// 最後にRaspberry Piへの報告が成功した設定バージョン
static int lastReportedConfigVersion = 0;


//==================================================
// 設定管理の初期化
//==================================================

void initConfigManager()
{
    // 設定確認時刻を初期化する
    lastConfigCheckTime = 0;

    // 現在の設定をコンパイル時の初期値で初期化する
    currentConfig.configVersion = 0;
    currentConfig.intervalSeconds = 5;
    currentConfig.dhtEnabled = SENSOR_DHT_ENABLED;
    currentConfig.soilEnabled = SENSOR_SOIL_ENABLED;
    currentConfig.lightEnabled = SENSOR_LIGHT_ENABLED;
}

//==================================================
// 設定確認タイミングの判定
//==================================================

bool shouldCheckDeviceConfig(unsigned long currentMillis)
{
    // 前回の確認から設定確認間隔が経過したか確認する
    if (currentMillis - lastConfigCheckTime < CONFIG_CHECK_INTERVAL_MS)
    {
        return false;
    }

    // 次回確認の基準時刻を更新する
    lastConfigCheckTime = currentMillis;

    return true;
}

//==================================================
// デバイス設定の取得と反映
//==================================================

bool updateDeviceConfig()
{
    DeviceConfig newConfig;

    // Raspberry Piから最新設定を取得する
    if (!fetchDeviceConfig(newConfig))
    {
        // 取得失敗時は現在の設定を維持する
        Serial.println("[CONFIG] Keeping current configuration.");
        return false;
    }

    // 古い設定は適用しない
    if (newConfig.configVersion < currentConfig.configVersion)
    {
        Serial.println("[CONFIG] Received an older configuration.");
        return false;
    }

    bool configChanged = false;

    if (newConfig.configVersion == currentConfig.configVersion)
    {
        Serial.println("[CONFIG] No configuration change.");
        return false;
    }
    else
    {
        // 新しい設定を現在の設定として反映する
        currentConfig = newConfig;
        configChanged = true;
    
        Serial.println("[CONFIG] Configuration changed.");
        Serial.print("[CONFIG] Version: ");
        Serial.println(currentConfig.configVersion);
        Serial.print("[CONFIG] Interval: ");
        Serial.print(currentConfig.intervalSeconds);
        Serial.println(" seconds");
    }

    // 未報告の適用済みバージョンを報告する
    // 失敗した場合は、次回の設定確認時に再試行する
    if (currentConfig.configVersion != lastReportedConfigVersion)
    {
        if (reportAppliedDeviceConfig(currentConfig.configVersion))
        {
            lastReportedConfigVersion = currentConfig.configVersion;
            Serial.println("[CONFIG] Applied configuration reported.");
        };
    }
    else
    {
        Serial.println("[CONFIG] Failed to report applied configuration.");
    }

    return true;
}

//==================================================
// 現在の設定の取得
//==================================================

const DeviceConfig& getCurrentDeviceConfig()
{
    return currentConfig;
}