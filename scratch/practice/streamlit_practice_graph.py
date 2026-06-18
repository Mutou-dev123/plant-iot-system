# Streamlit グラフ表示
import streamlit as st
import matplotlib.pyplot as plt
import random

st.title("Graph Test")

# ダミーデータ生成
data = [random.randint(10, 30) for _ in range(10)]
timestamps = list(range(len(data)))

# グラフ作成
fig1, ax1 = plt.subplots()
ax1.plot(timestamps, data, label="data")

ax1.set_title("Sample Graph")
ax1.set_xlabel("Time")
ax1.set_ylabel("Value")
ax1.legend()

# グラフ表示
st.pyplot(fig1)


# 複数データ
temp = [random.randint(20, 30) for _ in range(10)]
humid = [ random.randint(50, 70) for _ in range(10)]

fig2, ax2 = plt.subplots()
ax2.plot(timestamps, temp, label="Temp")
ax2.plot(timestamps, humid, label="Humidity")

ax2.set_title("Sample Graph2")
ax2.legend()

st.pyplot(fig2)

# 複数データ & 左右軸
st.title("Temp & Humidity")

# データ生成
timestamps = list(range(10))
temp = [random.randint(20, 30) for _ in range(10)]
humid = [random.randint(50, 70) for _ in range(10)]

# グラフ作成
fig3, ax3 = plt.subplots()

# 左軸（温度）
ax3.plot(timestamps, temp, color="red", label="Temp")
ax3.set_ylabel("Temperature ℃", color="red")

# 右軸（湿度）
ax4 = ax3.twinx()
ax4.plot(timestamps, humid, color="blue", label="Humidity")
ax4.set_ylabel("Humidity %", color="blue")

# 軸範囲固定
ax3.set_ylim(0, 40)     # 温度
ax4.set_ylim(0, 100)    # 湿度

# 最新データの協調
ax3.scatter(timestamps[-1], temp[-1], color="red")
ax4.scatter(timestamps[-1], humid[-1], color="blue")

# メモリの色
ax3.tick_params(axis='y', labelcolor='red')
ax4.tick_params(axis='y', labelcolor='blue')

# グリッド表示
ax3.grid(True, linestyle="--", alpha=0.5)

# タイトル
ax3.set_title("Temperature & Humidity")

# 表示
st.pyplot(fig3)