# 最終版フロントエンドコード

import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime

# ページ設定
st.set_page_config(page_title="植物環境観測システム", layout="wide")
st.title("🌿 植物環境観測システム（最終版）")

DB_FILE = "sensor_data.db"

# 植物別しきい値マスター
CROP_PRESETS = {
    "🌱 ラディッシュ (ハツカダイコン)": {
        "moisture_min": 30.0, "moisture_max": 65.0, "temp_min": 15.0, "temp_max": 25.0, "hum_min": 40.0,
        "msg_moisture_low": "⚠️ 乾燥気味です！根が育つようにお水を。",
        "msg_moisture_high": "🚨 水多すぎ！根割れ（破裂）の原因になります",
        "msg_temp_low": "🥶 寒すぎ（15℃未満）。成長が遅れるかも",
        "msg_temp_high": "🥵 暑すぎ（25℃超え）。病기에注意して"
    },
    "🥬 レタス (室内栽培)": {
        "moisture_min": 40.0, "moisture_max": 75.0, "temp_min": 15.0, "temp_max": 20.0, "hum_min": 50.0,
        "msg_moisture_low": "⚠️ カラカラです！レタスは乾燥に弱いのでお水を。",
        "msg_moisture_high": "🚨 水多すぎ！室内は風が通らないので根腐れ注意",
        "msg_temp_low": "🥶 15℃未満です。少し暖かい場所へ",
        "msg_temp_high": "🥵 20℃超えはレタスには暑すぎます！葉が苦くなるかも"
    },
    "🪴 汎用モード (基本設定)": {
        "moisture_min": 30.0, "moisture_max": 80.0, "temp_min": 15.0, "temp_max": 30.0, "hum_min": 40.0,
        "msg_moisture_low": "⚠️ 過少水分量！", "msg_moisture_high": "🚨 過多水分量！",
        "msg_temp_low": "🥶 寒い！", "msg_temp_high": "🥵 暑い！"
    }
}

# サイドバー設定
st.sidebar.header("⚙️ システム設定")
selected_crop = st.sidebar.selectbox("📋 栽培する植物を選択", list(CROP_PRESETS.keys()))
preset = CROP_PRESETS[selected_crop]

# 表示期間の選択
period = st.sidebar.radio("📊 表示期間を選択", ["今日（24時間）", "過去 3日間", "過去 1週間"])
days_map = {"今日（24時間）": 1, "過去 3日間": 3, "過去 1週間": 7}
target_days = days_map[period]

# 最新状態への更新ボタン
if st.sidebar.button("🔄 最新データに更新"):
    st.rerun()

# データベースからのデータ読込関数
def get_latest_data():

    # 最新1件を取得（現在のメーター表示用）
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT moisture, temperature, humidity, timestamp FROM sensor_logs ORDER BY id DESC LIMIT 1"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else None