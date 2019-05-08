import socket
import threading
import socketserver
import datetime


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    lock = 0
    keepConnection = True
    cmd_buffer = []     # NOT IN USE!
    toggle = True
    ID = 0

    pinging = False      # Test node connection by pinging
    pingRate = 9999       # loops in between pings
    pingMaxTime = 0     # seconds to wait for response
    pingMissCutout = 9999  # Allowed ping misses before closing connection
    loopsSincePing = 0
    pingsMissed = 0

    # Acquire threading lock. Prevents multiple threads using server_utils simultaneously
    def get_lock(self):

        cur_thread = threading.current_thread()
        print("TCP {} Requesting Lock \n".format(cur_thread.name))
        self.lock.acquire()
        print("TCP {} Lock acquired".format(cur_thread.name))

    # Release lock.
    def unlock(self):

        self.lock.release()
        print("...released\n")

    def debug_get_thread_name(self):
        return threading.current_thread().name

    def set_params(self):
        self.ID = self.server.ID

        self.pinging = self.server.pinging
        self.pingRate = self.server.pingRate
        self.pingMaxTime = self.server.pingMaxTime
        self.pingMissCutout = self.server.pingMissCutout

    # Send message to node
    def send(self, msg):
        self.request.sendall("{}#".format(msg).encode())

    # Receive from node
    def receive(self, retry=False, retry_count=10, timeout=0):



        # save current timeout if different one is used
        oldTimeout = self.request.timeout
        if timeout:
            self.request.settimeout(timeout)

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
                    data = "NULL"
                    i += i
                    if i == retry_count:
                        break

        if timeout:
            self.request.settimeout(oldTimeout)

        return data

    def ping(self):

        # Ping node if conditions are met (maybe move to end of loop to improve reactivenes)
        if self.pinging is True and self.loopsSincePing == self.pingRate:
            self.send("PING")
            self.loopsSincePing = 0
            print("SENT PING")

            # ping
            if self.receive(timeout=self.pingMaxTime) == "PONG":
                self.pingsMissed = 0
                print("GOT PONG")

            else:
                self.pingsMissed += 1
                print("NO RESPONSE!")

            # Disconnect if too many missed pings
            if self.pingsMissed > self.pingMissCutout:
                self.get_lock()
                print("Disconnecting Node: {} IP: {} due to missed pings!".format(self.ID, self.client_address))
                # TODO: Log this
                self.server.server_util.disconnect_node(self.ID)
                self.keepConnection = False
                self.unlock()
        elif self.pinging is True:
            self.loopsSincePing += 1
            # print("No Ping, loop {} , pingRate {}".format(self.loopsSincePing, self.pingRate))

    # Handler for individual connection. The good stuff
    def handle(self):

        # read connection parameters from server
        self.set_params()

        # Setup thread ref and lock
        cur_thread = threading.current_thread()
        self.lock = self.server.server_util.get_master_lock()

        # Read initial message
        data = self.request.recv(1024).decode()


        # Process and log new connection
        self.get_lock()
        self.server.server_util.log("New connection: {} -- Client:  {}".format(cur_thread.name, self.client_address))
        print("New client says: {} ".format(data))

        self.send("SEND_ID")

        self.ID = self.receive()
        print("Received ID: ", self.ID)

        cmds = []
        self.send("SEND_CMDS")
        cmds.append(self.receive())

        while True:
            cmd = self.receive()

            if cmd != "END":
                cmds.append(cmd)
            else:
                break
        print("CMDs received:")
        print(cmds)

        self.server.server_util.attach_node(self.ID, cur_thread, cmds)

        # setup complete
        self.server.server_util.log("Node attached: ID:{}".format(self.ID))

        # release
        self.unlock()

        # Set "refresh rate" of loop
        self.request.settimeout(1)

        # EXPERIMENTAL!!! Aims to reduce lag
        self.request.setblocking(0)

        # Go into persistent communication loop
        while self.keepConnection:

            # print("{} {} loop".format(datetime.datetime.now().time(), cur_thread.name))

            # Pinging (if enabled)
            self.ping()

            # Send nodeCMD if available
            # Check for nodeCMDs in buffer
            cmd = self.server.server_util.get_next_cmd(self.ID)

            while cmd is not None:

                self.send(cmd)

                # New cmd
                cmd = self.server.server_util.get_next_cmd(self.ID)

                response =  "NULL" ##self.receive(timeout=2)
                if response == "NULL":
                    #print("No response to {}\n".format(cmdToSend))
                    pass

                elif response == "ERROR":
                    #print("NodeCMD  {} produced an error!\n".format(cmdToSend))
                    pass

                elif response == "OK":
                    #print("NodeCMD  {} successful\n".format(cmdToSend))
                    pass

            # Receive (serverCMD) from node if available
            data = self.receive(timeout=1)

            # Nothing received
            if data == "NULL":
                """"
                print("... no traffic from node ... \n")
                # Toggle node light for debug reasons
                if self.toggle:
                    self.cmd_buffer.append("LIGHT_ON")
                    self.toggle = False
                else:
                    self.cmd_buffer.append("LIGHT_OFF")
                    self.toggle = True
                """
                pass

            # Process received
            else:
                print("Node {}: {}:".format(self.ID, cur_thread.name))

                # Splitting data
                data = data.split("/")

                # detect broken socket
                if not data[0]:
                    print("Received empty string!")
                    print(">> Closing socket as broken \n")

                    self.get_lock()
                    self.server.server_util.log("{}: Connection lost, socket broken".format(self.client_address))

                    self.request.close()
                    self.server.server_util.disconnect_node(self.ID)
                    self.unlock()
                    break

                # Check for termination command
                elif data[0] == 'Q':
                    print("Received terminate command!")
                    print(">> Closing socket \n")

                    self.get_lock()
                    self.server.server_util.log("Client {}: Connection lost, closed by client".format(self.client_address))

                    self.request.close()
                    self.server.server_util.disconnect_node(self.ID)
                    self.unlock()
                    self.keepConnection = False
                    break

                # Interpret received data /serverCMD
                elif data[0] == "ACTION":
                    self.get_lock()
                    self.server.server_util.server_cmd_action(self.ID, data[1])
                    self.server.event_handler.node_trigger(self.ID, data[1])
                    self.unlock()

                elif data[0] == "VAL_ACTION":
                    self.get_lock()
                    self.server.server_util.server_cmd_val_action(self.ID, data[1], data[2])
                    self.unlock()

                elif data[0] == "BATNOT":
                    self.get_lock()
                    self.server.server_util.server_cmd_bat_not(self.ID, data[1])
                    self.unlock()

                # default / unrecognized
                else:

                    # print("{} ACK Received".format(datetime.datetime.now().time()))
                    print("Received unsupported serverCMD: {} \n".format(data))

                    # self.get_lock()
                    # something lock-sensitive
                    # self.unlock()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self, H, P, hand, settings, SU, event_hand):
        socketserver.ThreadingMixIn.__init__(self)
        socketserver.TCPServer.__init__(self, (H, P), hand)
        self.server_util = SU
        self.ID = settings.ID
        self.event_handler = event_hand

        # Pinging settings
        self.pinging = settings.pinging
        self.pingRate = settings.pingRate
        self.pingMaxTime = settings.pingMaxTime
        self.pingMissCutout = settings.pingMissCutout


class TCPSettings:

    # Server parameters
    ID = 0

    # Pinging settings
    pinging = False  # Test node connection by pinging
    pingRate = 20  # loops in between pings
    pingMaxTime = 3  # seconds to wait for response
    pingMissCutout = 5  # Allowed ping misses before closing connection

    def __init__(self):
        pass
