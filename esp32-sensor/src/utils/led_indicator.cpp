//==================================================
// LED制御
// LED制御を行う処理を実装する
//==================================================

#include "led_indicator.h"

#include "../config/pin_config.h"

// 起動時のLED演出
void initLEDs()
{
    pinMode(LED_DHT, OUTPUT);
	pinMode(LED_SOIL, OUTPUT);
	pinMode(LED_LIGHT, OUTPUT);

    // 起動完了サインとして3回素早く同時点滅
    for (int i = 0; i < 3; i++) {
		digitalWrite(LED_DHT, HIGH);
		digitalWrite(LED_SOIL, HIGH);
		digitalWrite(LED_LIGHT, HIGH);
		delay(100);
		digitalWrite(LED_DHT, LOW);
		digitalWrite(LED_SOIL, LOW);
		digitalWrite(LED_LIGHT, LOW);
		delay(100);
	}
}

// LED制御
void updateLEDs(unsigned long currentMillis, unsigned long lastReadTime, bool isDhtError, bool isSoilError, bool isLightError)
{
    // ハートビートで光る時間（100ms）
    const unsigned long FLASH_TIME = 100;

    // データ取得直後に100msだけtrueになるフラグ
	bool isHeartbeat = (currentMillis - lastReadTime < FLASH_TIME);

	// --- 温湿度（緑色）の制御 ---
	digitalWrite(LED_DHT, isDhtError ? HIGH : (isHeartbeat ? HIGH : LOW));

	// --- 土壌水分（青色）の制御 ---
	digitalWrite(LED_SOIL, isSoilError ? HIGH : (isHeartbeat ? HIGH : LOW));

	// --- 光量（黄色）の制御 ---
	digitalWrite(LED_LIGHT, isLightError ? HIGH : (isHeartbeat ? HIGH : LOW));
}

