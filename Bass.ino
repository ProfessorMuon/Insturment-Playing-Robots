#include <Servo.h>

Servo rackServo;
Servo pluckServo;

#define RACK_PIN 9
#define PLUCK_PIN 10

int rackUp = 90;
int rackDown = 140;
int pluckRest = 90;

void setup() {

  Serial.begin(115200);

  rackServo.attach(RACK_PIN);
  pluckServo.attach(PLUCK_PIN);

  rackServo.write(rackUp);
  pluckServo.write(pluckRest);
}

void loop() {

  if(Serial.available()){

    String cmd = Serial.readStringUntil('\n');

    if(cmd == "RACK_DOWN"){
      rackServo.write(rackDown);
    }

    else if(cmd == "RACK_UP"){
      rackServo.write(rackUp);
    }

    else if(cmd.startsWith("PLUCK:")){

      int strength = cmd.substring(6).toInt();

      int strike = map(strength,0,255,70,30);

      pluckServo.write(strike);
      delay(15);
      pluckServo.write(pluckRest);
    }

    else if(cmd == "STOP"){

      rackServo.write(rackUp);
      pluckServo.write(pluckRest);
    }
  }
}
