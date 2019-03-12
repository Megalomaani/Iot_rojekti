import datetime

class Node:

    def __init__(self,id, handler, desc="NULL"):
        self.ID = id                    # Unique node ID
        self.connected = True           # is node connected to server
        self.handler = handler          # current handler instance of the connected node
        self.description = desc         # Short description of Node
        self.nodeCMDs = []              # List of available to be performed on the node
        print("Node {} created".format(self.ID))

    def add_node_cmd(self, cmd):
        self.nodeCMDs.append(cmd)

    def set_connected(self, is_connected):
        self.connected = is_connected

    def get_id(self):
        return self.ID

    def is_connected(self):
        return self.connected

    def get_node_cmd_list(self):
        return self.nodeCMDs

    def execute_cmd(self, cmd):
        #print("{} Node passing to handler".format(datetime.datetime.now().time()))
        print("NODE: ID{} CMD{} passing to handler")
        self.handler.cmd_to_node(cmd)

    def dummymethod(self):
        pass

    def debug_get_handler(self):
        return self.handler.debug_get_thread_name()


