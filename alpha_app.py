# 植物環境観測システム（α版）

import streamlit as st
from gpiozero import OutputDevice, InputDevice
import time
import pandas as pd
from datetime import datetime
import os
import altair as alt

import adafruit_dht
import board

# ページ設定
st.set_page_config(page_title="植物環境観測システム（α版）", layout="wide")
st.title("🌿 植物環境観測システム（α版）")

# 温湿度計と温湿度センサーの値差
TEMP_OFFSET = 1.6
HUMIDITY_OFFSET = 4.5

# 土壌水分量 0% の限界値（空気中）
DRY_VALUE = 0.529
# 土壌水分量 100% の限界値（泥水）
WET_VALUE = 0.333

CSV_FILE = "sensor_data.csv"

# 状態記憶
if "last_status" not in st.session_state:
    st.session_state.last_status = "OK"

# 一瞬のノイズを防ぐためのカウンター
if "dry_count" not in st.session_state:
    st.session_state.dry_count = 0

# 世代管理センサー
if "generation" not in st.session_state:
    st.session_state.generation = 0
st.session_state.generation += 1
my_generation = st.session_state.generation

@st.cache_resource
def init_sensors():
    return {
        "cs": OutputDevice(8),    # ラズパイ 24番ピン（GPIO 8）
        "clk": OutputDevice(11),  # ラズパイ 23番ピン（GPIO 11）
        "di": OutputDevice(10),   # ラズパイ 19番ピン（GPIO 10）
        "do": InputDevice(9),     # ラズパイ 21番ピン（GPIO 9）
        "dht": adafruit_dht.DHT11(board.D4)
    }

try:
    sensors = init_sensors()
    cs, clk, di, do = sensors["cs"], sensors["clk"], sensors["di"], sensors["do"]
    dhtDevice = sensors["dht"]
    st.sidebar.success("✅ すべてのセンサー 初期化完了")
except Exception as e:
    st.sidebar.error(f"❌ 初期化エラー: {e}")
    st.stop()

# デバッグ用スイッチ
show_raw = st.sidebar.toggle("🛠️ デバッグ用に生データを表示する", value=False)

# 任意取得間隔の設定
st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ 計測間隔のカスタマイズ")
time_unit = st.sidebar.radio("時間の単位を選択", ["秒（実験・デモ用）", "分（本番運用）"], index=0)

if "秒" in time_unit:
    input_value = st.sidebar.number_input("間隔を「秒」で入力してください", min_value=2, max_value=300, value=2, step=1)
    interval_seconds = float(input_value)
else:
    input_value = st.sidebar.number_input("間隔を「分」で入力してください", min_value=1, max_value=60, value=5, step=1)
    interval_seconds = float(input_value * 60)

st.sidebar.caption(f"現在の設定: {interval_seconds} 秒 ごとに計測します。")
st.sidebar.markdown("---")

# ADC0834から値を読み出す関数
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

# DHT11から値を読み出す関数
def read_dht11():
    try:
        temp = dhtDevice.temperature
        hum = dhtDevice.humidity
        return temp, hum
    except Exception:
        return None, None

run_system = st.toggle("センサー計測を開始する", value=True)

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame({
        'Time': pd.Series(dtype='str'),
        'Moisture': pd.Series(dtype='float'),
        'Temperature': pd.Series(dtype='float'),
        'Humidity': pd.Series(dtype='float')
    })

if 'last_temp' not in st.session_state:
    st.session_state.last_temp = 25.0
if 'last_hum' not in st.session_state:
    st.session_state.last_hum = 50.0

# 上書き用のプレースホルダー
metric_placeholder = st.empty()
chart_placeholder = st.empty()
raw_placeholder = st.empty()

try:
    while run_system:
        if st.session_state.generation != my_generation:
            break

        # 各センサーからデータを取得
        raw_val = read_adc0834_ch0()
        temp_val, hum_val = read_dht11()

        # データが取れた時だけ補正して、記憶を更新
        if temp_val is not None:
            calibrated_temp = round(temp_val - TEMP_OFFSET, 1)
            st.session_state.last_temp = calibrated_temp
        else:
            # エラーの時は、前回の正常な補正値を身代わりにする
            calibrated_temp = st.session_state.last_temp

        if hum_val is not None:
            calibrated_hum = round(hum_val - HUMIDITY_OFFSET, 1)
            st.session_state.last_hum = calibrated_hum
        else:
            calibrated_hum = st.session_state.last_hum

        # 土壌水分を％に変換（計算式完璧です！）
        moisture_pct = (raw_val - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
        moisture_pct = max(0, min(100, moisture_pct))

        # 履歴データに追加
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame({
            'Time': [now],
            'Moisture': [moisture_pct],
            'Temperature': [calibrated_temp],
            'Humidity': [calibrated_hum]
        })
        
        new_data[['Moisture', 'Temperature', 'Humidity']] = new_data[['Moisture', 'Temperature', 'Humidity']].astype(float).round(1)
        
        file_exists = os.path.isfile(CSV_FILE)
        new_data.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False)

        display_data = new_data.copy()
        display_data['Time'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.history = pd.concat([st.session_state.history, display_data], ignore_index=True).tail(20)

        # 風船を上げるか判定する
        trigger_balloons = False
        if moisture_pct >= 30.0 and st.session_state.last_status == "DRY":
            trigger_balloons = True
            st.session_state.last_status = "OK"
            st.session_state.dry_count = 0
        
        if moisture_pct < 30.0:
            st.session_state.dry_count += 1

            # センサー移動時などの際の誤作動を防ぐため、土壌水分量が30.0%未満に2回以上になったら乾燥状態に設定
            if st.session_state.dry_count >= 2:
                st.session_state.last_status = "DRY"
        else:
            if not trigger_balloons:
                st.session_state.last_status = "OK"
                st.session_state.dry_count = 0

        # 状態にい応じたメッセージ表示
        metric_placeholder.empty()
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)

            # 土壌水分量
            with col1:
                st.metric(label="💧 土壌水分量", value=f"{moisture_pct:.1f}%")
                if moisture_pct < 30.0: st.error("⚠️ 水が少なすぎます！")
                elif moisture_pct > 80.0: st.warning("🚨 水が多すぎます！")
                else: st.success("🌱 適切な水分量です！")

            # 温度
            with col2:
                st.metric(label="🌡️ 周囲の温度", value=f"{calibrated_temp:.1f}℃")
                if calibrated_temp > 30.0: st.error("🥵 暑すぎます！")
                elif calibrated_temp < 15.0: st.error("🥶 寒すぎます！")
                else: st.success("快適な温度です！")

            # 湿度
            with col3:
                st.metric(label="💨 周囲の湿度", value=f"{calibrated_hum:.1f}%")
                if calibrated_hum < 40.0: st.warning("🍂 乾燥しています！")
                else: st.success("適切な湿度です！")

        # グラフ表示
        chart_placeholder.empty()
        with chart_placeholder.container():
            g_col1, g_col2, g_col3 = st.columns(3)
            base_chart = alt.Chart(st.session_state.history).mark_line().encode(x=alt.X('Time:N', title=None)).properties(height=250)

            # 土壌水分量
            with g_col1:
                st.caption("📈 土壌水分量の推移 (%)")
                st.altair_chart(base_chart.encode(y=alt.Y('Moisture:Q', title=None, scale=alt.Scale(domain=[0, 100]))), width='stretch')

            # 温度
            with g_col2:
                st.caption("📈 周囲の温度の推移（℃）")
                st.altair_chart(base_chart.encode(y=alt.Y('Temperature:Q', title=None, scale=alt.Scale(domain=[0, 40]))), width='stretch')

            # 湿度
            with g_col3:
                st.caption("📈 周囲の湿度の推移（%）")
                st.altair_chart(base_chart.encode(y=alt.Y('Humidity:Q', title=None, scale=alt.Scale(domain=[0, 100]))), width='stretch')

        # 風船を上げる
        if trigger_balloons:
            st.balloons()   # 風船
            st.toast("🎉 乾燥状態から復活しました！")

        raw_placeholder.empty()
        if show_raw:
            with raw_placeholder.container():
                st.markdown("---")
                st.caption("⚙️ 管理用リアルタイム生データ（Raw Data）")
                r_col1, r_col2, r_col3 = st.columns(3)
                with r_col1:
                    st.text(f"土壌水分(ADC比): {raw_val:.4f}")
                with r_col2:
                    st.text(f"温度(生値): {temp_val} ℃") # None対策の前の本当の生値
                with r_col3:
                    st.text(f"湿度(生値): {hum_val} %")
        else:
            raw_placeholder.empty() # スイッチがオフなら完全消去

        loop_count = int(interval_seconds / 0.1)
        interrupted = False
        for _ in range(loop_count):
            time.sleep(0.1)
            if st.session_state.generation != my_generation:
                interrupted = True
                break
        if interrupted:
            break
    

except KeyboardInterrupt:
    pass

else:
    st.warning("⏸️ センサー計測は停止しています。")