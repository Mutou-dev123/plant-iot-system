//==================================================
// デバイス設定管理（ヘッダファイル）
//
// Raspberry Piから取得したデバイス設定を管理し、
// 設定確認のタイミングと設定変更の判定を行う。
//==================================================

#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include "../network/api_client.h"

// 設定管理を初期化する
void initConfigManager();

// 指定された時刻に設定確認を行うべきか判定する
bool shouldCheckDeviceConfig(unsigned long currentMillis);

// Raspberry Piから設定を取得し、変更があれば反映する
bool updateDeviceConfig();

// 現在適用されている設定を取得する
const DeviceConfig& getCurrentDeviceConfig();

#endif