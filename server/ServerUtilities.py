# ServerUtilities - all the useful stuff

import datetime
from node import Node


class ServerUtilities:

    # Dict of TCP nodes in system
    serverCMDs = ["ACTION", "VAL_ACTION"]

    # Buffer for outgoing nodeCMDs

    cmdBuffer = {}

    def __init__(self, mlock):
        self.masterLock = mlock
        self.TCP_nodes = {}

    def log(self, logEntry):
        now = datetime.datetime.now()
        stamped_logEntry = "{}: {}".format(now, logEntry)
        ##TODO dataDaemon
        print("Logged: ", stamped_logEntry, "\n")

    def get_master_lock(self):
        return self.masterLock

    def attach_node(self, node_id, handler, cmds):

        # Node is already in system
        if node_id in self.TCP_nodes.keys():

            self.TCP_nodes[node_id].set_connected(True)

        # New node, create it in system
        else:
            self.TCP_nodes[node_id] = Node(node_id, handler)
            self.cmdBuffer[node_id] = []

            for cmd in cmds:
                self.TCP_nodes[node_id].add_node_cmd(cmd)

    # Mark node as inactive and disconnected
    def disconnect_node(self, node_id):

        self.TCP_nodes[node_id].set_connected(False)

    def list_nodes(self,show_cmds=False):
        print("Nodes:")
        for nd in self.TCP_nodes.values():
            print("ID: {} {} (Connected: {})".format(nd.get_id(),nd.debug_get_handler(), nd.is_connected()))
            if show_cmds:
                for cmd in nd.get_node_cmd_list():
                    print("  {}".format(cmd))

    def get_tcp_node_list(self):
        return self.TCP_nodes.keys()

    def get_active_tcp_node_list(self):

        activeNodes = []

        for nd in self.TCP_nodes.keys():
            if self.TCP_nodes[nd].is_connected():
                activeNodes.append(nd)

        return activeNodes



    def get_node_cmds(self, node_id):
        if node_id in self.TCP_nodes.keys():
            return self.TCP_nodes[node_id].get_node_cmd_list()
        else:
            return ["INVALID NODE_ID"]


    # SERVER_CMDS

    def server_cmd_action(self, node_id, action_id):
        print("Node {} sent ACTION {}".format(node_id, action_id))

    def server_cmd_val_action(self, node_id, action_id, value):
        print("Node {} sent ACTION {} with value {}".format(node_id, action_id, value))

    # Battery notification BATNOT
    def server_cmd_bat_not(self, node_id, batteryLevel):
        print("Node {} sent Battery notification: Level:{}".format(node_id, batteryLevel))

    # NODE_CMDS

    def send_cmd_to_node(self, node_id, node_cmd):
        try:
            #print("{} SU passing to node".format(datetime.datetime.now().time()))
            print("command {} to ID {}".format(node_cmd, node_id))
            self.TCP_nodes[node_id].execute_cmd(node_cmd)
            self.cmdBuffer[node_id].append(node_cmd)
            return "OK"

        except Exception as e:
            print(e)
            print("Server utilities: Error on send_cmd_to_node")
            return "ERROR"

    def get_next_cmd(self, node_id):
        if len(self.cmdBuffer[node_id]) == 0:
            return None

        else:
            return self.cmdBuffer[node_id].pop()



