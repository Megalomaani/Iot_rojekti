
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


    def nodeTrigger(self, nodeID, actionID, val = 0):

        for evnt in self.events:
            for trig in evnt.get_triggers():
                if (trig[1] == nodeID or trig[1] == 0) and trig[2] == actionID:
                    evnt.trigger(self.server_util, val)

    def serverTrigger(self, code):
        pass

    def updateTriggers(self):
        pass

    def add_event(self, event_id):
        self.events[event_id] = EventObject.EventObject()

    def get_event(self, event_id):
        return self.events[event_id]