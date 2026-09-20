#include <Wire.h>

#define MPU_ADDR 0x68

void setup() {
  Serial.begin(115200);
  Wire.begin();

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  delay(100);


  Serial.println("AccX,AccY,AccZ,Magnitude");
}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);

  int16_t AccX = Wire.read() << 8 | Wire.read();
  int16_t AccY = Wire.read() << 8 | Wire.read();
  int16_t AccZ = Wire.read() << 8 | Wire.read();

  float axg = AccX / 16384.0;
  float ayg = AccY / 16384.0;
  float azg = AccZ / 16384.0;

  float magnitude = sqrt(axg * axg + ayg * ayg + azg * azg);


  Serial.print(axg, 4);
  Serial.print(",");
  Serial.print(ayg, 4);
  Serial.print(",");
  Serial.print(azg, 4);
  Serial.print(",");
  Serial.println(magnitude, 4);

  delay(20); 
}