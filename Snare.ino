int event = 0;

int strikelegnth = 80;

int incomingByte = 0;


void setup() {
  
  //establish motor direction toggle pins
  pinMode(12, OUTPUT); //CH A -- HIGH = forwards and LOW = backwards???
  pinMode(13, OUTPUT); //CH B -- HIGH = forwards and LOW = backwards???
  
  //establish motor brake pins
  pinMode(9, OUTPUT); //brake (disable) CH A
  pinMode(8, OUTPUT); //brake (disable) CH B

  digitalWrite(9, LOW);  //ENABLE CH A
  digitalWrite(8, LOW); //ENABLE CH B  
  
  
  Serial.begin(57600);

 cli();//stop interrupts

  //set timer2 interrupt every 128us
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 7.8khz increments
  OCR2A = 255;// = (16*10^6) / (7812.5*8) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS11 bit for 8 prescaler
  TCCR2B |= (1 << CS11);   
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
  
  sei();//allow interrupts

}

void loop() {
 
 if(event == 1){

   if (incomingByte == 131) {
       //start down
       digitalWrite(9, LOW); //Disengage the Brake for Channel A
       digitalWrite(12, LOW);   //Sets direction of CH A
       analogWrite(3, 255);   //Moves CH A
       
       //strike time
       delay(strikelegnth);
       
       //stop
       digitalWrite(9, HIGH); //Engage the Brake for Channel A
       delay(10);
       
       //go back
       digitalWrite(9, LOW); //Disengage the Brake for Channel A
       digitalWrite(12, HIGH);   //Sets direction of CH A
       analogWrite(3, 255);   //Moves CH A
       
       //recoil time
       delay(40);    
       
       //stop
       digitalWrite(9, HIGH); //Engage the Brake for Channel A
       
       event = 0; 
   }  
   
   
   if (incomingByte == 132) {
       //start down
       digitalWrite(8, LOW); //Disengage the Brake for Channel A
       digitalWrite(13, LOW);   //Sets direction of CH A
       analogWrite(11, 255);   //Moves CH A
       
       //strike time
       delay(strikelegnth);
       
       //stop
       digitalWrite(8, HIGH); //Engage the Brake for Channel A
       delay(10);
       
       //go back
       digitalWrite(8, LOW); //Disengage the Brake for Channel A
       digitalWrite(13, HIGH);   //Sets direction of CH A
       analogWrite(11, 255);   //Moves CH A
       
       //recoil time
       delay(40);    
       
       //stop
       digitalWrite(8, HIGH); //Engage the Brake for Channel A
       
       event = 0; 
   }  
   
   if (incomingByte == 160) {
       //start down
       digitalWrite(9, LOW); //Disengage the Brake for Channel A
       digitalWrite(12, LOW);   //Sets direction of CH A
       analogWrite(3, 255);   //Moves CH A
       
       digitalWrite(8, LOW); //Disengage the Brake for Channel A
       digitalWrite(13, LOW);   //Sets direction of CH A
       analogWrite(11, 255);   //Moves CH A
       
       //strike time
       delay(strikelegnth);
       
       //stop
       digitalWrite(8, HIGH); //Engage the Brake for Channel A
       digitalWrite(9, HIGH); //Engage the Brake for Channel A
       delay(10);
       
       //go back
       digitalWrite(9, LOW); //Disengage the Brake for Channel A
       digitalWrite(12, HIGH);   //Sets direction of CH A
       analogWrite(3, 255);   //Moves CH A
       
       digitalWrite(8, LOW); //Disengage the Brake for Channel A
       digitalWrite(13, HIGH);   //Sets direction of CH A
       analogWrite(11, 255);   //Moves CH A
       
       //recoil time
       delay(40);    
       
       //stop
       digitalWrite(8, HIGH); //Engage the Brake for Channel A
       digitalWrite(9, HIGH); //Engage the Brake for Channel A
       
       event = 0; 
   }  
 }
}



ISR(TIMER2_COMPA_vect) {
  do{
    if (Serial.available()){
      incomingByte = Serial.read();
      event = 1;
    }//end if serial available
  }//end do
 while (Serial.available() > 8);
}    

