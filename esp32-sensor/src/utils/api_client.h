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
 * @return true 送信成功
 * @return false 送信失敗
 */
bool sendSensorData(const SensorData& data);

#endif