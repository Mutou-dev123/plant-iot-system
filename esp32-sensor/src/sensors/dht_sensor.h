//==================================================
// 温湿度センサー制御（ヘッダファイル）
// DHTを利用するための関数を宣言する
//==================================================

#ifndef DHT_SENSOR_H
#define DHT_SENSOR_H

#include "../models/sensor_data.h"

// DHTの初期化
void initDHT();

// 温湿度取得
void readDHT(SensorData &data);

#endif 