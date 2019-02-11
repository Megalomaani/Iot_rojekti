/*
    This sketch establishes a TCP connection to a "quote of the day" service.
    It sends a "hello" message, and then prints received data.
*/

#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "Lohiverkko"
#define STAPSK  "88888888"
#endif

#define NODE_ID "1234"

// TODO: nodeCMD list

const char* ssid     = STASSID;
const char* password = STAPSK;

const char* host = "djxmmx.net";
const uint16_t port = 2500;

WiFiClient client;


String receive(int timeout = -1){
  int i = 0;

  while(!client.available()){
    if(i != timeout){
      delay(500);
      i++;
    }else{
      return "NULL";
    }
  }
  
  String cmd = client.readStringUntil('#');
  
  return cmd;
  
}

void setup() {
  Serial.begin(115200);

  // We start by connecting to a WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);

  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default,
     would try to act as both a client and an access-point and could cause
     network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // wifi connected
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  //Connect to server
  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);


  // Use WiFiClient class to create TCP connections
  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    delay(5000);
    return;
  }
  

  // This will send a string to the server
  Serial.println("sending data to server");
  if (client.connected()) {
    client.println("Hello from node");
  }

  // wait for the response from server
  while(!client.available()){
    delay(100);
  }

  if(!(client.readStringUntil('#') == "SEND_ID")){
    Serial.println("Protocol error on ID request!");
    return;
  }

  client.println(NODE_ID);

  
  if(!(client.readStringUntil('#') == "SEND_CMDS")){
    Serial.println("Protocol error on CMD request!");
    return;
  }

  // SEND COMMAND LIST

  
  // finish handshake


  
}



void loop() {
  
  
  // wait for data to be available
  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      delay(60000);
      return;
    }
  }

  

  // Close the connection
  Serial.println();
  Serial.println("closing connection");
  client.stop();

  delay(300000); // execute once every 5 minutes, don't flood remote service
}
