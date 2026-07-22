//==================================================
// ログ表示（ヘッダファイル）
// ログでのデータ・エラー表示するための関数を宣言する
//==================================================

#ifndef LOGGER_H
#define LOGGER_H

#include "../models/sensor_data.h"

// システム異常表示
void printSystemAlert(
    bool isDhtError,
    bool isSoilError,
    bool isLightError
);

// センサーデータ表示
void printSensorLog(
    const SensorData& data,
    bool isDhtError,
    bool isSoilError,
    bool isLightError
);

// NTPログ
void printTimeLog(time_t timestamp);

// HTTP通信ログ
void printNetworkLog(
    int httpCode,
    int nextInterval
);

#endif