


class EventHandler:

    def __init__(self):

        # All programmed events
        self.events = []

        # Map of all known triggers
        self.triggers = {}
        self.triggers["node"] = []
        self.triggers["server"] = []
        self.triggers["timed"] = []


    def nodeTrigger(self, nodeID, actionID, val = 0):
        pass

    def serverTrigger(self, code):
        pass

    def updateTriggers(self):
        pass