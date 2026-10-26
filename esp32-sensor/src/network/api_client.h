//==================================================
// API通信（ヘッダファイル）
// JSON変換およびHTTP通信を行うための関数を宣言する
//==================================================

#ifndef API_CLIENT_H
#define API_CLIENT_H

#include "../models/sensor_data.h"

/**
 * @brief センサーデータをJSON形式に変換し、HTTP POSTで送信する
 *
 * @param data センサーデータ
 * @return 0より大きい値 次回の計測間隔（秒）
 * @return -1 送信失敗
 */
int sendSensorData(const SensorData& data);

#endif