# 最終版バックエンドコード

import sqlite3
import time
from datetime import datetime
from gpiozero import OutputDevice, InputDevice
import adafruit_dht
import board

# 設定項目
DB_FILE = "sensor_data.db"

# キャリブレーション値
DRY_VALUE = 0.278
WET_VALUE = 0.152

# センサー初期化
cs = OutputDevice(8)    # ラズパイ 24番ピン
clk = OutputDevice(11)  # ラズパイ 23番ピン
di = OutputDevice(10)   # ラズパイ 19番ピン
do = InputDevice(9)     # ラズパイ 21番ピン
dht_device = adafruit_dht.DHT11(board.D4) # ラズパイ 7番ピン

# SQLiteデータベースとテーブルがなければ作成する関数
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ログ用テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            moisture REAL NOT NULL,
            temperature REAL,
            humidity REAL
        )
    """)

    # 設定用テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY,
            interval_seconds INTEGER NOT NULL
        )
    """)
    
    # 初期値（5分 = 300秒）がなければ挿入
    cursor.execute("INSERT OR IGNORE INTO system_settings (id, interval_seconds) VALUES (1, 300)")

    conn.commit()
    conn.close()

# DBから現在の計測間隔を読み出す関数
def get_current_interval():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT interval_seconds FROM system_settings WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 300
    except Exception:
        return 300  # エラー時は5分に設定

# ADC0834から生データを読み出す
def read_adc0834_ch0():
    cs.on()
    clk.off()
    cs.off()

    config_bits = [1, 1, 0, 0]
    for bit in config_bits:
        di.value = bit
        clk.on()
        clk.off()
    
    clk.on()
    clk.off()

    raw_value = 0
    for _ in range(8):
        clk.on()
        clk.off()
        raw_value = (raw_value << 1) | int(do.value)

    cs.on()
    return raw_value / 255.0

# DHT11から温湿度を読み出す（失敗時はNoneを返す）
def read_dht11():
    try:
        temp = dht_device.temperature
        hum = dht_device.humidity
        return temp, hum
    except Exception:
        return None, None

def main():
    print("🚀 植物環境データ収集システム（バックエンド）を起動しました...")
    init_db()

    # 前回の値を保持する変数
    last_temp = 25.0
    last_hum = 50.0

    while True:
        try:
            # センサーデータ取得
            raw_val = read_adc0834_ch0()
            temp_val, hum_val = read_dht11()

            # DHT11がエラーだった場合の処理
            if temp_val is not None:
                last_temp = temp_val
            else:
                temp_val = last_temp    # 読み取り失敗時は前回の値を使用

            if hum_val is not None:
                last_hum = hum_val
            else:
                hum_val = last_hum

            # 土壌水分量を％に変換
            moisture_pct = (raw_val - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
            moisture_pct = round(max(0, min(100, moisture_pct)), 1)

            # データベース保存
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_logs (timestamp, moisture, temperature, humidity)
                VALUES (?, ?, ?, ?)
            """, (now, moisture_pct, temp_val, hum_val))
            conn.commit()
            conn.close()

            print(f"[{now}] 保存成功 -> 水分: {moisture_pct}%, 気温: {temp_val}℃, 湿度: {hum_val}%")

        except Exception as e:
            print(f"⚠️ 予期せぬエラーが発生しました（自動復帰します）: {e}")

        # 1秒ごとにDBをチェックし、設定が変わったらすぐ追従するループ
        elapsed = 0
        while True:
            current_interval = get_current_interval()
            if elapsed >= current_interval:
                break   # 設定された時間が経過したので次の計測へ
            time.sleep(1)
            elapsed += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 システムを安全に終了しました。")