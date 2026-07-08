//==================================================
// ログ表示（ヘッダファイル）
// ログでのデータ・エラー表示するための関数を宣言する
//==================================================

#ifndef LOGGER_H
#define LOGGER_H

#include <Arduino.h>
#include "../models/sensor_data.h"

// センサーデータとエラー状態からログを出力
void printSensorLog(const SensorData& data, bool isDhtError, bool isSoilError, bool isLightError);

#endif