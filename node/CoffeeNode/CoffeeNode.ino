#include "IoT_utils.h"
//#include "ESP8266WiFi.h"

String node_id = "69";
String node_CMDs[] = { "TOGGLE_COFFEE" };
uint8_t node_cmd_amount = 1;


extern WiFiClient client;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  connectToWifi();

  connectToServer();

}

void loop() {
  // put your main code here, to run repeatedly:
  //delay(500);

  String command = "";
  //handle commands must be called periodically to process incoming messages from server
  //returns empty string if command not recognized
  command = handleCommands();

  if ( command == node_CMDs[0] ) {
    DEBUGPRINTLN("ON");
  }

  reconnectWiFi();
  reconnectServer();
}
