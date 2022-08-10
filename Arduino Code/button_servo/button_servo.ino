#include <Servo.h>
const int servo1Pin=5;
const int servo2Pin=3;
int servo1Pos=0;
int servo2Pos=0;
int selectedServo;
int delayTime=100;
int raw_input;

Servo servo1;
Servo servo2;

void setup() {
Serial.begin(9600);
servo1.attach(servo1Pin);
servo2.attach(servo2Pin);
}

void loop() {
while (!Serial.available()){}
delay(5);
raw_input=Serial.readString().toInt();
Serial.println(raw_input);
}
