#include "IoT_utils.h"

char cd[] = "LCGSP";      //ESP-Arduino commands
String data = "NULL";     //data read from command

char sid[MAX_SSID_LEN];
char sala[MAX_SSID_LEN];

extern String node_id;
extern String node_CMDs[NODE_CMD_AMOUNT_MAX];
extern uint8_t node_cmd_amount;

WiFiClient client;

#if USE_HARD_CODED_WIFI_SETTINGS
const char* ssid     = STASSID;
const char* password = STAPSK;
#endif



const char* host = SERVER_HOST;
const uint16_t port = SERVER_PORT;


String handleCommands(){

  if(client.available()){

    data = client.readStringUntil('#');
    Serial.print("Received data: ");
    Serial.println(data);

    // Test cmd
    for (uint8_t i = 0; i < node_cmd_amount; i++) {
      if(data == node_CMDs[i]){
        client.print("OK");
        return node_CMDs[i];
      }
    }

    if(data == "PING"){

      client.print("PONG");

    }else if(data == "NULL"){

      client.print("NULL");

    }else{

      client.print("UNKWNCMD");

    }

  }
  return "";

}




String receive(int timeout/* = -1*/){
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


#if USE_HARD_CODED_WIFI_SETTINGS

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

#else

  DEBUGPRINTLN("Connecting to ");
  //DEBUGPRINTLN(ssid);

  WiFi.mode(WIFI_STA);


  WiFi.begin();


  while ( WiFi.status() != WL_CONNECTED ){
    uint8_t i = 0;
    while (WiFi.status() != WL_CONNECTED && i < 20) {
      delay(500);
      DEBUGPRINTLN(".");
      ++i;
    }
    //timeout
    kysyTunnukset(sid,sala);
    char* a = sid;
    ++a;
    char* b = sala;
    ++b;
    if ( WiFi.status() != WL_CONNECTED) WiFi.begin(a,b);
    DEBUGPRINTLN("Got new wifi settings:");
    DEBUGPRINTLN(a);
    DEBUGPRINTLN(b);
  }
  DEBUGPRINTLN();

  DEBUGPRINTLN("WiFi connected");
  DEBUGPRINTLN("IP address: ");
  DEBUGPRINTLN(WiFi.localIP());

#endif
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
  Serial.println(node_id);
  client.print(node_id);


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
  for(int i = 0; i < node_cmd_amount;i++){
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

void reconnectWiFi(){
  if(WiFi.status() != WL_CONNECTED){
    Serial.println("Connection to Wifi lost");
    Serial.println("Waiting for connection...");
    delay(5000);
    if(!client.connected()){

      Serial.println("No connection! Rebooting...");
      ESP.restart();
    }
  }
}

void reconnectServer(){
  if(!client.connected()){
    Serial.println("Connection to server lost!");
    Serial.println("Waiting for connection...");
    delay(5000);
    if(!client.connected()){

      Serial.println("No connection! Reconnecting...");
      connectToServer();
    }

  }
}

//Asks for wifi login info from Arduino via uart

bool getWifiLogin(char* ssid, char* password){

  ssid[0] = '\0';
  password[0] = '\0';

  DEBUGPRINTLN("Kysy ssid");
  char p[] = "";
  sendCmdSerial(&Serial, 'G', p);
  delay(10);
  while ( !readCmdSerial(&Serial, cd, ssid, NULL) ){
    if ( ssid[0] == 'S'){
      break;
    }
  }
  delay(50);
  DEBUGPRINTLN("Kysy salasana");
  while ( !readCmdSerial(&Serial, cd, password, NULL) ){
    if ( password[0] == 'P'){
      break;
    }
  }


}

bool readCmdSerial(Stream *serial, char cmdArray[], char* readTo, Stream *debugSerial /*=NULL*/){


  if ( serial->available() ){

    //char buf[PL_LEN + 2];

    while(serial->available()) {

      char c1 = (char)serial->read();

      if(  c1 == CMD_START ){
        //go on

        delay(10);
        char c2 = (char)serial->read();

        for ( int i = 0 ; i < strlen(cmdArray) ; ++i ){

          if ( c2 == cmdArray[i] ){

            readTo[0] = cmdArray[i];
            delay(50);
            for( int n = 1 ; n < MAX_SSID_LEN + 2 ; ++n){  //lue parametrit, maks. pituus on maks. wlan tunnusten pituus

                char c3 = (char)serial->read();

                if (c3 == CMD_STOP){
                  readTo[n] = '\0';
                  return true;
                }

                readTo[n] = c3;
            }
            return false;

          }
        }
        if (debugSerial != NULL)
          debugSerial->print(c1);
          debugSerial->print(c2);


      } else if( debugSerial != NULL){
        debugSerial->print(c1);
      }

    }
  }
  return false;
}

void sendCmdSerial(Stream *serial, char cmdChar, char param[]) {

  char kom[MAX_SSID_LEN + 4];

  sprintf(kom, "%c%c%s%c", CMD_START, cmdChar, param, CMD_STOP);

  serial->print(kom);

}
