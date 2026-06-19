# ==============================
#       バックエンド
# ==============================

# ここでは土壌水分、温湿度センサーからデータを取得、DBに保存するところまで行う

import time
from datetime import datetime
from gpiozero import OutputDevice, InputDevice
import adafruit_dht
import board

# Djangoを外部スクリプトから呼び出す
import os
import sys
import django

# このファイルの場所を基準に、plant_projectフォルダへのパスを通す
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_DIR = os.path.join(BASE_DIR, 'plant_project')
sys.path.append(DJANGO_DIR)

# Djangoの設定ファイルを指定して起動
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_project.settings')
django.setup()

# Djangoのモデル読み込み
from dashboard.models import SensorLogs, SystemSettings

# キャリブレーション値
DRY_VALUE = 0.9608
WET_VALUE = 0.3216

# DHT11の仕様上の測定誤差（参考値）
# 温度：±2℃程度
# 湿度：±5%RH程度

# DHT22へのアップグレードも考える

# 温湿度の補正値（センサーの生の値から引く数字）
TEMP_OFFSET = 1.3
HUMIDITY_OFFSET = 7.0

# センサー初期化
cs = OutputDevice(8)    # ラズパイ 24番ピン
clk = OutputDevice(11)  # ラズパイ 23番ピン
di = OutputDevice(10)   # ラズパイ 19番ピン
do = InputDevice(9)     # ラズパイ 21番ピン
dht_device = adafruit_dht.DHT11(board.D4) # ラズパイ 7番ピン

# DBから現在の計測間隔を読み出す関数（Djangoモデル経由）
def get_current_interval():
    try:
        setting = SystemSettings.objects.filter(id=1).first()
        if setting:
            return setting.interval_seconds
        else:
            SystemSettings.objects.create(id=1, interval_seconds=300)
            return 300
    except Exception:
        return 300

# 土壌水分量をADコンバータから取得する関数  
def read_adc0834_ch0():

    # コンバータを叩き起こす
    cs.on()
    clk.off()
    cs.off()

    # CH0（チャンネル0）のピンの土壌水分量を図る
    # ADC0834では 1, 1, 0, 0 の順序で信号を送れば CH0 を測れる
    config_bits = [1, 1, 0, 0]
    for bit in config_bits:
        di.value = bit
        clk.on()
        clk.off()

    # ダミークロック
    clk.on()
    clk.off()

    # 結果を受け取る
    raw_value = 0
    for _ in range(8):
        clk.on()
        clk.off()
        raw_value = (raw_value << 1) | int(do.value)

    cs.on()
    return raw_value / 255.0

# 温湿度センサー（DHT11）からデータを読み取る関数
def read_dht11():
    try:
        temp = dht_device.temperature
        hum = dht_device.humidity
        return temp, hum
    except Exception:
        return None, None

# ==============================
#       メイン処理
# ==============================
def main():
    print("🚀 植物環境データ収集システム（Django統合版）を起動しました...")

    last_temp = 25.0
    last_hum = 50.0

    while True:
        try:
            raw_val = read_adc0834_ch0()
            temp_val, hum_val = read_dht11()

            # 温湿度が取得できなかった場合、それぞれ前回の正常値を使用する
            if temp_val is not None:
                last_temp = temp_val
            else:
                temp_val = last_temp

            if hum_val is not None:
                last_hum = hum_val
            else:
                hum_val = last_hum

            # 土壌水分量を％に変換
            print(raw_val)
            moisture_pct = (raw_val - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
            moisture_pct = round(max(0, min(100, moisture_pct)), 1)

            # データ取得日時を記録
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Djangoのモデルに直接保存する
            SensorLogs.objects.create(
                timestamp=now,
                moisture=moisture_pct,
                temperature=temp_val,
                humidity=hum_val
            )

            # 保存処理成功時のログ表示
            print(f"[{now}] 保存成功 -> 水分: {moisture_pct}%, 気温: {temp_val}℃, 温度: {hum_val}%")

        except Exception as e:

            # 保存処理失敗時のログ表示
            print(f"⚠️ 予期せぬエラーが発生しました: {e}")

        elapsed = 0

        # 計測間隔設定変更監視ループ
        while True:
            current_interval = get_current_interval()
            if elapsed >= current_interval:
                break
            time.sleep(1)
            elapsed += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 システムを安全に終了しました。")

    except Exception as e:
        print(f"\n💥 予期せぬエラーで停止しました: {e}")

    finally:

        # GPIO busy対策
        print("🧹 GPIOピンのロックを解除（クリーンアップ）しています...")
        try:
            cs.close()
            clk.close()
            di.close()
            do.close()
            dht_device.exit()
            print("✨ クリーンアップ完了！ピンは無事にOSへ返却されました。")
        except Exception as cleanup_error:
            print("⚠️ クリーンアップ中にエラーが出ましたが、終了を優先します: {cleanup_error}")