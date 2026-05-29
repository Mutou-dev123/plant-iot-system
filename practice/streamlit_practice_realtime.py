# リアルタイム更新
# 2秒ごとのデータ更新・グラフ書き換え
import streamlit as st
import matplotlib.pyplot as plt
import random
import time

placeholder = st.empty()    # 後で上書きするため、空の場所を作成
data = []
timestamps = list(range(len(data)))

while True: # 無限ループ
    data.append(random.randint(10, 30))
    timestamps.append(len(data))

    fig1, ax1 = plt.subplots()
    ax1.plot(timestamps, data)

    placeholder.pyplot(fig1)
    time.sleep(2)   # 2秒待機