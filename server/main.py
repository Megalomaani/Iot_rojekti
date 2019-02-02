# Tästä se lähtee


import threading
import TCPServer

print("Hello world")


# Port 0 means to select an arbitrary unused port
# HOST, PORT = "localhost", 0
HOST, PORT = "192.168.1.36", 2500

server = TCPServer.ThreadedTCPServer((HOST, PORT), TCPServer.ThreadedTCPRequestHandler)
ip, port = server.server_address

# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = threading.Thread(target=server.serve_forever)
# Exit the server thread when the main thread terminates
server_thread.daemon = True
server_thread.start()
print("Server loop running in thread:", server_thread.name)
print("ip: ", ip, " port: ", port, "\n")

TCPServer.client(ip, port, "Hello World 1".encode())
TCPServer.client(ip, port, "Hello World 2".encode())
TCPServer.client(ip, port, "Hello World 3".encode())

server.shutdown()
server.server_close()
