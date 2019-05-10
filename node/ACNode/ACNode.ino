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

const String node_CMDs[] = {"FAN_ON", "FAN_OFF", "SET_SPEED?int?45;1000"};


String data = "NULL";
String cmd = "NULL";
int sep_ind = -1;

const char* ssid     = STASSID;
const char* password = STAPSK;

//const char* host = "192.168.1.35";  //marppanet
//const char* host = "192.168.10.34";  //narva
const char* host = "192.168.10.45";  //Herwood
const uint16_t port = 2500;

int adc_values[] = {0,0,0,0,0,0,0,0,0,0};

int adc_val = 0;

int manual_setting = 0;
int automation_setting = 0;
int fanspeed = 0;

int switch_treshold = 200;

bool manual_mode = true;

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
  for(int i = 0; i < 3;i++){
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
  
  connectToWifi();
  connectToServer();
    
}


void read_pot(){

  for(int i = 0; i < 9; i++){
    
    adc_values[i] = adc_values[i+1];    
    
  }

  adc_values[9] = analogRead(A0);

  adc_val = 0;
  
  for(int i = 0; i < 10; i++){
    
    adc_val += adc_values[i];
    
  }

  adc_val = adc_val/10;
  
  Serial.print("ADC: " );
  Serial.print(adc_val);
   
}


void adjust_fans(){

  if(manual_mode){

    manual_setting = adc_val;
    fanspeed = manual_setting;

    
    Serial.print(" <MANUAL> FanSpeed: " );
    Serial.print(fanspeed);
    
  }else{

    if(abs(manual_setting-adc_val) > switch_treshold){
      manual_mode = true;
    }

    fanspeed = automation_setting;

    Serial.print(" <AUTO> FanSpeed: " );
    Serial.print(fanspeed);
   
  }

  if(fanspeed > 1000){

    digitalWrite(pwm_pin, HIGH);
    
  }else if(fanspeed < 40){

    digitalWrite(pwm_pin, LOW);
        
  }else if(fanspeed > 45){
    
    analogWrite(pwm_pin, fanspeed);
    
  }
    
}



void loop() {

  read_pot();
  adjust_fans();
  
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
    if(cmd == "FAN_ON"){        // Turn on fan
  
      digitalWrite(BUILTIN_LED2, LOW); // Turn the LED ON by making the voltage LOW 

      manual_mode = false;

      if(automation_setting < 50){
        automation_setting = 200;
      }
          
      client.print("OK");
      
      
    }else if(cmd == "FAN_OFF"){   // Turn off fan
      
      digitalWrite(BUILTIN_LED2, HIGH); // Turn the LED off by making the voltage HIGH

      manual_mode = false;

      automation_setting = 0;      
      
      client.print("OK");
      
    }else if(cmd == "SET_SPEED"){ // Set fan speed
      
      digitalWrite(BUILTIN_LED2, LOW); // Turn the LED on by making the voltage LOW

      manual_mode = false;

      automation_setting = data.substring(sep_ind + 1).toInt();      
      
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

  digitalWrite(BUILTIN_LED1, HIGH); // Turn the LED OFF by making the voltage HIGH
  delay(20);

}
