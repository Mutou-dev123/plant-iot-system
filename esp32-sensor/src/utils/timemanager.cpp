//==================================================
// 時刻管理
// NTP同期処理および現在時刻取得処理を実装する
//==================================================

#include "time_manager.h"

#include <WiFi.h>
#include <time.h>

//==============================
// NTP設定
//==============================

constexpr const char* NTP_SERVER = "pool.ntp.org";

constexpr long GMT_OFFSET_SEC = 9 * 60 * 60;
constexpr int DAYLIGHT_OFFSET_SEC = 0;

// 前回同期した日
static int lastSyncDay = -1;

//==============================
// NTP初期化
//==============================

void initTime()
{
    syncTime();
}

//==============================
// NTP同期
//==============================

void syncTime()
{
    if (WiFi.status() != WL_CONNECTED)
    {
        return;
    }

    configTime(
        GMT_OFFSET_SEC,
        DAYLIGHT_OFFSET_SEC,
        NTP_SERVER
    );

    struct tm timeInfo;

    while (!getLocalTime(&timeInfo))
    {
        delay(500);
    }

    lastSyncDay = timeInfo.tm_mday;
}

//==============================
// 現在時刻取得
//==============================

time_t getCurrentTimestamp()
{
    return time(nullptr);
}

//==============================
// 日付変更時の再同期
//==============================

void updateTimeSync()
{
    if (WiFi.status() != WL_CONNECTED)
    {
        return;
    }

    struct tm timeInfo;

    if (!getLocalTime(&timeInfo))
    {
        return;
    }

    if (timeInfo.tm_mday != lastSyncDay)
    {
        syncTime();
    }
}