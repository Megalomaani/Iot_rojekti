/*
    This sketch establishes a TCP connection to a "quote of the day" service.
    It sends a "hello" message, and then prints received data.
*/

#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "Koti_005D"
#define STAPSK  "A3LDJCRAJYL3F"
//#define STASSID "HUAWEI P10 lite"
//#define STAPSK  "77777777"
#endif

#define NODE_ID "1234"

const short int BUILTIN_LED1 = 2; //GPIO2
const short int BUILTIN_LED2 = 16;//GPIO16

//nodeCMD list

const String node_CMDs[] = {"LIGHT_ON", "LIGHT_OFF"};


String data = "NULL";

const char* ssid     = STASSID;
const char* password = STAPSK;

//const char* host = "192.168.1.38";  //marppanet
const char* host = "192.168.10.34";  //narva
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

  // Setup LEDs
  pinMode(BUILTIN_LED1, OUTPUT); // Initialize the BUILTIN_LED1 pin as an output
  pinMode(BUILTIN_LED2, OUTPUT); // Initialize the BUILTIN_LED2 pin as an output
  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED off by making the voltage HIGH
  digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH
  
  delay(200);
  Serial.begin(9600);
  delay(200);
  Serial.println();
  Serial.println();
  
  

  // Connecting to a WiFi network
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
    client.print("Hello from node ");
  }

  // wait for the response from server
  while(!client.available()){
    delay(100);
  }

  data = client.readStringUntil('\n');
  Serial.println(data);
   
  if(!(data == "SEND_ID")){
    Serial.println("Protocol error on ID request!");
    return;
  }

  Serial.print("Sending ID: ");
  Serial.println(NODE_ID);  
  client.print(NODE_ID);

  
  // wait for the response from server
  while(!client.available()){
    delay(100);
  }

  data = client.readStringUntil('\n');
  Serial.println(data); 
  
  if(!(data == "SEND_CMDS")){
    Serial.println("Protocol error on CMD request!");
    return;
  }

  // SEND COMMAND LIST
  for(int i = 0; i < 2;i++){
    Serial.println("sent cmd");
    client.print(node_CMDs[i]);
    delay(50); //TODO Test if neccesary
  }

  Serial.println("Sending END");
  client.print("END");


  delay(500);

  
  // finish handshake
  
}



void loop() {

  // Listen for incoming nodeCMDs
  data = receive();

  // Test cmd
  if(data == "LIGHT_ON"){

    digitalWrite(BUILTIN_LED2, LOW); // Turn the LED ON by making the voltage LOW 
    client.print("OK");
    
  }else if(data == "LIGHT_OFF"){
    
    digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH
    client.print("OK");
    
  }else if(data == "PING"){
    
    client.print("PONG");
    
  }else if(data == "NULL"){

    client.print("NULL");
    
  }else{

    client.print("UNKWNCMD");
    
  }

  delay(500);

}

/*

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
 
 */
