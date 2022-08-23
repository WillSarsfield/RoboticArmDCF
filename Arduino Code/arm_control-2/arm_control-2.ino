#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define MIN_PULSE_WIDTH 400
#define MAX_PULSE_WIDTH 2300
#define FREQUENCY 60
#define NUMBER_OF_MOTORS 5
#define NUMBER_OF_PUMPS 4
#define NUMBER_OF_SWITCHES 2
#define length1 10.5
#define length2 9
#define length3 11.7
#define length4 9.3
#define lowerX -30
#define upperX 30
#define lowerY -30
#define upperY 30
#define lowerZ -30
#define upperZ 30

int motor[5] = {0,4,8,12,15};
float ang[5] = {0.,0.,0.,0.,0.};
float startAng[5] = {0.,0.,0.,0.,0.};
float finishAng[5] = {0.,0.,0.,0.,0.};
float frame = 0.;
bool setFlag = true;
bool valid = true;
int bitPin = 2;
int pumpPin[4] = {12,12,12,12};
int directionPin[4] = {11,11,11,11};
int enablePin[4] = {10,10,10,10};
bool pumpFlag[4] = {false, false, false, false};
int steps[4] = {0,0,0,0};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(.1005);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);
  for (int x = 0; x < 4; x++){
    pinMode(pumpPin[x],OUTPUT);
    pinMode(directionPin[x],OUTPUT);
    pinMode(enablePin[x],OUTPUT); 
    digitalWrite(enablePin[x],HIGH); 
  }
  pinMode(bitPin, OUTPUT); 
  calibrate();
}

void calibrate(){//sets the physical motors to the correct start position when called
  for (int x  = 180; x >= 0; x -= 2){
    for (int y = 0; y < 5; y += 1){
      ang[y] = x ;
      delay(5);
      moveMotor(x ,motor[y]);
    }
  }
}

float getMotorPulse(float angle,int motorOut){
  float pulse;
   if (motorOut == 0){
    pulse = map(angle, 0, 180, MIN_PULSE_WIDTH+100, MAX_PULSE_WIDTH-50);//maps angle to pulse width, different for top motor
  }else if (motorOut==4){
    pulse = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);//maps angle to pulse width
  }else if (motorOut==8){
    pulse = map(angle, 0, 180, MIN_PULSE_WIDTH+50, MAX_PULSE_WIDTH);//maps angle to pulse width
  }else if (motorOut==12){
    pulse = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);//maps angle to pulse width
  }else if (motorOut==15){
    pulse = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH);//maps angle to pulse width
  }
  pulse = pulse / 1000000 * FREQUENCY * 4096;//changes pulse width to out pulse sent to servo
  return pulse;
}

float calcMockX(){//calculates a mock X coordinate from middle servos - used for 2 dimensions
  float xCoord[3] = {0.,0.,0.};
  xCoord[2] = length1 * cos(((ang[2])*M_PI)/180.);
  xCoord[1] = length2 * cos(((ang[2] + 90 - ang[1])*M_PI)/180.);
  xCoord[0] = length3 * cos((((ang[2] + 90 - ang[1]) + 90 - ang[0])*M_PI)/180.);
  return (xCoord[2] + xCoord[1] + xCoord[0]);
}

float calcTrueX(){//calculates X coordinate via all servos
  float xCoord = 0.;
  xCoord = calcMockX() * cos(((ang[3])*M_PI)/180.);
  return (xCoord);
}

float calcY(){// calculates Y coordinate from middle servos
  float yCoord[3] = {0.,0.,0.};
  yCoord[2] = length1 * sin(((ang[2])*M_PI)/180.);
  yCoord[1] = length2 * sin(((ang[2] + 90 - ang[1])*M_PI)/180.);
  yCoord[0] = length3 * sin((((ang[2] + 90 - ang[1]) + 90 - ang[0])*M_PI)/180.);
  return (yCoord[2] + yCoord[1] + yCoord[0]);
}

float calcZ(){//calculates Z coordinate from bottom servo
  float zCoord = 0.;
  zCoord = calcMockX() * sin(((ang[3])*M_PI)/180.);
  return (zCoord);
}

float getAngle(int motor, float input){//takes serial input and the motor calculated and returns the corresponding angle
  float angle = (input-(motor*181.));
  return angle;
}

int getMotor(float input){//takes serial input and returns the corresponding motor
  int motor = floor(input/181.);
  return motor;
}

int getPump(int input){
  int pumpNumber = floor((input-(((NUMBER_OF_MOTORS)*181)+1))/3001.);
  return pumpNumber;
}

int getSteps(int pump, float input){//takes serial input and the motor calculated and returns the corresponding angle
  int steps = ((input-((NUMBER_OF_MOTORS)*181))-(pump*3001.)) - 1501.;
  return steps;
}

int getSwitch(int input){
  int switchNumber = floor((input - (NUMBER_OF_MOTORS*181) - (NUMBER_OF_PUMPS * 3001)-1)/2);
  return switchNumber;
}

int getSwitchPulse(int switchNumber, float input){//takes serial input and the motor calculated and returns the corresponding angle
  int pulse = ((int(input - (NUMBER_OF_MOTORS*181) - (NUMBER_OF_PUMPS * 3001)+1))%2);
  return pulse;
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
  if (setFlag == true){
    while (Serial.available() == false){}
    delay(5); 
    float input = Serial.readString().toFloat();
    input -= 1.;
    //Serial.println(input);
    if (input <= (-1.)){
      setFlag = false;
    } else if (input >=0 && input <= ((NUMBER_OF_MOTORS)*181)){
      int motor = getMotor(input);
      float angle = getAngle(motor,input);
      finishAng[motor] = angle;
    } else if ((input >= ((NUMBER_OF_MOTORS)*181)+1) && (input <= (((NUMBER_OF_PUMPS)*3001)+((NUMBER_OF_MOTORS)*181)))){
      int pump = getPump(input);
      steps[pump] = getSteps(pump,input);
      pumpFlag[pump] = true;
      //Serial.println("pump " + String(pump) + " " + String(steps));
    } else if (((input >= (((NUMBER_OF_PUMPS)*3001)+((NUMBER_OF_MOTORS)*181))+1)) && (input <= (((((NUMBER_OF_PUMPS)*3001)+((NUMBER_OF_MOTORS)*181)+1))+NUMBER_OF_SWITCHES*2)+1)){
      int switchNumber = getSwitch(input);
      int switchPulse = getSwitchPulse(switchNumber, input);
      //Serial.println("switch " + String(switchNumber) + " " + String(switchPulse));
    }
  } else{
    for (int x = 0; x < 4; x += 1){
      if (pumpFlag[x] == true){
        movePump(x);
        pumpFlag[x] = false;
      }
    }
    frame += 0.25;
    for (int x = 0; x < 5; x += 1){    
      if (frame < 61 && valid != false){//within frames 0 to 90
        ang[x] = map(frame, 0, 60, startAng[x], finishAng[x]);
        if (checkBounds() != false){
          moveMotor(ang[x], motor[x]);
        } else {
          Serial.println("out of bounds");
          valid = false;
          for (int y = 0; y < 5; y += 1){
            ang[y] = map(frame - 1, 0, 60, startAng[y], finishAng[y]);
          }
        }
      }
    }
    
      if (frame > 61 || valid == false){//once frames exceed 90, resets frames and waits for new serial to read
        for (int x = 0; x < 5; x += 1){
          startAng[x] = ang[x];
          finishAng[x] = ang[x];
          frame = 0;
          setFlag = true;
          valid = true;
       }
    }
  }
}

void movePump(int pump){
  if (steps[pump] < 0){
    digitalWrite(directionPin, LOW);
  } else{
    digitalWrite(directionPin, HIGH);
  }
  for(int i =0; i<steps[pump];i++){
    digitalWrite(pumpPin[pump],HIGH);
    delayMicroseconds(600);
    digitalWrite(pumpPin[pump],LOW);//for pulse duration>4μs
    delayMicroseconds(600);
    delay(10);
 }
}

void moveMotor(float angle, int motorOut){//takes the motor and angle specified and physically moves the corresponding servo
  float pulse;
  pulse = getMotorPulse(angle,motorOut);
  //Serial.println(pulse);
  pwm.setPWM(motorOut, 0, pulse);
  //Serial.println("motor " + String((motorOut/4)+1) + " " + angle + " x: " + String(calcTrueX()) + " y: " + String(calcY()) + " z: " + String(calcZ()));
  delayMicroseconds(10);
}
