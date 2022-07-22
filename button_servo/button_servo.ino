#include <Servo.h>
int servoPin=5;
int servoPos=0;
int delayTime=100;
Servo servo1;

void setup() {
Serial.begin(9600);
servo1.attach(servoPin);
}

void loop() {
while (!Serial.available()){}
servoPos=Serial.readString().toInt();
servo1.write(servoPos);
}
