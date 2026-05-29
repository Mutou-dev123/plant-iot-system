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

# 過去N日分のデータを取得（グラフ表示用）
def load_historical_data(days):
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT timestamp, moisture, temperature, humidity
        FROM sensor_logs
        WHERE timestamp >= datetune('now', ?, 'localtime')
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(f"-{days} days",))
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])   # 時間軸として扱えるように変換
    return df

# メイン表示処理
try:
    latest = get_latest_data()
    df_history = load_historical_data(target_days)
except Exception as e:
    st.error("⚠️ データベースの接続に失敗しました。バックエンド(sensor_logger.py)が起動しているか確認してください。")
    st.stop()

if latest is not None:

    # 最終更新時刻の表示
    st.caption(f"🕒 最終データ更新時刻: {latest['timestamp']}")

    # 現在の値を表示するメーター（しきい値判定付き）
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💧 現在の土壌水分量", value=f"{latest['moisture']:.1f}%")
        if latest['moisture'] < preset['moisture_min']: st.error(preset["msg_moisture_low"])
        elif latest['moisture'] > preset["moisture_max"]: st.warning(preset["msg_moisture_high"])
        else: st.success("🌱 適切水分量です")

    with col2:
        st.metric(label="🌡️ 現在の周囲の温度", value=f"{latest['temperature']:.1f}℃")
        if latest['temperature'] > preset["temp_max"]: st.error(preset["msg_temp_high"])
        elif latest['temperature'] < preset["temp_min"]: st.warning(preset["msg_temp_low"])
        else: st.success("適切な温度です")

    with col3:
        st.metric(label="💨 現在の周囲の湿度", value=f"{latest['humidity']:.1f}%")
        if latest['humidity'] < preset['hum_min']: st.warning("🍂 乾燥しています")
        else: st.success("適切な湿度です")

    st.markdown("---")

    # 過去データの長期間グラフ表示
    if not df_history.empty:
        st.subheader(f"📈 {period} の環境推移グラフ")

        # 共通のベースチャート（Xの時間軸を固定）
        base_chart = alt.Chart(df_history).mark_line().encode(
            x=alt.X('timestamp:T', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
            tooltip=['timestamp:T', 'moisture:Q', 'temperature:Q', 'humidity:Q']
        ).properties(height=280).interactive()  # マウスで拡大・縮小・ドラッグを可能に

        g_col1, g_col2, g_col3 = st.columns(3)
        with g_col1:
            st.caption("💧 土壌水分量の推移（%）")
            chart_moist = base_chart.encode(y=alt.Y('moisture:Q', title=None, scale=alt.Scale(domain=[0, 100])), color=alt.value('#1f77b4'))
            st.altair_chart(chart_moist, use_container_width=True)

        with g_col2:
            st.caption("🌡️ 周囲の温度の推移 (℃)")
            chart_temp = base_chart.encode(y=alt.Y('temperature:Q', title=None, scale=alt.Scale(domain=[0, 40])), color=alt.value('#ff7f0e'))
            st.altair_chart(chart_temp, use_container_width=True)
    else:
        st.info("選択された期間のデータがまだデータベースにありません。")
else:
    st.info("データベースが空っぽです。バックエンドのログにデータが保存されるまでしばらくお待ちください。")