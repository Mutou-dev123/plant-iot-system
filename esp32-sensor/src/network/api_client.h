//==================================================
// API通信（ヘッダファイル）
// JSON変換およびHTTP通信を行うための関数を宣言する
//==================================================

#ifndef API_CLIENT_H
#define API_CLIENT_H

#include "../models/sensor_data.h"

/**
 * @brief Raspberry Piから取得したデバイス設定
 */
struct DeviceConfig
{
    int configVersion;
    int intervalSeconds;
    bool dhtEnabled;
    bool soilEnabled;
    bool lightEnabled;
};

/**
 * @brief センサーデータをJSON形式に変換し、HTTP POSTで送信する
 */
int sendSensorData(const SensorData& data);

/**
 * @brief Raspberry Piから最新のデバイス設定を取得する
 * 
 * 全項目が正しい場合だけconfigへ書き込む
 * 
 * @param config 取得した設定の格納先
 * @return true 設定の取得・検証に成功
 * @return false 通信失敗または不正なレスポンス
 */
bool fetchDeviceConfig(DeviceConfig& config);

#endif