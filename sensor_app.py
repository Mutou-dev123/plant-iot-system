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
    "🪴 汎用モード (基本設定)": {
        "moisture_min": 30.0, "moisture_max": 80.0, "temp_min": 15.0, "temp_max": 30.0, "hum_min": 40.0,
        "msg_moisture_low": "⚠️ 過少水分量！", "msg_moisture_high": "🚨 過多水分量！",
        "msg_temp_low": "🥶 寒い！", "msg_temp_high": "🥵 暑い！"
    },
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
}

# 計測間隔マスタ
INTERVAL_OPTIONS = {
    "⚡ 2秒 (実験・デモ用)": 2,
    "⏱️ 30秒": 30,
    "📅 1分": 60,
    "🌳 5分 (おすすめ)": 300,
    "🔋 10分 (省エネ)": 600,
    "💤 30分 (超長期)": 1800
}

# 表示期間マスタ
PERIOD_OPTIONS = ["今日（24時間）", "過去 3日間", "過去 1週間"]
DAYS_MAP = {"今日（24時間）": 1, "過去 3日間": 3, "過去 1週間": 7}

# 設定保存用のテーブル（バックエンドに伝えるため）
def init_settings_db():

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # テーブルがない場合作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY,
                interval_seconds INTEGER,
                selected_crop TEXT,
                selected_period TEXT
            )
        """)

        # 初期レコード値がなければデフォルト値を挿入
        cursor.execute("SELECT COUNT(*) FROM system_settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO system_settings (id, interval_seconds, selected_crop, selected_period)
                VALUES (1, 300, '🪴 汎用モード (基本設定)', '今日（24時間）')
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"設定テーブルの初期化に失敗: {e}")

def load_system_settings():

    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT interval_seconds, selected_crop, selected_period FROM system_settings WHERE id = 1", conn)
        conn.close()
        if not df.empty():
            return df.iloc[0].to_dict()
    except Exception as e:
        pass

    # エラー時のデフォルトフォールバック
    return {"interval_seconds": 300, "selected_crop": "🪴 汎用モード (基本設定)", "selected_period": "今日（24時間）"}
        
# ユーザーが変更した設定をデータベースに保存する関数
def save_system_settings(interval, crop, period):

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE system_settings
            SET interval_seconds = ?, selected_crop = ?, selected_period = ?
            WHERE id = 1
        """, (interval, crop, period))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

# メイン処理

# DBの初期化と前回の設定読み込み
init_settings_db()
saved_settings = load_system_settings()

# サイドバー設定
st.sidebar.header("⚙️ システム設定")

# 植物設定をDBから復元（見つからなければインデックス0）
crop_keys = list(CROP_PRESETS.keys())
default_crop_idx = crop_keys.index(saved_settings["selected_crop"]) if saved_settings["selected_crop"] in crop_keys else 0
selected_crop = st.sidebar.selectbox("📋 栽培する植物を選択", crop_keys, index=default_crop_idx)
preset = CROP_PRESETS[selected_crop]

st.sidebar.markdown("---")

# 計測間隔設定をDBから復元
interval_labels = list(INTERVAL_OPTIONS.keys())

# 保存されている秒数に対応するラベルを探す
default_interval_idx = 3    # デフォルト（5分）
for idx, label in enumerate(interval_labels):
    if INTERVAL_OPTIONS[label] == saved_settings["interval_seconds"]:
        default_interval_idx = idx
        break

selected_interval_label = st.sidebar.selectbox("⏱️ 計測間隔を設定", interval_labels, index=default_interval_idx)
interval_seconds = INTERVAL_OPTIONS[selected_interval_label]

st.sidebar.caption(f"現在の設定:  {interval_seconds} 秒 ごとに計測します。")

st.sidebar.markdown("---")

# 表示期間設定をDBから復元
default_period_idx = PERIOD_OPTIONS.index(saved_settings["selected_period"]) if saved_settings["selected_period"] in PERIOD_OPTIONS else 0
period = st.sidebar.radio("📊 表示期間を選択", PERIOD_OPTIONS, index=default_period_idx)
target_days = DAYS_MAP[period]

# 設定が変更されたら即座にDBに保存する
save_system_settings(interval_seconds, selected_crop, period)

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

st.subheader(selected_crop)

# 過去N日分のデータを取得（グラフ表示用）
def load_historical_data(days):
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT timestamp, moisture, temperature, humidity
        FROM sensor_logs
        WHERE timestamp >= datetime('now', ?, 'localtime')
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(f"-{days} days",))
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])   # 時間軸として扱えるように変換
    return df

# データ取得
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

        with g_col3:
            st.caption("💨 周囲の湿度の推移 (%)")
            chart_hum = base_chart.encode(y=alt.Y('humidity:Q', title=None, scale=alt.Scale(domain=[0, 100])), color=alt.value('#2ca02c'))
            st.altair_chart(chart_hum, use_container_width=True)
        
    else:
        st.info("選択された期間のデータがまだデータベースにありません。")
else:
    st.info("データベースが空っぽです。バックエンドのログにデータが保存されるまでしばらくお待ちください。")