# IoT-rojekti Main


from threading import Thread, Lock, enumerate
import time
#import subprocess
from _datetime import datetime
import ast


import TCPServer
import ServerUtilities
import UIServer
import WSServer
import EventHandler
import Alarm
import PhonePing
#import speech


running = True

# Port 0 means to select an arbitrary unused port
# HOST, PORT = "localhost", 0
# HOST, PORT = "192.168.1.36", 2500          #MarppaNET
HOST, PORT, UI_PORT, WS_PORT = "localhost", 2500, 2600, 2700        #local / DEFAULT
SERVER_ID = "00000000"      # default, overwritten by param read
tcp_settings = 0


def read_server_config():

    global HOST
    global PORT
    global SERVER_ID
    global tcp_settings

    params = {}
    # Creating TCPServer settings object
    tcp_settings = TCPServer.TCPSettings()


    try:
        f = open("server.conf", "r")
        print("server.conf found")

        for line in f:
            if line[0] == "#" or line[0] == "\n":
                continue
            else:
                splitted = line.split("=")
                params[splitted[0]] = splitted[1][:-1]

        print("Server parameters:")
        print(params)


        try:
            if params["server_IP"] != "localhost":
                HOST = params["server_IP"]

            PORT = int(params["TCP_port"])

            SERVER_ID = params["server_ID"]

            # setting TCPServer params
            tcp_settings.ID = params["server_ID"]
            tcp_settings.pinging = ast.literal_eval(params["TCP_EnablePinging"])
            tcp_settings.pingMissCutout = int(params["TCP_pingMissCutout"])
            tcp_settings.pingMaxTime = int(params["pingMaxTime"])
            tcp_settings.pingRate = int(params["pingRate"])

            # Parameters successfully set
            print("Server parameters set")

        except Exception as e1:
            print("parameter setup FAILED:")
            print(e1)
            print("\n => SERVER RUNNING WITH DEFAULT PARAMETERS! \n")

            # set adjusted parameters to default
            HOST, PORT = "localhost", 2500
            SERVER_ID = "00000000"

        # close file after done
        f.close()

    except Exception as e:
        print("server.conf read FAILED")
        print(e)
        print("\n => SERVER RUNNING WITH DEFAULT PARAMETERS! \n")

        # set adjusted parameters to default
        HOST, PORT = "localhost", 2500
        SERVER_ID = "00000000"

    print("Starting server, ID: ", SERVER_ID, "\n")


def start_server_utilities():
    print("Starting ServerUtilities...")
    print("Done")
    return ServerUtilities.ServerUtilities(masterLock)


def start_tcp_server(s_util, event_hand):

    print("Starting TCP server ...")
    print("Server parameters:")
    print("server_ID: {}".format(tcp_settings.ID))
    print("TCP_EnablePinging: {}".format(tcp_settings.pinging))
    print("TCP_pingMissCutout: {}".format(tcp_settings.pingMissCutout))
    print("pingMaxTime: {}".format(tcp_settings.pingMaxTime))
    print("pingRate: {}".format(tcp_settings.pingRate))

    server = TCPServer.ThreadedTCPServer(HOST, PORT, TCPServer.ThreadedTCPRequestHandler, tcp_settings,
                                         s_util, event_hand)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = Thread(target=server.serve_forever)
    server_thread.setName("TCP_ServerThread")

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    print("TCP server running in thread:", server_thread.name)
    print("ip: ", ip, " port: ", port, "\n")


    return server, server_thread

def start_ui_server(s_util):

    print("Starting UI server ...")
    ui_server = UIServer.UIThreadedTCPServer(HOST, UI_PORT, UIServer.UIThreadedTCPRequestHandler, s_util)
    ip, port = ui_server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    ui_server_thread = Thread(target=ui_server.serve_forever)
    ui_server_thread.setName("UI_ServerThread")

    # Exit the server thread when the main thread terminates
    ui_server_thread.daemon = True
    ui_server_thread.start()

    print("UI server running in thread:", ui_server_thread.name)
    print("ip: ", ip, " port: ", port, "\n")

    return ui_server, ui_server_thread


def start_ws_server(s_util):

    print("Starting WS server ...")
    ws_server = WSServer.WSThreadedTCPServer(HOST, WS_PORT, WSServer.WSThreadedTCPRequestHandler, s_util)
    ip, port = ws_server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    ws_server_thread = Thread(target=ws_server.serve_forever)
    ws_server_thread.setName("WSS_ServerThread")

    # Exit the server thread when the main thread terminates
    ws_server_thread.daemon = True
    ws_server_thread.start()

    print("WS server running in thread:", ws_server_thread.name)
    print("ip: ", ip, " port: ", port, "\n")

    return ws_server, ws_server_thread

def start_event_handler(s_util):

    event_hand = EventHandler.EventHandler(s_util)

    event_hand.add_event(10)
    event_hand.get_event(10).add_trigger(1, 666)
    event_hand.get_event(10).add_node_cmd_to_run("1234", "LIGHT_ON")

    event_hand.add_event(11)
    event_hand.get_event(11).add_trigger(1, 69)
    event_hand.get_event(11).add_node_cmd_to_run("1234", "ALARM MOTHERFUCKER")

    return event_hand

def start_alarm(event_hand):

    alarm = Alarm.Alarm(event_hand.node_trigger, 69, 1)
    #alarms should not be set here
    alarm.setAlarm("a", [0], 13, 51, "no")
    alarm.setAlarm("b", [0], 13, 55, "no")

    return alarm

def start_phone_pinger(event_hand):

    pinger = PhonePing.wifiPinger("10.42.0.102", event_hand.node_trigger, 69, 1)
    return pinger

def speechCallback(phrase, event_hand):

    if phrase == "light on":
        event_hand.node_trigger(69, 1)



# IF MAIN

if __name__ == "__main__":

    # Read server configuration from file
    read_server_config()

    # Start dataDaemon
    pass

    # Start TGUI
    pass

    # Start ServerUtilities
    masterLock = Lock()
    server_util = start_server_utilities()

    # start EventHandler
    event_handler = start_event_handler(server_util)

    alarm = start_alarm(event_handler)

    #pinger = start_phone_pinger(event_handler)

    #s = speech.SpeechRecognizer5000(speechCallback, event_handler)
    #time.sleep(2)
    #s.startListening()

    # Start TCP server
    TCP_server, TCP_server_thread = start_tcp_server(server_util, event_handler)

    # Start UI server
    UI_server, UI_server_thread = start_ui_server(server_util)

    # Start WS server
    WS_server, WS_server_thread = start_ws_server(server_util)

    # start UDP server
    pass

    # DEBUG Add Dummy nodes
    if True:
        server_util.attach_node("dummy_1", "NO_THREAD", ["LIGHT_ON", "LIGHT_OF"])
        server_util.attach_node("dummy_2", "NO_THREAD", ["MAKE_RAIN", "DO_THING"])

    server_util.log("Server started")

    while running:

        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        now = datetime.now()
        print("{}:{}:{} Main loop".format(now.hour, now.minute, now.second))
        print("TCP Server running: {}".format(TCP_server_thread.isAlive()))
        print("UI Server running: {}".format(UI_server_thread.isAlive()))
        server_util.list_nodes(True)
        print("---------------------")
        print("Threads running:")
        for thrd in enumerate():
            print(thrd.name)
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

        time.sleep(10)


    TCP_server.shutdown()
    TCP_server.server_close()

    UI_server.shutdown()
    UI_server.server_close()
