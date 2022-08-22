long directionPin=5;//terminal 4 on the motor connected to pin 5 on arduino 
long pulsePin=8;//terminal 5 on the motor connected to pin 8 on arduino
long enablePin=3;//terminal 6 on the motor connected to pin 3 on arduino
long numSteps;
long i=0;
long motorDelay =600;
String msg="How many Steps do you want?:";
void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
pinMode(pulsePin,OUTPUT);
pinMode(directionPin,OUTPUT);
pinMode(enablePin,OUTPUT); 
digitalWrite(enablePin,HIGH);   
}
void loop() {
digitalWrite(directionPin,HIGH);//if terminal 4 for direction is not connected, CHANGE LOW AND HIGH TO CHANGE DIRECTION
Serial.println(msg);
while(Serial.available()==0){
  }
 numSteps = Serial.parseInt();
 if (numSteps < 0){
  digitalWrite(directionPin, LOW);
 }
//put your main code here, to run repeatedly:
 for(i =0; i<numSteps;i++){
     digitalWrite(pulsePin,HIGH);
     delayMicroseconds(motorDelay);
     digitalWrite(pulsePin,LOW);//for pulse duration>4μs
     delayMicroseconds(motorDelay);
     delay(10);
 }
}
