import socket
import threading
import socketserver
import time


class UIThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    lock = 0
    keepConnection = True
    cmd_buffer = []
    toggle = True

    # Acquire threading lock. Prevents multiple threads using server_utils simultaneously
    def get_lock(self):

        cur_thread = threading.current_thread()
        print("UI {} Requesting Lock \n".format(cur_thread.name))
        self.lock.acquire()
        print("UI {} Lock acquired".format(cur_thread.name))

    # Release lock.
    def unlock(self):

        self.lock.release()
        print("...released\n")


    def send(self, msg):
        self.request.sendall(msg.encode())

    def receive(self, retry=False, retry_count=10):

        # Receive from node if available
        try:
            data = self.request.recv(1024).decode().strip()

        # Nothing received
        except:

            data = "NULL"

            while retry:
                # Receive from node if available
                i = 0
                try:
                    data = self.request.recv(1024).decode().strip()

                # Nothing received
                except:
                    i += i
                    if i == retry_count:
                        return data

                # Successful read
                else:
                    return data

        # Successful read
        else:
            return data

    # Handler for individual connection. The good stuff
    def handle(self):

        # Setup thread ref and lock
        cur_thread = threading.current_thread()
        self.lock = self.server.server_util.get_master_lock()

        # Read initial message
        data = self.request.recv(1024).decode()

        # set timeout for read (TIMEOUT THROWS ERROR!)
        # self.request.settimeout(60)

        # Process and log new connection
        self.get_lock()
        self.server.server_util.log("New connection: {} -- UI Client:  {}".format(cur_thread.name, self.client_address))
        print("New client says: {} ".format(data))

        self.send("Connected to server\n")
        self.send("Enter command...\n")

        # release
        self.unlock()

        # Set "refresh rate" of loop
        self.request.settimeout(30)

        # Go into persistent communication loop
        while self.keepConnection:

            # Receive (serverCMD) from node if available
            try:
                data = self.request.recv(1024).decode().strip()

            # Nothing received
            except :
                print("(loop) {}: UI Client: {}".format(cur_thread.name, self.client_address))
                print("... no traffic ... \n")

            # Process received
            else:
                print("{}: UI Client: {}".format(cur_thread.name, self.client_address))

                # Splitting data
                data = data.split("/")

                # detect broken socket
                if not data[0]:
                    print("Received empty string!")
                    print(">> Closing socket as broken \n")

                    self.get_lock()
                    self.server.server_util.log("UI Client{}: Connection lost, socket broken".format(self.client_address))

                    self.request.close()
                    #self.server.server_util.disconnect_node(ID)
                    self.unlock()
                    break

                # Check for termination command
                elif data[0] == 'Q':
                    print("Received terminate command!")
                    print(">> Closing socket \n")

                    self.get_lock()
                    self.server.server_util.log("UI Client {}: Connection lost, closed by UI Client".format(self.client_address))

                    self.request.close()
                    #self.server.server_util.disconnect_node(ID)
                    self.unlock()
                    self.keepConnection = False
                    break

                # Interpret received data /serverCMD
                elif data[0] == "ACTION":
                    self.send("Got ACTION\n")
                    #self.server.server_util.server_cmd_action(ID, data[1])


                elif data[0] == "VAL_ACTION":

                    self.send("Got VAL_ACTION\n")
                    #self.server.server_util.server_cmd_val_action(ID, data[1], data[2])

                elif data[0] == "LS":

                    self.get_lock()
                    if len(data) == 2:
                        if data[1] == "A":
                            self.send("Attached TCP nodes:\n")
                            for n_id in self.server.server_util.get_tcp_node_list():
                                self.send("{}\n".format(n_id))
                                for n_cmd in self.server.server_util.get_node_cmds(n_id):
                                    self.send(" -{}\n".format(n_cmd))

                    else:
                        self.send("Attached TCP nodes:\n")
                        for n_id in self.server.server_util.get_tcp_node_list():
                            self.send("{}\n".format(n_id))

                    self.send("\n")
                    self.unlock()

                # Node_CMD
                elif data[0] == "CMD":
                    self.send("Got Node_CMD\n")
                    self.get_lock()
                    ok_msg = self.server.server_util.send_cmd_to_node(data[1], data[2])
                    print("UI SERVER: Node_CMD attempt went: {}".format(ok_msg))
                    self.send(ok_msg)
                    self.send("\n")
                    self.unlock()

                # default / unrecognized
                else:
                    self.send("UNSUPPORTED COMMAND!\n")
                    print("Received unsupported serverCMD: {} \n".format(data))

                    # self.get_lock()
                    # something lock-sensitive
                    # self.unlock()


class UIThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self, H,P,hand, SU):
        socketserver.ThreadingMixIn.__init__(self)
        socketserver.TCPServer.__init__(self,(H,P),hand)
        self.server_util = SU


