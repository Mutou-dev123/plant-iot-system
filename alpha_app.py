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
st.set_page_config(page_title="植物環境観測システム", layout="wide")
st.title("🌿 植物環境観測システム（アルファ版）")

DRY_VALUE = 0.290
WET_VALUE = 0.196
CSV_FILE = "sensor_data.csv"


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

# ADC0834から値を読み出す関数
def read_adc0834_ch0():
    cs.on()
    clk.off()
    cs.off()    # 通信開始

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

metric_placeholder = st.empty()
chart_placeholder = st.empty()

# 💡 Ctrl+Cによる強制終了を綺麗に受け止めるための try
try:
    while run_system:
        # 各センサーからデータを取得
        raw_val = read_adc0834_ch0()
        temp_val, hum_val = read_dht11()

        if temp_val is not None:
            st.session_state.last_temp = temp_val
        else:
            temp_val = st.session_state.last_temp

        if hum_val is not None:
            st.session_state.last_hum = hum_val
        else:
            hum_val = st.session_state.last_hum

        # 土壌水分を％に変換
        moisture_pct = (raw_val - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
        moisture_pct = max(0, min(100, moisture_pct))

        # 履歴データに追加
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame({
            'Time': [now],
            'Moisture': [moisture_pct],
            'Temperature': [temp_val],
            'Humidity': [hum_val]
        })
        
        # 💡 CSV保存時は小数点第1位に綺麗に丸める
        new_data[['Moisture', 'Temperature', 'Humidity']] = new_data[['Moisture', 'Temperature', 'Humidity']].astype(float).round(1)
        
        file_exists = os.path.isfile(CSV_FILE)
        new_data.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False)

        # アプリ画面の履歴データに追加（Timeだけで成形）
        display_data = new_data.copy()
        display_data['Time'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.history = pd.concat([st.session_state.history, display_data], ignore_index=True).tail(20)

        # 画面表示
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(label="💧 土壌水分量", value=f"{moisture_pct:.1f}%")
                if moisture_pct < 30.0: st.error("⚠️ 過少水分量！")
                elif moisture_pct > 80.0: st.warning("🚨 過多水分量！")
                else: st.success("🌱 適切水分量！")

            with col2:
                st.metric(label="🌡️ 周囲の温度", value=f"{temp_val:.1f}℃")
                if temp_val > 30.0: st.error("🥵 暑い！")
                elif temp_val < 15.0: st.warning("🥶 寒い！")
                else: st.success("快適温度！")

            with col3:
                st.metric(label="💨 周囲の湿度", value=f"{hum_val:.1f}%")
                if hum_val < 40.0: st.warning("🍂 乾燥！")
                else: st.success("適切湿度！")

        # グラフ表示
        with chart_placeholder.container():
            g_col1, g_col2, g_col3 = st.columns(3)

            # ベースとなるグラフの設定
            base_chart = alt.Chart(st.session_state.history).mark_line().encode(
                x=alt.X('Time:N', title=None)
            ).properties(height=250)    # グラフの高さを指定

            with g_col1:
                st.caption("📈 土壌水分量の推移 (%)")
                # グラフの目盛りを固定
                moisture_chart = base_chart.encode(
                    y=alt.Y('Moisture:Q', title=None, scale=alt.Scale(domain=[0, 100]))
                )
                st.altair_chart(moisture_chart, width='stretch')

            with g_col2:
                st.caption("📈 周囲の温度の推移（℃）")
                temp_chart = base_chart.encode(
                    y=alt.Y('Temperature:Q', title=None, scale=alt.Scale(domain=[0, 40]))
                )
                st.altair_chart(temp_chart, width='stretch')

            with g_col3:
                st.caption("📈 周囲の湿度の推移（%）")
                hum_chart = base_chart.encode(
                    y=alt.Y('Humidity:Q', title=None, scale=alt.Scale(domain=[0, 100]))
                )
                st.altair_chart(hum_chart, width='stretch')

        for _ in range(20):
            time.sleep(0.1)

except KeyboardInterrupt:
    pass