# IoT-rojekti Main


from threading import Thread, Lock
import time
from _datetime import datetime

import TCPServer
import ServerUtilities


running = True

# Port 0 means to select an arbitrary unused port
# HOST, PORT = "localhost", 0
HOST, PORT = "192.168.1.36", 2500

def start_server_utilities():
    print("Starting ServerUtilities...")
    print("Done")
    return ServerUtilities.ServerUtilities(masterLock)


def start_tcp_server(s_util):

    print("Starting TCP server ...")
    server = TCPServer.ThreadedTCPServer(HOST, PORT, TCPServer.ThreadedTCPRequestHandler, s_util)
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


# IF MAIN

# Start dataDaemon
pass

# Start TGUI
pass

# Start ServerUtilities
masterLock = Lock()
server_util = start_server_utilities()

# Start TCP server
TCP_server, TCP_server_thread = start_tcp_server(server_util)

# start UDP server

server_util.log("Server started")

while running:

    now = datetime.now()
    print("{}:{}:{} Main loop".format(now.hour, now.minute, now.second))
    print("TCP Server running: {}".format(TCP_server_thread.isAlive()))
    server_util.list_nodes(True)
    print()


    time.sleep(20)


TCP_server.shutdown()
TCP_server.server_close()


