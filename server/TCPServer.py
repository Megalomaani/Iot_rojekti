import socket
import threading
import socketserver
import time


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()

        print("New connection: {} -- Client:  {}".format(cur_thread.name, self.client_address))
        print("Received: {} ".format(data))

        response = "{}: Hello to you too! \n".format(cur_thread.name).encode()
        self.request.sendall(response)

        self.request.settimeout(60)

        while data != 'Q':



            try:
                data = self.request.recv(1024).decode().strip()
                print("(loop) {}: client: {}".format(cur_thread.name, self.client_address))

            except:
                print("(loop) {}: client: {}".format(cur_thread.name, self.client_address))
                print("... no traffic ...")

            else:
                if not data:
                    print("Received empty string!")
                    print(">>Closing socket as broken")
                    self.request.close()
                    break

                print("Received: {} ".format(data))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, H,P,hand, testi):
        socketserver.ThreadingMixIn.__init__(self)
        socketserver.TCPServer.__init__(self,(H,P),hand)
        print(testi)



def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print("Received: {}".format(response.decode()))


    finally:
        sock.close()
