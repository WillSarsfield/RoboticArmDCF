#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define MIN_PULSE_WIDTH 400
#define MAX_PULSE_WIDTH 2400
#define FREQUENCY 60
#define lowerX -30
#define upperX 30
#define lowerY -30
#define upperY 30
#define lowerZ -30
#define upperZ 30

int motor[4] = {0,4,8,12};
float ang[4] = {0.,0.,0.,0.};
int startAng[4] = {0,0,0,0};
int finishAng[4] = {0,0,0,0};
float frame = 0.;
bool setFlag = true;
bool valid = true;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(.1005);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);
  calibrate();
}

void calibrate(){//sets the physical motors to the correct start position when called
  for (int x  = 180; x >= 0; x -= 1){
    for (int y = 0; y < 4; y += 1){
      ang[y] = x ;
      moveMotor(x ,motor[y]);
    }
  }
}

float getMotorAngle(float angle){
  return map(angle, 0, 180, -50, 180);
}

float calcMockX(){//calculates a mock X coordinate from middle servos - used for 2 dimensions
  float xCoord[3] = {0.,0.,0.};
  xCoord[2] = 10.5 * cos(((ang[2])*M_PI)/180.);
  xCoord[1] = 9 * cos(((ang[2] + 90 - ang[1])*M_PI)/180.);
  xCoord[0] = 5 * cos((((ang[2] + 90 - ang[1]) + 90 - ang[0])*M_PI)/180.);
  return (xCoord[2] + xCoord[1] + xCoord[0]);
}

float calcTrueX(){//calculates X coordinate via all servos
  float xCoord = 0.;
  xCoord = calcMockX() * cos(((ang[3])*M_PI)/180.);
  return (xCoord);
}

float calcY(){// calculates Y coordinate from middle servos
  float yCoord[3] = {0.,0.,0.};
  yCoord[2] = 10.5 * sin(((ang[2])*M_PI)/180.);
  yCoord[1] = 9 * sin(((ang[2] + 90 - ang[1])*M_PI)/180.);
  yCoord[0] = 5 * sin((((ang[2] + 90 - ang[1]) + 90 - ang[0])*M_PI)/180.);
  return (yCoord[2] + yCoord[1] + yCoord[0]);
}

float calcZ(){//calculates Z coordinate from bottom servo
  float zCoord = 0.;
  zCoord = calcMockX() * sin(((ang[3])*M_PI)/180.);
  return (zCoord);
}

int getAngle(int motor, int input){//takes serial input and the motor calculated and returns the corresponding angle
  int angle = (input-(motor*181));
  return angle;
}

int getMotor(int input){//takes serial input and returns the corresponding motor
  int motor = floor(input/181);
  return motor;
}

bool checkBounds(){
  if (calcTrueX() >= upperX || calcTrueX() <= lowerX){
    return false;
  } else if (calcY() >= upperY || calcY() <= lowerY){
    return false;
  }else if (calcZ() >= upperZ || calcZ() <= lowerZ){
    return false;
  } else{
    return true;
  }
}

void loop(){//then executes input instruction
  if (setFlag == true){//serial read to change new finish angle until told to execute
    while (!Serial.available()){}
    delay(10);
    int input = Serial.readString().toInt();
    input--;
    if (input == -1){//input read as serial input and translated to motor - angle
      setFlag = false;
    } else{
      if (input > -1 && input < 725){
        int currentMotor = getMotor(input);
        finishAng[currentMotor] = getAngle(currentMotor, input);
        Serial.println("motor: " + String(currentMotor) + " angle:" + String(finishAng[currentMotor]));
      }
      }
  }
  if (setFlag == false){ //when unpaused and not looking for angle to read
    frame += 1;
      for (int x = 0; x < 4; x += 1){
        if (frame < 181 && valid != false){//within frames 0 to 180
          ang[x] = map(frame, 0, 180, startAng[x], finishAng[x]);
          if (checkBounds() != false){
            moveMotor(ang[x], motor[x]);
          } else {
            valid = false;
            for (int x = 0; x < 4; x += 1){
              ang[x] = map(frame - 1, 0, 180, startAng[x], finishAng[x]);
            }
          }
        }
      } 
      if (frame > 181 || valid == false){//once frames exceed 180, resets frames and waits for new serial to read
        for (int x = 0; x < 4; x += 1){ 
          startAng[x] = ang[x];
          finishAng[x] = ang[x];
        }
        frame = 0;
        setFlag = true;
        valid = true;
      }
    }
}

void moveMotor(float angle, int motorOut){//takes the motor and angle specified and physically moves the corresponding servo
  int pulse;
  angle = getMotorAngle(angle);
  if (motorOut == 0){
    pulse = map(angle, -50, 180, MIN_PULSE_WIDTH + 100, MAX_PULSE_WIDTH - 200);//maps angle to pulse width, different for top motor
  } else{
    pulse = map(angle, -50, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);//maps angle to pulse width
  }
  pulse = int(float(pulse) / 1000000 * FREQUENCY * 4096);//changes pulse width to out pulse sent to servo
  pwm.setPWM(motorOut, 0, pulse);
  Serial.println(String(map(angle, -50, 180, 0, 180)) + " x: " + String(calcTrueX()) + " y: " + String(calcY()) + " z: " + String(calcZ()));
  delay(5);
}
