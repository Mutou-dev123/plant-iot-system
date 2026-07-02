//==================================================
// DHT11センサー制御（ヘッダファイル）
// DHT11を利用するための関数を宣言する
//==================================================

#ifndef DHT_SENSOR_H
#define DHT_SENSOR_H

// DHT11の初期化
void initDHT();

// 温度を取得
float getTemperature();

// 湿度を取得
float getHumidity();

#endif 