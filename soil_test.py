# 土壌水分センサー用テストコード
from gpiozero import MCP3008
from time import sleep

# GPIOピン番号
soil_sensor = MCP3008(channel=0)

while True:
    raw_value = soil_sensor.value

    voltage = raw_value * 3.3

    print(f"数値: {raw_value:.4f} | 電圧: {voltage:.2f}V")

    sleep(0.5)