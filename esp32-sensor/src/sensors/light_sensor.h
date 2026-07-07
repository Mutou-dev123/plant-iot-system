//==================================================
// 光量センサー制御（ヘッダファイル）
// フォトレジスタモジュールの制御関数を宣言する
//==================================================

#ifndef LIGHT_SENSOR_H
#define LIGHT_SENSOR_H

#include "../models/sensor_data.h"

// 光量センサー初期化
void initLightSensor();

// 光量取得
void readLight(SensorData &data);

#endif