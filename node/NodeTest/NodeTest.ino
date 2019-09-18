/*
  ESP8266 Blink by Simon Peter
  Blink the blue LED on the ESP-01 module
  This example code is in the public domain

  The blue LED on the ESP-01 module is connected to GPIO1
  (which is also the TXD pin; so we cannot use Serial.print() at the same time)

  Note that this sketch uses LED_BUILTIN to find the pin with the internal LED
*/

const short int BUILTIN_LED1 = 2; //GPIO2
const short int BUILTIN_LED2 = 16;//GPIO16

const short int STATUS_LED = 5;//GPIO16
const short int RELAY_EN = 4;//GPIO16

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
  pinMode(BUILTIN_LED1, OUTPUT); // Initialize the BUILTIN_LED1 pin as an output
  pinMode(BUILTIN_LED2, OUTPUT); // Initialize the BUILTIN_LED2 pin as an output

  pinMode(STATUS_LED, OUTPUT); // Initialize the STATUS_LED pin as an output
  pinMode(RELAY_EN, OUTPUT); // Initialize the RELAY_EN pin as an output
}

// the loop function runs over and over again forever
void loop() {
  
  digitalWrite(BUILTIN_LED1, LOW);

  delay(1000); 
                       
  digitalWrite(BUILTIN_LED1, HIGH);  


  delay(500);

  
  digitalWrite(STATUS_LED, HIGH);

  delay(1000); 
                       
  digitalWrite(STATUS_LED, LOW);  


  delay(500);

  
  digitalWrite(RELAY_EN, HIGH);

  delay(1000); 
                       
  digitalWrite(RELAY_EN, LOW);  

  
  
  delay(2000);                      
  
}
