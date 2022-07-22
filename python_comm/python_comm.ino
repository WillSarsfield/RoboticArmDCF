int x=0;
int led1=10;
int led2=11;
int led3=9;
int led4=6;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  pinMode(led1,OUTPUT);
  pinMode(led2,OUTPUT);
  pinMode(led3,OUTPUT);
  pinMode(led4,OUTPUT);
  digitalWrite(led1,HIGH);
  delay(100);
  digitalWrite(led1,LOW);
  delay(100);
  digitalWrite(led1,HIGH);
  delay(100);
  digitalWrite(led1,LOW);
  delay(100);
}

void loop() {
  Serial.print(x);
  while (!Serial.available()){}
  x=!Serial.readString().toInt();
  digitalWrite(led1,x);
  digitalWrite(led2,x);
  digitalWrite(led3,x);
  digitalWrite(led4,x);
}
