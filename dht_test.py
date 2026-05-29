# 温湿度センサー用テストコード
import adafruit_dht
import board
import time

dhtDevice = adafruit_dht.DHT11(board.D4)

while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(temperature, humidity)
        if temperature is not None and humidity is not None:
            print(f"Temp: {temperature}℃ Humidity: {humidity}%")
        else:
            print("データ取得待ち．．．")

        if temperature >= 30:
            print("暑すぎる！")
        elif temperature <= 10:
            print("寒すぎる！")
        else:
            print("適正！適正！")

    except RuntimeError as e:
        print(f"読み取り失敗: {e}")

    time.sleep(2)