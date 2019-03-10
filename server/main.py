# IoT-rojekti Main


from threading import Thread, Lock
import time
from _datetime import datetime

import TCPServer
import ServerUtilities
import UIServer
import EventHandler



running = True

# Port 0 means to select an arbitrary unused port
# HOST, PORT = "localhost", 0
# HOST, PORT = "192.168.1.36", 2500          #MarppaNET
HOST, PORT, UI_PORT = "localhost", 2500, 2600        #local / DEFAULT
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

            # SERVER_ID = params["server_ID"]

            # setting TCPServer params
            tcp_settings.ID = params["server_ID"]
            tcp_settings.pinging = params["TCP_EnablePinging"]
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
    server = TCPServer.ThreadedTCPServer(HOST, PORT, TCPServer.ThreadedTCPRequestHandler, tcp_settings,
                                         s_util, event_hand)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = Thread(target=server.serve_forever)

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

    # Exit the server thread when the main thread terminates
    ui_server_thread.daemon = True
    ui_server_thread.start()

    print("UI server running in thread:", ui_server_thread.name)
    print("ip: ", ip, " port: ", port, "\n")

    return ui_server, ui_server_thread

def start_event_handler(s_util):

    event_hand = EventHandler.EventHandler(s_util)

    event_hand.add_event(10)
    event_hand.get_event(10).add_trigger(1, 666)
    event_hand.get_event(10).add_node_cmd_to_run("1234", "LIGHT_ON")


    return event_hand


# IF MAIN

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

# Start TCP server
TCP_server, TCP_server_thread = start_tcp_server(server_util, event_handler)

# Start UI server
UI_server, UI_server_thread = start_ui_server(server_util)

# start UDP server



server_util.log("Server started")

while running:

    now = datetime.now()
    print("{}:{}:{} Main loop".format(now.hour, now.minute, now.second))
    print("TCP Server running: {}".format(TCP_server_thread.isAlive()))
    print("UI Server running: {}".format(UI_server_thread.isAlive()))
    server_util.list_nodes(True)
    print()


    time.sleep(20)


TCP_server.shutdown()
TCP_server.server_close()

UI_server.shutdown()
UI_server.server_close()
