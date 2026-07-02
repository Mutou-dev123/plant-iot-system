//==================================================
// 温湿度センサー制御（ヘッダファイル）
// DHT11を利用するための関数を宣言する
//==================================================

#ifndef DHT_SENSOR_H
#define DHT_SENSOR_H

#include "../models/sensor_data.h"

// DHT11の初期化
void initDHT();

// 温湿度取得
void readDHT(SensorData &data);

#endif 