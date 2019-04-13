# Iot_rojekti

Rojekt vor eyeoutee

## Server setup

### Server.conf
File that contains setting used to control server properties and 
behaviour.

<b>NOTICE</b>:This file is not part of git version control as 
the parameters must be set on per server basis. Therefore it must
(currently) be <u>manually created</u> and maintained and 
<u>NEVER BE ADDED to Git.</u>  

Most important ones:

<b>server_IP</b>: Determines the IP address the server 
attempts to use. If running the server on non-server platform 
for development purposes, setting "localhost" can be used. 
<u>This is ONLY FOR DEVELOPMENT and will prevent any outside 
access (e.g. Nodes) to the server!</u> For deployment, set as 
the local IP address of the server machine the server is running
 on e.g. "192.168.1.69".
 
 
<b>TCP_EnablePinging</b>: Setting this to "True" will tell the 
server to ping attached TCP Nodes at a rate set by other pining 
settings as seen in the EXAMPLE_server.conf file. If Node does 
not reply specified amount of pings server will close the 
connection and setNode as disconnected.