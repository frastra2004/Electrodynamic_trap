// This version writes to the circuit electronics, includes Dc & AC power control

//Author: Francesco Straniero
//Date: 04/03/2024


#include <TimeLib.h>
String incomingString;

int t;
int AC_duty_cycle;
int DC_duty;
int freq;
String str;
int ttl;
int voltage;
int voltage_1000;
int voltage_100;
int voltage_10;
int voltage_1;
int lolol;
int freq_1000;
int freq_100;
int freq_10;
int freq_1;
int DCvoltage;
int DCvoltage_1000;
int DCvoltage_100;
int DCvoltage_10;
int DCvoltage_1;
int lolol2;


void setup() {
  Serial.begin(115200);
  pinMode(7, OUTPUT);   //clock pin
  pinMode(4, OUTPUT);   //ttl pin
  pinMode(10, OUTPUT);  //AC voltage pin
  pinMode(11, OUTPUT);
  digitalWrite(7, LOW);
  digitalWrite(4, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11,LOW);
  delay(500);
}

void loop() {

  // This next if loop reads the Serial only if there is any communication available and creates a static variable which doesnt change until new communications come
  //this is very important for two reasons: 1) the variable values is kept through loops; 2)this is memory efficient.
  if (Serial.available() > 0) {
    incomingString = Serial.readString();
    str = incomingString.toInt();
    static int voltage;
    static int freq;
    static int ttl;
    static int lolol;
    static int lolol2;
  }
  ttl = String(str.charAt(0)).toInt();
  freq_1000 = String(str.charAt(1)).toInt();
  freq_100 = String(str.charAt(2)).toInt();
  freq_10 = String(str.charAt(3)).toInt();
  freq_1 = String(str.charAt(4)).toInt();
  freq =  1000*freq_1000 + 100 * freq_100 + 10 * freq_10 + freq_1;
  
  //voltage_100 = String(str.charAt(5)).toInt();
  voltage_10 = String(str.charAt(5)).toInt();
  voltage_1 = String(str.charAt(6)).toInt();
  voltage =   10 * voltage_10 + voltage_1;
  
  //DCvoltage_100 = String(str.charAt(8)).toInt();
  DCvoltage_10 = String(str.charAt(7)).toInt();
  DCvoltage_1 = String(str.charAt(8)).toInt();
  DCvoltage =   10 * DCvoltage_10 + DCvoltage_1;
 
  t = 500000 / freq;
  lolol = (255 * voltage) / 100;
  lolol2 = (255*DCvoltage)/100;
  AC_duty_cycle = truncf(lolol);
  DC_duty = truncf(lolol2);

  while (true) {
    if (Serial.available()>0){
      break;
    }

    if (ttl == 0) {
      digitalWrite(7, LOW);
      digitalWrite(4, HIGH);
      digitalWrite(10, LOW);
      digitalWrite(11,LOW);
    }

    if (ttl == 1) {
      analogWrite(10, AC_duty_cycle);
      analogWrite(11, DC_duty);

      if ((freq > 0) && (freq < 50)) {
        float tprime = t / 1000;
        digitalWrite(7, HIGH);
        delay(tprime);

        digitalWrite(7, LOW);
        delay(tprime);

      } else if (freq >= 50) {
        digitalWrite(7, HIGH);
        delayMicroseconds(t);

        digitalWrite(7, LOW);
        delayMicroseconds(t);
      }
    }
  }
}
