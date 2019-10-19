/*
    This sketch establishes a TCP connection to a "quote of the day" service.
    It sends a "hello" message, and then prints received data.
*/

#include <ESP8266WiFi.h>


#ifndef STASSID
#define STASSID "Lohiverkko"
#define STAPSK  "88888888"
#endif

#define NODE_ID "RelayNode"
String NODE_ID_U = "UNDEFINED";

#define pwm_pin D7
#define STATUS_LED D1
#define RELAY_EN D2

const short int BUILTIN_LED1 = 2; //GPIO2
const short int BUILTIN_LED2 = 16;//GPIO16


//nodeCMD list

const String node_CMDs[] = {"ON", "OFF"};


String data = "NULL";
String cmd = "NULL";
int sep_ind = -1;

const char* ssid     = STASSID;
const char* password = STAPSK;

//const char* host = "192.168.0.9";  //Riksu
//const char* host = "192.168.1.35";  //marppanet
//const char* host = "192.168.10.34";  //narva
const char* host = "192.168.10.45";  //Herwood
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

void connectToWifi(){

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

  
}

void connectToServer(){

  //Connect to server
  Serial.print("connecting to server at:");
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

  data = client.readStringUntil('#');
  Serial.println(data);
   
  if(!(data == "SEND_ID")){
    Serial.println("Protocol error on ID request!");
    return;
  }

  Serial.print("Sending ID: ");
  Serial.println(NODE_ID_U);  
  client.print(NODE_ID_U);

  
  // wait for the response from server
  while(!client.available()){
    delay(100);
  }

  data = client.readStringUntil('#');
  Serial.println(data); 
  
  if(!(data == "SEND_CMDS")){
    Serial.println("Protocol error on CMD request!");
    return;
  }

  // SEND COMMAND LIST
  for(int i = 0; i < 3;i++){
    Serial.println("sent cmd");
    client.print(node_CMDs[i]);
    delay(50); //TODO Test if neccesary
  }

  Serial.println("Sending END");
  client.print("END");
  //client.receive();

   digitalWrite(STATUS_LED, HIGH); // Turn on STATUS_LED
  

  //delay(500);

  
  // finish handshake
  
}

void setup() {

  // Setup Pins
  pinMode(BUILTIN_LED1, OUTPUT); // Initialize the BUILTIN_LED1 pin as an output
  pinMode(BUILTIN_LED2, OUTPUT); // Initialize the BUILTIN_LED2 pin as an output
  pinMode(STATUS_LED, OUTPUT); //
  pinMode(RELAY_EN, OUTPUT); // 
  
  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED off by making the voltage HIGH
  digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH
  digitalWrite(STATUS_LED, LOW); // Turn the LED off by making the voltage LOW
  digitalWrite(RELAY_EN, HIGH); // Turn the RELAY_EN on by making the voltage HIGH

  digitalWrite(BUILTIN_LED1, LOW); 
  delay(500);
  digitalWrite(BUILTIN_LED1, HIGH); 
  delay(500);
  digitalWrite(BUILTIN_LED1, LOW); 
  delay(500);
  digitalWrite(BUILTIN_LED1, HIGH); 

  // Set Device ID based on MAC address

  NODE_ID_U = NODE_ID + WiFi.macAddress();
  
  


  client.setNoDelay(true);
  
  connectToWifi();
  connectToServer();
    
}






void loop() {
  
  
  // Listen for incoming nodeCMDs
  if(client.available()){
    
    digitalWrite(BUILTIN_LED1, LOW); // Turn the LED ON by making the voltage LOW
    data = client.readStringUntil('#');
    digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED ON by making the voltage LOW
    Serial.println(data); 

    sep_ind = data.indexOf('?');

    if(sep_ind != -1){

      cmd = data.substring(0,sep_ind);
      
    }else{

      cmd = data;
      
    }

    // Test cmd
    if(cmd == "ON"){        // Turn on fan

      digitalWrite(RELAY_EN, HIGH); // Close relay 

      client.print("OK");
      
      
    }else if(cmd == "OFF"){   // Turn off fan
      
      digitalWrite(RELAY_EN, LOW); // Open relay 
      
      client.print("OK");
      
      
    }else if(cmd == "PING"){
      
      client.print("PONG");
      
    }else if(cmd == "NULL"){
  
      client.print("NULL");
      
    }else{
  
      client.print("UNKWNCMD");
      
    }
      
  }else if(!client.connected()){
    Serial.println("Connection to server lost!");
    Serial.println("Waiting for connection...");

    for(int i = 0; i < 6; i++){ // Flash STATUS_LED
    
      digitalWrite(STATUS_LED, LOW); 
      delay(500);
      digitalWrite(STATUS_LED, HIGH); 
      delay(500);  
      
    }
    
    digitalWrite(STATUS_LED, LOW); 
     
    if(!client.connected()){
      
      Serial.println("No connection! Reconnecting...");
      connectToServer();
    }
  
  }else if(WiFi.status() != WL_CONNECTED){
    Serial.println("Connection to Wifi lost");
    Serial.println("Waiting for connection...");
    digitalWrite(STATUS_LED, LOW); 
    delay(5000);
    if(!client.connected()){
      
      Serial.println("No connection! Rebooting...");
      ESP.restart();
    }  
  }

  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED OFF by making the voltage HIGH
  delay(20);

}
