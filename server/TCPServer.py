import socket
import threading
import socketserver
import time


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()

        self.lock = self.server.server_util.get_lock()

        print("New connection: {} -- Client:  {}".format(cur_thread.name, self.client_address))
        print("Received: {} ".format(data))

        self.server.server_util.log("new connection!")

        response = "{}: Hello to you too! \n".format(cur_thread.name).encode()
        self.request.sendall(response)

        self.request.settimeout(60)

        while data != 'Q':

            try:
                data = self.request.recv(1024).decode().strip()

            except :
                print("(loop) {}: client: {}".format(cur_thread.name, self.client_address))
                print("... no traffic ... \n")

            else:
                print("{}: client: {}".format(cur_thread.name, self.client_address))

                # detect broken socket
                if not data:
                    print("Received empty string!")
                    print(">> Closing socket as broken \n")

                    print("{} Requesting Lock".format(cur_thread.name))
                    self.lock.acquire()
                    print("{} Lock acquired".format(cur_thread.name))
                    self.server.server_util.log("{}: Connection lost, socket broken".format(self.client_address))
                    self.lock.release()
                    print("...released")
                    self.request.close()
                    break

                elif data == 'Q':
                    print("Received terminate command!")
                    print(">> Closing socket \n")

                    self.server.server_util.log("Client {}: Connection lost, closed by client".format(self.client_address))

                    self.request.close()
                    break

                else:
                    print("{} Requesting Lock".format(cur_thread.name))
                    self.lock.acquire()
                    print("{} Lock acquired".format(cur_thread.name))

                    print("Received: {} \n".format(data))
                    time.sleep(20)
                    self.lock.release()
                    print("...released")


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
