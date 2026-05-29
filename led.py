# LED点灯用テストコード
import RPi.GPIO as GPIO
import time

PNO = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PNO, GPIO.OUT)

for i in range(15):
    GPIO.output(PNO, GPIO.HIGH)
    time.sleep(0.4)
    GPIO.output(PNO, GPIO.LOW)
    time.sleep(0.4)

GPIO.cleanup()