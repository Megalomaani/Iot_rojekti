

class EventObject:

    def __init__(self, event_id):

        self.ID = event_id

        # Triggers for the event
        self.triggers = []

        # nodeCMDs to run when event is triggered
        self.nodeCMDsToRun = []

    def trigger(self, s_util, val):
        # Run specified nodeCMDs
        print("Event{} trigged!".format(self.ID))
        for cmd in self.nodeCMDsToRun:
            s_util.send_cmd_to_node(cmd[0], cmd[1])

    def add_node_cmd_to_run(self, node_to_use_id, node_cmd):
        self.nodeCMDsToRun.append((node_to_use_id, node_cmd))

    def add_trigger(self, node_action, node_id=0):
        self.triggers.append((node_id, node_action))

    def get_triggers(self):
        return self.triggers
