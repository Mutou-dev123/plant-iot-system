# Matplotlib 基礎
import matplotlib.pyplot as plt

# === 基本 ===
data = [10, 20, 15, 30]

plt.plot(data)
plt.title("Sample Data")
plt.xlabel("Time")
plt.ylabel("Value")

plt.show()
plt.clf()   # リセット

# === 時間軸 ===
time = [1, 2, 3, 4]
value = [10, 20, 15, 30]

plt.plot(time, value)
plt.title("Temperature")
plt.xlabel("Time")
plt.ylabel("°C")

plt.show()
plt.clf()

# === 複数データ ===
temp = [20, 22, 21, 23]
humid = [60, 65, 63, 70]

plt.plot(temp, label="Temp")
plt.plot(humid, label="Humidity")

plt.legend() # 凡例表示
plt.show()
plt.clf()

# === 増加データ対応型 ===
value = [10, 20, 15, 30]
# 要素数（取得時間数）
time = list(range(len(value)))

plt.plot(time, value)
plt.show()