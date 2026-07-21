//==================================================
// LED制御（ヘッダファイル）
// LEDを制御するための関数を宣言する
//==================================================

#ifndef LED_INDICATOR_H
#define LED_INDICATOR_H

#include <Arduino.h>

// LEDの初期化
void initLEDs();

// LEDの状態を更新
// 今後RTCを導入の可能性あり
void updateLEDs(unsigned long currentMillis, unsigned long lastReadTime, bool isDhtError, bool isSoilError, bool isLightError);

#endif