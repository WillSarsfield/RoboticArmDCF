#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <IRremote.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define MIN_PULSE_WIDTH 800
#define MAX_PULSE_WIDTH 2200
#define FREQUENCY 60

int motor[4] = {0,4,8,12};
int input[4] = {A0,A1,A2,A3};
float ang[4] = {0.,0.,0.,0.};
float startAng[4] = {0.,0.,0.,0.};
float finishAng[4] = {0.,0.,0.,0.};
int IRpin = 3;
int code;
bool pause = true;
int frame = 0;  

IRrecv IR(IRpin);
decode_results cmd;

void setup() {
  // put your setup code here, to run once:
  IR.enableIRIn();
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);
}

void calibrate(){
  for (int y = 0; y < 4; y += 1){
    for (int x  = 180; x >= startAng[y]; x -= 1){
      moveMotor(x ,motor[y]);
    }
  }
  Serial.println();
}

void loop(){//loops to check for power and pause, then executes chosen task repeatedly
  if (IR.decode(&cmd)!=0 && cmd.value == 16712445){
    pause = !pause;
    Serial.println("pause: " + String(pause));
    delay(100);
  }
  IR.resume();
  if (pause == false){ 
    frame += 1;
    if (frame != 181){
      for (int x = 0; x < 4; x += 1){
        ang[x] = map(frame, 0, 180, startAng[x], finishAng[x]);
        moveMotor(ang[x], motor[x]);
      }
      Serial.println();
    } else {
      frame = 0;
      for (int x = 0; x < 4; x += 1){
        startAng[x] = finishAng[x];
      }
    }
  }
}

void moveMotor(float angle, int motorOut){
  int pulse;
  pulse = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);
  pulse = int(float(pulse) / 1000000 * FREQUENCY * 4096);
  pwm.setPWM(motorOut, 0, pulse);
  Serial.print(String(pulse) + " ");
  delay(5);
}