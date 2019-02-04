import socket
import threading
import socketserver
import time


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    lock = 0
    keepConnection = True
    cmd_buffer = []

    # Acquire threading lock. Prevents multiple threads using server_utils simultaneously
    def get_lock(self):

        cur_thread = threading.current_thread()
        print("{} Requesting Lock \n".format(cur_thread.name))
        self.lock.acquire()
        print("{} Lock acquired".format(cur_thread.name))

    # Release lock.
    def unlock(self):

        self.lock.release()
        print("...released\n")

    # Add a nodeCMD to cmd buffer
    def cdm_to_node(self, cmd):
        self.cmd_buffer.append(cmd)

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
        self.server.server_util.log("New connection: {} -- Client:  {}".format(cur_thread.name, self.client_address))
        print("New client says: {} ".format(data))

        self.send("SEND_ID\n".format(cur_thread.name))

        ID = self.receive()
        print("Received ID: ", ID)

        cmds = []
        self.send("SEND_CMDS\n")
        cmds.append(self.receive())

        while True:
            cmd = self.receive()

            if cmd != "END":
                cmds.append(cmd)
            else:
                break
        print("CMDs received:")
        print(cmds)

        self.server.server_util.attach_node(ID, self, cmds)

        # setup complete
        self.server.server_util.log("Node attached: ID:{}".format(ID))

        # release
        self.unlock()

        # Set "refresh rate" of loop
        self.request.settimeout(60)

        # Go into persistent communication loop
        while self.keepConnection:

            # Send nodeCMD if available
            if self.cmd_buffer:

                self.request.sendall(self.cmd_buffer.pop().encode)

            # Receive (serverCMD) from node if available
            try:
                data = self.request.recv(1024).decode().strip()

            # Nothing received
            except :
                print("(loop) {}: client: {}".format(cur_thread.name, self.client_address))
                print("... no traffic ... \n")

            # Process received
            else:
                print("{}: client: {}".format(cur_thread.name, self.client_address))

                # Splitting data
                data = data.split("/")

                # detect broken socket
                if not data[0]:
                    print("Received empty string!")
                    print(">> Closing socket as broken \n")

                    self.get_lock()
                    self.server.server_util.log("{}: Connection lost, socket broken".format(self.client_address))

                    self.request.close()
                    self.server.server_util.disconnect_node(ID)
                    self.unlock()
                    break

                # Check for termination command
                elif data[0] == 'Q':
                    print("Received terminate command!")
                    print(">> Closing socket \n")

                    self.get_lock()
                    self.server.server_util.log("Client {}: Connection lost, closed by client".format(self.client_address))

                    self.request.close()
                    self.server.server_util.disconnect_node(ID)
                    self.unlock()
                    self.keepConnection = False
                    break

                # Interpret received data /serverCMD
                elif data[0] == "ACTION":
                    self.server.server_util.server_cmd_action(ID, data[1])


                elif data[0] == "VAL_ACTION":

                    self.server.server_util.server_cmd_val_action(ID, data[1], data[2])

                elif data[0] == "BATNOT":

                    self.server.server_util.server_cmd_bat_not(ID, data[1])


                # default / unrecognized
                else:

                    print("Received unsupported serverCMD: {} \n".format(data))

                    # self.get_lock()
                    # something lock-sensitive
                    # self.unlock()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self, H,P,hand, SU):
        socketserver.ThreadingMixIn.__init__(self)
        socketserver.TCPServer.__init__(self,(H,P),hand)
        self.server_util = SU











def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print("Received: {}".format(response.decode()))

    finally:
        sock.close()
