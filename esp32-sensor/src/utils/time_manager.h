//==================================================
// 時刻管理（ヘッダファイル）
// NTP同期および現在時刻の取得するための関数を宣言する
//==================================================

#ifndef TIME_MANAGER_H
#define TIME_MANAGER_H

#include <Arduino.h>
#include <time.h>

// 起動時の時刻初期化
void initTime();

// NTPと再同期
void syncTime();

// 現在時刻取得（Unix Time）
time_t getCurrentTimestamp();

// 日付変更時の再同期判定
void updateTimeSync();

#endif