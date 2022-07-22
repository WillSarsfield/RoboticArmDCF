#include <Servo.h>
const int servo1Pin=5;
const int servo2Pin=3;
int servo1Pos=0;
int servo2Pos=0;
int selectedServo;
int delayTime=100;

Servo servo1;
Servo servo2;

void setup() {
Serial.begin(9600);
servo1.attach(servo1Pin);
servo2.attach(servo2Pin);
}

void loop() {
while (!Serial.available()){}
selectedServo=Serial.readString().toInt();
Serial.println(selectedServo);
if (selectedServo==1){
  servo1Pos=180;
  servo1.write(servo1Pos);
} else if (selectedServo==2){
  servo2Pos=180;
  servo2.write(servo2Pos);
}
}
