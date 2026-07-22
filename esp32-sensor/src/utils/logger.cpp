//==================================================
// ログ表示
// ログでのセンサーデータ・エラー表示を行う処理を実装する
//==================================================

#include "logger.h"

#include "../models/sensor_data.h"

void printSensorLog(const SensorData& data, bool isDhtError, bool isSoilError, bool isLightError)
{
    //==============================
    // エラー警告
    //==============================
    if (isDhtError || isSoilError || isLightError)
    {
        Serial.println("\n[⚠️ SYSTEM ALERT] 異常を検知しました");
        
        if (isDhtError) {
            Serial.println("❌ 【温湿度センサー】データの取得に失敗しました。");
            Serial.println("   ➡ 原因の可能性: センサーの故障、またはピン（D13）の接触不良・ワイヤー抜け");
        }

        if (isSoilError) {
            Serial.println("❌ 【土壌水分センサー】異常値（0または4095）を検知しました。");
            Serial.println("   ➡ 原因の可能性: ワイヤーの脱落（0V）、または水濡れによるショート（3.3V）");
        }

        if (isLightError) {
            Serial.println("❌ 【光量センサー】異常値（0または4095）を検知しました。");
            Serial.println("   ➡ 原因の可能性: ワイヤーの脱落（0V）、またはショート（3.3V）");
        }

        Serial.println("------------------------------------------------");
    }

    //==============================
    // データ表示
    //==============================

    Serial.printf("Timestamp    : %lu ms\n", data.timestamp);
    
    // 温湿度
    if (isDhtError) {
        Serial.println("Temperature  : [ERROR]");
        Serial.println("Humidity     : [ERROR]");
    } else {
        Serial.printf("Temperature  : %.1f ℃\n", data.temperature);
        Serial.printf("Humidity     : %.1f %%\n", data.humidity);
    }

    // 土壌水分（エラー時でもデータを表示する）
    if (isSoilError) {
        Serial.printf("Soil Raw     : %d [ERROR]\n", data.soilRaw);
    } else {
        Serial.printf("Soil Raw     : %d \n", data.soilRaw);
    }

    // 光量（エラー時でもデータを表示する）
    if (isLightError) {
        Serial.printf("Light Raw    : %d [ERROR]\n", data.lightRaw);
    } else {
        Serial.printf("Light Raw    : %d\n", data.lightRaw);
    }

    Serial.println("========================");
}