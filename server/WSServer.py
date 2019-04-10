import socket
import threading
import socketserver
import time
import datetime

import socketserver
import hashlib
import base64

import json
import struct

from time import sleep

WS_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WSThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

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

        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).decode().strip()

        self.server.server_util.log("WSServer: New connection: {} -- WS Client:  {}".format(threading.current_thread()
                                                                                            .name, self.client_address))

        print(self.data)

        headers = self.data.split("\r\n")

        # is it a websocket request?
        if ("Connection: keep-alive, Upgrade" in self.data or "Connection: Upgrade" in self.data) \
                                                                                and "Upgrade: websocket" in self.data:


            print("\nIs correct WS Request!!\n")

            # getting the websocket key out
            for h in headers:
                if "Sec-WebSocket-Key" in h:
                    key = h.split(" ")[1]

            self.shake_hand(key)

            while True:

                try:
                    rawReceive = bytearray(self.request.recv(1024).strip())
                    payload = self.decode_frame(rawReceive)
                    decoded_payload = payload.decode('utf-8')
                    print("WSServer ({}):  RECEIVED: {}".format(threading.current_thread().name, decoded_payload))

                    received = decoded_payload.split("/")
                    print(received)

                    # self.send_frame("{} to you too! BR, {}".format(decoded_payload, threading.current_thread().name).encode('utf-8'))

                    # Attempt to interpret received data
                    try:

                        if received[0] == "GET":
                            # self.send_frame("Received GET".encode('utf-8'))

                            if received[1] == "NODE_INFO":
                                node_info = {
                                    "TCP_NODES": [
                                        {"ID": "1234", "CMDS": ["LIGHT_ON", "LIGHT_OFF"]},
                                        {"ID": "666", "CMDS": ["LIGHT_ON", "LIGHT_OFF"]}
                                    ]
                                }

                                #self.send_frame("NODE_INFO/{}".format(json.dumps(node_info)).encode('utf-8'))
                                self.get_lock()
                                self.send_frame("NODE_INFO/{}".format(self.server.server_util.get_node_json()).encode('utf-8'))
                                self.unlock()


                        elif received[0] == "CMD":
                            print("Received CMD")
                            # print("{} UI processed".format(datetime.datetime.now().time()))
                            self.send_frame("Got Node_CMD\n".encode('utf-8'))
                            self.get_lock()
                            # print("{} UI locked + passing to util".format(datetime.datetime.now().time()))
                            ok_msg = self.server.server_util.send_cmd_to_node(received[1], received[2])
                            print("UI SERVER: Node_CMD attempt went: {}".format(ok_msg))
                            self.send_frame(ok_msg.encode('utf-8'))

                            self.unlock()


                    except Exception as e:

                        print("ERROR! Failed to interpret received data")
                        print(e)

                    try:

                        received_json = json.loads(decoded_payload)
                        print("WSServer: Received JSON:")
                        print(received_json)

                    except:
                        print("WSServer: Received not JSON!")


                except:
                    print("WSServer ({}):  CONNECTION BROKEN".format(threading.current_thread().name))
                    return

                if "bye" == decoded_payload.lower():
                    "Bidding goodbye to our client..."
                    return
        else:
            print("INVALID REQUEST")
            self.request.sendall(("HTTP/1.1 400 Bad Request\r\n" + \
                                  "Content-Type: text/plain\r\n" + \
                                  "Connection: close\r\n" + \
                                  "\r\n" + \
                                  "Incorrect request").encode('utf-8'))

    def shake_hand(self,key):
        # calculating response as per protocol RFC
        key = key + WS_MAGIC_STRING
        resp_key = base64.standard_b64encode(hashlib.sha1(key.encode('utf-8')).digest()).decode('utf-8')

        resp=("HTTP/1.1 101 Switching Protocols\r\n" + \
             "Upgrade: websocket\r\n" + \
             "Connection: Upgrade\r\n" + \
             "Sec-WebSocket-Accept: %s\r\n\r\n"%(resp_key)).encode('utf-8')

       # print("Responding:\n{}".format(resp))
       # print()

        self.request.sendall(resp)

    def decode_frame(self,frame):
        opcode_and_fin = frame[0]

        # assuming it's masked, hence removing the mask bit(MSB) to get len. also assuming len is <125
        payload_len = frame[1] - 128

        mask = frame [2:6]
        encrypted_payload = frame [6: 6+payload_len]

        payload = bytearray([ encrypted_payload[i] ^ mask[i%4] for i in range(payload_len)])

        return payload

    def send_frame(self, payload):

        plen = len(payload)

        if plen <= 125:
            print("Payload length: {}".format(plen))
            # setting fin to 1 and opcpde to 0x1
            frame = [129]
            # adding len. no masking hence not doing +128
            frame += [len(payload)]
            # adding payload
            frame_to_send = bytearray(frame) + payload

            print(frame)
            print(bytearray(frame))
            print(frame_to_send)

            self.request.sendall(frame_to_send)

        elif plen <= 65000:

            print("Long payload! Length: {}".format(plen))

            # setting fin to 1 and opcpde to 0x1
            frame = [129]
            # adding indication of long message
            frame += [126]
            # adding len of long message
            b = struct.pack('<H', len(payload))
            frame += [b[1]]
            frame += [b[0]]
            # adding payload
            frame_to_send = bytearray(frame) + payload

            print(frame_to_send)

            self.request.sendall(frame_to_send)

        else:
            print("TOO LONG payload! Length: {}".format(plen))


class WSThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self, H,P,hand, SU):
        socketserver.ThreadingMixIn.__init__(self)
        socketserver.TCPServer.__init__(self,(H,P),hand)
        self.server_util = SU

