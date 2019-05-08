#include "IoT_utils.h"
//#include "ESP8266WiFi.h"

String node_id = "69";
String node_CMDs[] = { "TOGGLE_COFFEE" };
uint8_t node_cmd_amount = 1;

#define BUILDIN_LED1 2
#define BUILDIN_LED2 16
#define COFFEE_MAKER_SWITCH D1

extern WiFiClient client;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(BUILDIN_LED1,OUTPUT);
  pinMode(COFFEE_MAKER_SWITCH,OUTPUT);
  pinMode(BUILDIN_LED2,OUTPUT);

  digitalWrite(BUILDIN_LED1,HIGH);
  digitalWrite(BUILDIN_LED2,HIGH);
  digitalWrite(COFFEE_MAKER_SWITCH,LOW);
  
  connectToWifi();

  connectToServer();

}

void loop() {
  // put your main code here, to run repeatedly:
  //delay(500);
  if ( client.connected() ) digitalWrite(BUILDIN_LED2,LOW);
  else digitalWrite(BUILDIN_LED2,HIGH);



  String command = "";
  //handle commands must be called periodically to process incoming messages from server
  //returns empty string if command not recognized
  command = handleCommands();

  if ( command == "TOGGLE_COFFEE" ) {
    digitalWrite(BUILDIN_LED1,LOW);
    digitalWrite(COFFEE_MAKER_SWITCH,HIGH);
    delay(500);
    digitalWrite(BUILDIN_LED1,HIGH);
    digitalWrite(COFFEE_MAKER_SWITCH,LOW);
  }

  reconnectWiFi();
  reconnectServer();
}
