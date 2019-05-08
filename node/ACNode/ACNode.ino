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

#define pwm_pin D7

const short int BUILTIN_LED1 = 2; //GPIO2
const short int BUILTIN_LED2 = 16;//GPIO16


//nodeCMD list

const String node_CMDs[] = {"LIGHT_ON", "LIGHT_OFF"};


String data = "NULL";

const char* ssid     = STASSID;
const char* password = STAPSK;

//const char* host = "192.168.1.35";  //marppanet
//const char* host = "192.168.10.34";  //narva
const char* host = "192.168.10.45";  //Herwood
const uint16_t port = 2500;

int adc_val = 0;

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
  Serial.println(NODE_ID);  
  client.print(NODE_ID);

  
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
  for(int i = 0; i < 2;i++){
    Serial.println("sent cmd");
    client.print(node_CMDs[i]);
    delay(50); //TODO Test if neccesary
  }

  Serial.println("Sending END");
  client.print("END");
  //client.receive();
  

  //delay(500);

  
  // finish handshake
  
}

void setup() {

  // Setup LEDs
  pinMode(BUILTIN_LED1, OUTPUT); // Initialize the BUILTIN_LED1 pin as an output
  pinMode(BUILTIN_LED2, OUTPUT); // Initialize the BUILTIN_LED2 pin as an output
  pinMode(D1, OUTPUT); //
  pinMode(D2, OUTPUT); // 
  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED off by making the voltage HIGH
  digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH

  //Setup ADC
  pinMode(A0, INPUT);

  // Setup PWM
  analogWriteFreq(500); //3000 ok
  
  delay(200);
  Serial.begin(9600);
  delay(200);
  Serial.println();
  Serial.println();

  client.setNoDelay(true);
  
  //connectToWifi();
  //connectToServer();
    
}



void loop() {

  adc_val = analogRead(A0);

  if(adc_val > 1000){

    digitalWrite(pwm_pin, HIGH);
    
  }else if(adc_val < 20){

    digitalWrite(pwm_pin, LOW);
        
  }else if(adc_val < 35){
     analogWrite(pwm_pin, 5);
  }else{
    
    analogWrite(pwm_pin, adc_val);
    
  }
  
  Serial.print("ADC: ");
  Serial.println(adc_val);

  

  delay(100);
  
  

  

}


/*

  
  // Listen for incoming nodeCMDs
  if(client.available()){
    digitalWrite(BUILTIN_LED1, LOW); // Turn the LED ON by making the voltage LOW
    data = client.readStringUntil('#');
    digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED ON by making the voltage LOW
    Serial.println(data); 

    // Test cmd
    if(data == "LIGHT_ON"){
  
      digitalWrite(BUILTIN_LED2, LOW); // Turn the LED ON by making the voltage LOW 

      
      digitalWrite(D1, HIGH); // Turn on Relay
      digitalWrite(D2, HIGH); // Turn on IND_LED
      
      client.print("OK");
      
    }else if(data == "LIGHT_OFF"){
      
      digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH

      digitalWrite(D1, LOW); // Turn off Relay
      digitalWrite(D2, LOW); // Turn off IND_LED
      
      client.print("OK");
      
    }else if(data == "PING"){
      
      client.print("PONG");
      
    }else if(data == "NULL"){
  
      client.print("NULL");
      
    }else{
  
      client.print("UNKWNCMD");
      
    }
      
  }else if(!client.connected()){
    Serial.println("Connection to server lost!");
    Serial.println("Waiting for connection...");
    delay(5000);
    if(!client.connected()){
      
      Serial.println("No connection! Reconnecting...");
      connectToServer();
    }
  
  }else if(WiFi.status() != WL_CONNECTED){
    Serial.println("Connection to Wifi lost");
    Serial.println("Waiting for connection...");
    delay(5000);
    if(!client.connected()){
      
      Serial.println("No connection! Rebooting...");
      ESP.restart();
    }
  
  }
  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED ON by making the voltage LOW
  delay(50);




 
 */
