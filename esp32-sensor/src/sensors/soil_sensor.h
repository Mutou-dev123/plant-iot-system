//==================================================
// 土壌水分センサー制御（ヘッダファイル）
// Capacitive Soil Moisture Sensor V1.2を利用するための関数を宣言する
//==================================================

#ifndef SOIL_SENSOR_H
#define SOIL_SENSOR_H

// 土壌水分センサー初期化
void initSoilSensor();

// 土壌水分値取得
int getSoilMoisture();

#endif