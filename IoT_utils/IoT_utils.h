/**
  * Fully open source configurable modular super library
  */

#include "ESP8266WiFi.h"

#ifndef DEBUG
#define DEBUG true
#endif

#define DEBUGPRINTLN(x)    if(DEBUG) { Serial.print("ESP>>> "); Serial.println(x); }

#define USE_HARD_CODED_WIFI_SETTINGS true

#ifndef STASSID
#define STASSID ""
#define STAPSK  ""
#endif

#define NODE_CMD_AMOUNT_MAX 5
#define NODE_CMD_AMOUNT 2

//For ESP-Arduino communication
#define PL_LEN 6
#define CMD_START '#'
#define CMD_STOP '&'

#define MAX_SSID_LEN 32

String handleCommands();

String receive(int timeout = -1);

void connectToWifi();

void connectToServer();

void reconnectWiFi();
void reconnectServer();


bool getWifiLogin(char* ssid, char* password);

void sendCmdSerial(Stream *serial, char cmdChar, char param[]);
bool readCmdSerial(Stream *serial, char cmdArray[], char* readTo, Stream *debugSerial = NULL);
