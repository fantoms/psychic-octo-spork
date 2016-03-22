#include <Wire.h>

int M1 = 0;
int M2 = 0;
int M3 = 0;
int M4 = 0;
int M5 = 0;
//int M6 = 0;

char moisture_data[33] = "";
int moisture_data_len = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  //pinMode(A4, INPUT);
  pinMode(A7, INPUT);
  Serial.begin(115200);
//  Serial2.begin(115200);
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event
}

void requestEvent() {
  //Serial.print(moisture_data);
  //Serial.print("-");
  //Serial.println(moisture_data_len);
    Wire.write(moisture_data); // respond with message of 6 bytes
    // as expected by master
}

String readMoisture() {
  //$0000-0000-0000-0000-0000-0000#
  M1 = analogRead(A0);
  M2 = analogRead(A1);
  M3 = analogRead(A2);
  M4 = analogRead(A3);
  M5 = analogRead(A7);
  //M6 = analogRead(A5);
  String moistureData = "";
  moistureData = "$";
  moistureData.concat(M1);
  moistureData.concat("-");
  moistureData.concat(M2);
  moistureData.concat("-");
  moistureData.concat(M3);
  moistureData.concat("-");
  moistureData.concat(M4);
  moistureData.concat("-");
  moistureData.concat(M5);
  //moistureData.concat("-");
  //moistureData.concat(M6);
  moistureData.concat("#");
  if(moistureData.length() <=32) {
    moisture_data_len = moistureData.length()+1;
    moistureData.toCharArray(moisture_data, 32);
  }
 return String(moistureData);
}

void loop() {
  // put your main code here, to run repeatedly:
  String sensors = readMoisture();
  Serial.println(sensors);
//  Serial2.println(sensors);
  delay(420);
}

