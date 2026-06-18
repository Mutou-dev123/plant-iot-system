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
st.title("🌿 植物環境観測システム（ベータ版への進化）")

DRY_VALUE = 0.290
WET_VALUE = 0.196
CSV_FILE = "sensor_data.csv"

# =================================================================
# 作物のしきい値・メッセージのマスターデータ
# =================================================================
CROP_PRESETS = {
    "🌱 ラディッシュ (ハツカダイコン)": {
        "moisture_min": 30.0, "moisture_max": 65.0,
        "temp_min": 15.0, "temp_max": 25.0,
        "hum_min": 40.0,
        "msg_moisture_low": "⚠️ 乾燥気味です！根が育つようにお水を。",
        "msg_moisture_high": "🚨 水多すぎ！根割れ（破裂）の原因になります",
        "msg_temp_low": "🥶 寒すぎ（15℃未満）。成長が遅れるかも",
        "msg_temp_high": "🥵 暑すぎ（25℃超え）。病気に注意して"
    },
    "🥬 レタス (室内栽培)": {
        "moisture_min": 40.0, "moisture_max": 75.0,
        "temp_min": 15.0, "temp_max": 20.0,
        "hum_min": 50.0,
        "msg_moisture_low": "⚠️ カラカラです！レタスは乾燥に弱いのでお水を。",
        "msg_moisture_high": "🚨 水多すぎ！室内は風が通らないので根腐れ注意",
        "msg_temp_low": "🥶 15℃未満です。少し暖かい場所へ",
        "msg_temp_high": "🥵 20℃超えはレタスには暑すぎます！葉が苦くなるかも"
    },
    "🪴 汎用モード (基本設定)": {
        "moisture_min": 30.0, "moisture_max": 80.0,
        "temp_min": 15.0, "temp_max": 30.0,
        "hum_min": 40.0,
        "msg_moisture_low": "⚠️ 過少水分量！",
        "msg_moisture_high": "🚨 過多水分量！",
        "msg_temp_low": "🥶 寒い！",
        "msg_temp_high": "🥵 暑い！"
    }
}

# サイドバーで作物を選べるようにする
selected_crop = st.sidebar.selectbox("📋 栽培する植物を選択", list(CROP_PRESETS.keys()))
preset = CROP_PRESETS[selected_crop] # 選ばれた植物のしきい値データを取得


@st.cache_resource
def init_sensors():
    return {
        "cs": OutputDevice(8),
        "clk": OutputDevice(11),
        "di": OutputDevice(10),
        "do": InputDevice(9),
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

try:
    while run_system:
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

        moisture_pct = (raw_val - DRY_VALUE) / (WET_VALUE - DRY_VALUE) * 100
        moisture_pct = max(0, min(100, moisture_pct))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame({
            'Time': [now],
            'Moisture': [moisture_pct],
            'Temperature': [temp_val],
            'Humidity': [hum_val]
        })
        
        new_data[['Moisture', 'Temperature', 'Humidity']] = new_data[['Moisture', 'Temperature', 'Humidity']].astype(float).round(1)
        
        file_exists = os.path.isfile(CSV_FILE)
        new_data.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False)

        display_data = new_data.copy()
        display_data['Time'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.history = pd.concat([st.session_state.history, display_data], ignore_index=True).tail(20)

        # 画面表示
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(label="💧 土壌水分量", value=f"{moisture_pct:.1f}%")
                if moisture_pct < preset["moisture_min"]: 
                    st.error(preset["msg_moisture_low"])
                elif moisture_pct > preset["moisture_max"]: 
                    st.warning(preset["msg_moisture_high"])
                else: 
                    st.success("🌱 適切水分量です")

            with col2:
                st.metric(label="🌡️ 周囲の温度", value=f"{temp_val:.1f}℃")
                if temp_val > preset["temp_max"]: 
                    st.error(preset["msg_temp_high"])
                elif temp_val < preset["temp_min"]: 
                    st.warning(preset["msg_temp_low"])
                else: 
                    st.success("快適温度です")

            with col3:
                st.metric(label="💨 周囲の湿度", value=f"{hum_val:.1f}%")
                if hum_val < preset["hum_min"]: 
                    st.warning("🍂 乾燥しています")
                else: 
                    st.success("適切な湿度です")

        # グラフ表示
        with chart_placeholder.container():
            g_col1, g_col2, g_col3 = st.columns(3)
            
            base_chart = alt.Chart(st.session_state.history).mark_line().encode(
                x=alt.X('Time:N', title=None)
            ).properties(height=250)

            with g_col1:
                st.caption("📈 土壌水分量の推移 (%)")
                moisture_chart = base_chart.encode(
                    y=alt.Y('Moisture:Q', title=None, scale=alt.Scale(domain=[0, 100]))
                )
                st.altair_chart(moisture_chart, width='stretch')
                
            with g_col2:
                st.caption("📈 周囲の温度の推移 (℃)")
                temp_chart = base_chart.encode(
                    y=alt.Y('Temperature:Q', title=None, scale=alt.Scale(domain=[0, 40]))
                )
                st.altair_chart(temp_chart, width='stretch')
                
            with g_col3:
                st.caption("📈 周囲の湿度の推移 (%)")
                hum_chart = base_chart.encode(
                    y=alt.Y('Humidity:Q', title=None, scale=alt.Scale(domain=[0, 100]))
                )
                st.altair_chart(hum_chart, width='stretch')

        for _ in range(20):
            time.sleep(0.1)

except KeyboardInterrupt:
    pass