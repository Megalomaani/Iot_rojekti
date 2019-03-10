
import EventObject

class EventHandler:

    def __init__(self, s_util):

        self.server_util = s_util

        # All programmed events
        self.events = {}

        # Map of all known triggers
        self.triggers = {}
        self.triggers["node"] = []
        self.triggers["server"] = []
        self.triggers["timed"] = []

    def node_trigger(self, nodeID, actionID, val = 0):
        print("node trigger: ID:{} Action:{}".format(nodeID,actionID))
        for evnt in self.events.values():
            for trig in evnt.get_triggers():
                print("trig: ID:{} Action:{}".format(trig[0],trig[1]))
                if (trig[0] == nodeID or trig[0] == 0) and trig[1] == actionID:
                    evnt.trigger(self.server_util, val)

    def serverTrigger(self, code):
        pass

    def updateTriggers(self):
        pass

    def add_event(self, event_id):
        self.events[event_id] = EventObject.EventObject(event_id)

    def get_event(self, event_id):
        return self.events[event_id]