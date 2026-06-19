#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  pinMode(4, OUTPUT);
}

void loop() {
  digitalWrite(4, HIGH);
  Serial.println("VS CodeからLチカ！");
  delay(1000);

  digitalWrite(4, LOW);
  Serial.println("VS CodeからLチカOFF！");
  delay(1000);
}