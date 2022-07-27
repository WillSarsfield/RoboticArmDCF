#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define MIN_PULSE_WIDTH 800
#define MAX_PULSE_WIDTH 2200
#define FREQUENCY 60

int motor[4] = {0,4,8,12};
int ang[4] = {0,0,0,0};
int startAng[4] = {0,0,0,0};
int finishAng[4] = {0,0,0,0};
int frame = 0;
bool setFlag = true;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(.1);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);
  calibrate();
}

void calibrate(){//sets the physical motors to the correct start position when called
  for (int y = 0; y < 4; y += 1){
    for (int x  = 180; x >= startAng[y]; x -= 1){
      moveMotor(x ,motor[y]);
    }
  }
}

int getAngle(int motor, int input){//takes serial input and the motor calculated and returns the corresponding angle
  int angle = (input-(motor*181));
  return angle;
}

int getMotor(int input){//takes serial input and returns the corresponding motor
  int motor = floor(input/181);
  return motor;
}

void loop(){//then executes input instruction
  if (setFlag == true){//serial read to change new finish angle until told to execute
    while (!Serial.available()){}
    delay(5);
    int input = Serial.readString().toInt();
    input--;
    if (input == -1){
      setFlag = false;
    } else{
      int currentMotor = getMotor(input);
      finishAng[currentMotor] = getAngle(currentMotor, input);
      Serial.println(String(finishAng[currentMotor]) + String(currentMotor));
    }
  }
  if (setFlag == false){ //when unpaused and not looking for angle to read
    frame += 1;
    if (frame < 181){//within frames 0 to 180
      for (int x = 0; x < 4; x += 1){
        ang[x] = map(frame, 0, 180, startAng[x], finishAng[x]);
        moveMotor(ang[x], motor[x]);
      }
    } else {//once frames exceed 180, resets frames and waits for new serial to read
      frame = 0;
      setFlag = true;
      for (int x = 0; x < 4; x += 1){//updates the new start angles to the previous finish angles
        startAng[x] = finishAng[x];
      }
    }
  }
}

void moveMotor(float angle, int motorOut){//takes the motor and angle specified and physically moves the corresponding servo
  int pulse;
  pulse = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);//maps angle to pulse width
  pulse = int(float(pulse) / 1000000 * FREQUENCY * 4096);//changes pulse width to out pulse sent to servo
  pwm.setPWM(motorOut, 0, pulse);
  //delay(0);
}
