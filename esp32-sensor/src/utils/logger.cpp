//==================================================
// ログ表示
// ログでのデータ・エラー表示を行う処理を実装する
//==================================================

#include "logger.h"

#include <Arduino.h>
#include <time.h>

//==================================================
// システム異常表示
//==================================================
void printSystemAlert(
    bool isDhtError,
    bool isSoilError,
    bool isLightError
)
{
    if (!(isDhtError || isSoilError || isLightError))
    {
        return;
    }

    Serial.println();
    Serial.println("========== SYSTEM ALERT ==========");

    if (isDhtError)
    {
        Serial.println("[DHT11] Sensor read failed.");
    }

    if (isSoilError)
    {
        Serial.println("[Soil] Invalid raw value.");
    }

    if (isLightError)
    {
        Serial.println("[Light] Invalid raw value.");
    }

    Serial.println("==================================");
    Serial.println();
}

//==================================================
// NTP時刻表示
//==================================================
void printTimeLog(time_t timestamp)
{
    struct tm timeinfo;

    if (localtime_r(&timestamp, &timeinfo))
    {
        char buffer[32];

        strftime(
            buffer,
            sizeof(buffer),
            "%Y-%m-%d %H:%M:%S",
            &timeinfo
        );

        Serial.println("========== TIME ==========");
        Serial.print("Measured At : ");
        Serial.println(buffer);
    }
    else
    {
        Serial.println("========== TIME ==========");
        Serial.println("Measured At : Invalid");
    }

    Serial.println();
}

//==================================================
// センサーデータ表示
//==================================================
void printSensorLog(
    const SensorData& data,
    bool isDhtError,
    bool isSoilError,
    bool isLightError
)
{
    Serial.println("======= SENSOR DATA =======");

    // 温度
    if (isDhtError)
    {
        Serial.println("Temperature : ERROR");
        Serial.println("Humidity    : ERROR");
    }
    else
    {
        Serial.printf("Temperature : %.1f C\n", data.temperature);
        Serial.printf("Humidity    : %.1f %%\n", data.humidity);
    }

    // 土壌水分
    if (isSoilError)
    {
        Serial.printf("Soil Raw    : %d [ERROR]\n", data.soilRaw);
    }
    else
    {
        Serial.printf("Soil Raw    : %d\n", data.soilRaw);
    }

    // 光量
    if (isLightError)
    {
        Serial.printf("Light Raw   : %d [ERROR]\n", data.lightRaw);
    }
    else
    {
        Serial.printf("Light Raw   : %d\n", data.lightRaw);
    }

    Serial.println("===========================");
    Serial.println();
}

//==================================================
// HTTP通信ログ
//==================================================
void printNetworkLog(
    int httpCode,
    int nextInterval
)
{
    Serial.println("====== HTTP RESULT ======");

    Serial.print("HTTP Code   : ");
    Serial.println(httpCode);

    if (httpCode >= 200 && httpCode < 300)
    {
        Serial.println("Status      : Success");

        Serial.print("Next Interval : ");
        Serial.print(nextInterval);
        Serial.println(" sec");
    }
    else
    {
        Serial.println("Status      : Failed");
    }

    Serial.println("=========================");
    Serial.println();
}